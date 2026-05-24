"""Run a shortlist for a brief and append the result to docs/runs/shortlist-runs.md.

Lets you re-run with different inputs and compare rounds in one file.

Examples:
  PYTHONPATH=src python scripts/run_shortlist.py --label "Shreya round 1"
  PYTHONPATH=src python scripts/run_shortlist.py --city Pune --office "Hinjewadi" --mode public --commute-target 45

Use --skip-sentiment to avoid the grounded-search Gemini calls (useful on the
free-tier daily quota); the run then uses a single Gemini call for area proposal.
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime
from urllib.parse import quote_plus

from property_finder.agents.area_agent import AreaAgent
from property_finder.agents.commute_agent import CommuteAgent
from property_finder.agents.orchestrator import Orchestrator
from property_finder.agents.sentiment_agent import SentimentAgent
from property_finder.application.container import build_orchestrator
from property_finder.config import load_settings
from property_finder.domain.models import Shortlist, TransportMode, UserBrief

_RUNS_FILE = "docs/runs/shortlist-runs.md"

# Shreya's brief is the default so a bare run reproduces her case.
_DEFAULT_OFFICE = (
    "12th Floor, Lotus Corporate Park, F Wing, off Western Express Highway, "
    "Geetanjali Railway Colony, Laxmi Nagar, Goregaon East, Mumbai, Maharashtra 400060"
)


class _NoSentiment:
    """Returns no text so the SentimentAgent reports its 'no data' message
    without making any LLM call. Used with --skip-sentiment."""

    def neighbourhood_sentiment(self, area: str, city: str) -> str:
        return ""


def _build(settings, skip_sentiment: bool, area_model: str) -> Orchestrator:
    if not skip_sentiment:
        return build_orchestrator(settings)
    # Manual wiring: real area + societies + commute, sentiment off.
    from property_finder.infrastructure.gemini_llm import GeminiLLMAdapter
    from property_finder.infrastructure.google_maps import GoogleMapsProvider
    from property_finder.infrastructure.places import GooglePlacesAdapter

    area_llm = GeminiLLMAdapter(settings.gemini_api_key, model=area_model)
    return Orchestrator(
        AreaAgent(area_llm, GooglePlacesAdapter(settings.google_maps_api_key)),
        CommuteAgent(GoogleMapsProvider(settings.google_maps_api_key)),
        SentimentAgent(_NoSentiment(), area_llm),
    )


def _run_with_retry(orch: Orchestrator, brief: UserBrief, top_n: int) -> Shortlist:
    last: Exception | None = None
    for attempt in range(3):
        try:
            return orch.run(brief, top_n=top_n)
        except Exception as e:  # noqa: BLE001 - surface to caller after retries
            last = e
            print(f"attempt {attempt + 1} failed: {type(e).__name__}; retrying in 8s")
            time.sleep(8)
    raise SystemExit(f"run failed after retries: {last}")


def _maps_dir_link(area: str, city: str, office: str) -> str:
    """Google Maps directions URL (official Maps URLs format): origin = the area,
    destination = the office. Clicking opens Google Maps with both points set."""
    origin = quote_plus(f"{area}, {city}")
    dest = quote_plus(office)
    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}"


def _format(
    brief: UserBrief, sl: Shortlist, label: str, target: int,
    skip_sentiment: bool, prompt: str,
) -> str:
    stamp = datetime.now().strftime("%d-%m-%Y %H:%M")
    lines = [
        f"## {label} ({stamp})",
        "",
        "### Prompt",
        "",
        "```",
        prompt.strip() or "(no verbatim prompt provided)",
        "```",
        "",
        "### Parsed brief",
        "",
        f"- City: {brief.city} | Mode: {brief.transport_mode.value} | "
        f"Budget: {brief.monthly_budget_inr} | Commute target: <= {target} min both peaks",
        f"- Office: {brief.office_location}",
        f"- Preferences: {', '.join(brief.preferences) or 'none'}",
    ]
    if skip_sentiment:
        lines.append("- NOTE: sentiment deferred (grounded-search calls skipped to fit quota)")
    lines += ["", "### Output", "",
              "| Area | Morning | Evening | Meets target | Monsoon | Confidence | "
              "Verify on Maps | Societies |",
              "|---|---|---|---|---|---|---|---|"]
    for r in sl.recommendations:
        if r.commute.reliable:
            m, e = f"~{r.commute.minutes_morning_peak}m", f"~{r.commute.minutes_evening_peak}m"
            meets = ("yes" if r.commute.minutes_morning_peak <= target
                     and r.commute.minutes_evening_peak <= target else "no")
        else:
            m = e = "unreliable"
            meets = "n/a"
        monsoon = "flag" if r.monsoon_note else "-"
        link = _maps_dir_link(r.area_name, brief.city, brief.office_location)
        socs = ", ".join(r.society_names[:5]) or "(none found)"
        lines.append(
            f"| {r.area_name} | {m} | {e} | {meets} | {monsoon} | {r.confidence} | "
            f"[Open in Maps]({link}) | {socs} |"
        )

    lines += ["", "### Candidate listings (UNVERIFIED - grounded best-effort; confirm on the "
              "listing and at visit)", ""]
    any_listing = False
    for r in sl.recommendations:
        if not r.listings:
            continue
        any_listing = True
        lines.append(f"**{r.area_name}**")
        for lst in r.listings:
            rent = f"INR {lst.rent_inr}" if lst.rent_inr is not None else "rent ?"
            sqft = f"{lst.sqft} sqft" if lst.sqft is not None else "sqft ?"
            park = ("parking yes" if lst.car_parking is True
                    else "parking no" if lst.car_parking is False else "parking ?")
            url = f" - [link]({lst.source_url})" if lst.source_url else ""
            lines.append(
                f"- {lst.title}: {lst.bhk or 'BHK ?'}, {sqft}, {rent}, "
                f"{lst.furnishing or 'furnishing ?'}, {park}{url}"
            )
        lines.append("")
    if not any_listing:
        lines += ["(No matching candidate listings returned for the given criteria.)", ""]

    lines += ["Sentiment / notes:"]
    for r in sl.recommendations:
        note = r.sentiment_summary[:220]
        if r.monsoon_note:
            note += f"  _[{r.monsoon_note}]_"
        lines.append(f"- **{r.area_name}**: {note}")
    lines += ["", "Listing attributes (size, parking, BHK, furnishing, rent) are best-effort and "
              "UNVERIFIED - confirm on the listing page and at visit.",
              "", "---", ""]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--label", default="Run")
    p.add_argument("--city", default="Mumbai")
    p.add_argument("--office", default=_DEFAULT_OFFICE)
    p.add_argument("--mode", default="own_car", choices=[m.value for m in TransportMode])
    p.add_argument("--budget", type=int, default=80000)
    p.add_argument("--commute-target", type=int, default=30)
    p.add_argument("--top-n", type=int, default=12)
    p.add_argument("--preferences", default=(
        "four-wheeler parking,apartments at least 500 sq ft,"
        "commute under 30 min both peaks,monsoon/flooding aware"))
    p.add_argument("--skip-sentiment", action="store_true")
    p.add_argument("--area-model", default="gemini-2.5-flash",
                   help="Model for area proposal (e.g. gemini-2.5-flash-lite to use a separate quota).")
    p.add_argument("--prompt", default="",
                   help="Verbatim user prompt to record in the runs file alongside the output.")
    p.add_argument("--prompt-file", default="",
                   help="Path to a file whose contents are used as the verbatim prompt.")
    p.add_argument("--bhk", default=None, help='e.g. "1 BHK"')
    p.add_argument("--min-sqft", type=int, default=None)
    p.add_argument("--parking", action="store_true", help="require four-wheeler parking")
    p.add_argument("--furnishing", default=None, help='e.g. "semi-furnished"')
    args = p.parse_args()

    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as pf:
            prompt = pf.read()

    brief = UserBrief(
        city=args.city,
        office_location=args.office,
        transport_mode=TransportMode(args.mode),
        monthly_budget_inr=args.budget,
        preferences=[s.strip() for s in args.preferences.split(",") if s.strip()],
        bhk=args.bhk,
        min_sqft=args.min_sqft,
        needs_car_parking=args.parking,
        furnishing=args.furnishing,
    )
    orch = _build(load_settings(), args.skip_sentiment, args.area_model)
    sl = _run_with_retry(orch, brief, args.top_n)

    block = _format(brief, sl, args.label, args.commute_target, args.skip_sentiment, prompt)
    with open(_RUNS_FILE, "a", encoding="utf-8") as f:
        f.write(block)
    print(block)
    print(f"Appended to {_RUNS_FILE}")


if __name__ == "__main__":
    main()
