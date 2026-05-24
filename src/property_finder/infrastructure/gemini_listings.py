"""Best-effort listings source via Gemini + Google Search grounding.

Implements ListingsProvider. Indian listing portals have no official API and
prohibit scraping (see docs/discovery-notes.md Q3), so this asks Gemini to search
the open web for currently advertised flats matching the brief and return them as
structured candidates. Results are UNVERIFIED: exact rent/size/parking/furnishing
from search snippets are often stale or wrong, so every Listing has verified=False
and must be confirmed on the listing page and at visit.
"""
from __future__ import annotations

import json
import re

from google import genai
from google.genai import types

from property_finder.domain.models import Listing, UserBrief

_PROMPT = (
    "Search the web for currently advertised flats FOR RENT in {area}, {city} that match "
    "these requirements: {criteria}. Return ONLY a JSON array (max 6) of objects with keys: "
    'title, rent_inr (integer INR/month), bhk, sqft (integer), car_parking (true/false), '
    "furnishing, source_url. Use null for any value you cannot find. Do not invent specifics; "
    "prefer real advertised listings."
)


class GeminiGroundedListings:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def find_listings(self, area: str, brief: UserBrief) -> list[Listing]:
        prompt = _PROMPT.format(area=area, city=brief.city, criteria=_criteria(brief))
        try:
            resp = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
        except Exception:
            return []
        return _parse(resp.text or "")


def _criteria(brief: UserBrief) -> str:
    parts = [f"budget up to INR {brief.monthly_budget_inr}/month"]
    if brief.bhk:
        parts.append(brief.bhk)
    if brief.min_sqft:
        parts.append(f"at least {brief.min_sqft} sq ft")
    if brief.needs_car_parking:
        parts.append("four-wheeler parking")
    if brief.furnishing:
        parts.append(brief.furnishing)
    return ", ".join(parts)


def _parse(text: str) -> list[Listing]:
    text = text.strip()
    # Strip a ```json ... ``` fence if present.
    fence = re.search(r"\[.*\]", text, re.DOTALL)
    if fence:
        text = fence.group(0)
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(rows, list):
        return []
    listings: list[Listing] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "Listing")
        # The model often leaves bhk null even when the title says "1 BHK"; recover it.
        bhk = _as_str(row.get("bhk")) or _bhk_from_title(title)
        listings.append(
            Listing(
                title=title,
                rent_inr=_as_int(row.get("rent_inr")),
                bhk=bhk,
                sqft=_as_int(row.get("sqft")),
                car_parking=row.get("car_parking") if isinstance(row.get("car_parking"), bool) else None,
                furnishing=_as_str(row.get("furnishing")),
                source_url=_as_str(row.get("source_url")),
                verified=False,
            )
        )
    return listings


def _bhk_from_title(title: str) -> str | None:
    """Pull a configuration like '1 BHK', '2.5 BHK', or '1 RK' out of a title."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*(BHK|RK)", title, re.IGNORECASE)
    if not m:
        return None
    return f"{m.group(1)} {m.group(2).upper()}"


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        digits = re.sub(r"[^0-9]", "", value)
        return int(digits) if digits else None
    return None


def _as_str(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
