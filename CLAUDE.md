# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A POC that helps a person who does not know a city decide where to rent. It takes
what the user knows (office location, transport mode, budget, preferences) and
returns a ranked shortlist of areas and named societies worth an in-person visit.
Read `docs/property-finder-brief.md` for the problem and goal before changing behavior.

Scope guardrails for this POC:
- Rental-only (11-month agreements). Do not build for buying or long-term area-evolution forecasting.
- City-agnostic. The city is a per-search input (`UserBrief.city`), so the same flow works for any city (Mumbai, Bangalore, Pune, ...). Do not hardcode a city. City-specific data resolves at runtime: the subreddit (r/<city>), the state RERA portal (MahaRERA for Maharashtra, RERA Karnataka for Bangalore, etc.), and local hazard zones (e.g. monsoon flood areas). `DEFAULT_CITY` is only an optional demo fallback, not a constraint.
- The output is a shortlist to validate in person, never a final decision (human-in-the-loop boundary).
- No revenue/monetization features.

## Commands

```bash
pip install -e ".[dev]"          # install (editable) with dev deps
cp .env.example .env             # fill GEMINI_API_KEY, GOOGLE_MAPS_API_KEY (or set USE_STUB_ADAPTERS=true)
uvicorn property_finder.main:app --reload   # run the API (http://127.0.0.1:8000/health)
pytest                           # run tests
pytest tests/test_health.py::test_health_reports_default_city   # single test
ruff check .                     # lint
```

Config is validated at startup (`config.py` / `load_settings`). A missing or bad
env var crashes immediately by design (fail-fast) - do not add defensive fallbacks.

## Architecture

Clean Architecture, dependencies point inward. Outer layers implement inner-layer
ports. The multi-agent flow is the core of the POC.

- `domain/models.py` - entities (`UserBrief`, `AreaRecommendation`, `Shortlist`) and ports (`MapsProvider`, `ReviewsProvider`). No framework or vendor imports here.
- `agents/` - the reasoning units. `orchestrator.py` runs the flow: `area_agent` (candidate areas + societies) -> `commute_agent` (feasibility by mode and time of day) -> `sentiment_agent` (neighbourhood signal) -> rank into a shortlist. Each agent maps to a problem statement in the brief.
- `tools/` - thin agent-callable tool wrappers.
- `infrastructure/` - concrete adapters implementing domain ports (`google_maps.py`, `reviews.py`).
- `application/container.py` - composition root. The only place infrastructure is bound to agents. Wire new dependencies here, not inside agents.
- `main.py` - FastAPI presentation layer.

The agent stubs raise `NotImplementedError`. Implementing them is the POC work;
keep each agent's responsibility aligned with its problem statement.

Key design intents baked into the structure:
- Google Maps times are treated as approximate. `commute_agent` adds mode and
  time-of-day judgement rather than trusting raw map estimates.
- Source trust (reviews, listings) is unresolved - see `docs/discovery-notes.md`.

## Docs (PM layer)

`docs/` holds the product thinking, separate from runnable code:
`property-finder-brief.md` (problem + goal), `personas.md`, `success-metrics.md`,
`discovery-notes.md` (open questions), `prd.md` (placeholder until discovery firms up).
Update these when product scope or assumptions change.
