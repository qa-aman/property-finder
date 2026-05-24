# Property Finder POC

Helps someone relocating to a city they do not know decide where to rent. It takes
what the user knows (city, office location, transport mode, budget, and apartment
criteria) and returns a ranked shortlist of localities, named societies, and
candidate listings worth an in-person visit.

City is a per-search input, so the same flow works for any city. The output is a
level-1 filter to validate in person, never a final decision (human-in-the-loop).

## What it does

For a brief, the multi-agent flow:

1. proposes 5-7 candidate localities near the office (Gemini)
2. names societies in each (Google Places)
3. estimates peak commute by mode, morning and evening (Google Routes API, pessimistic traffic)
4. summarizes grounded resident sentiment (Gemini + Google Search grounding)
5. flags monsoon flood-prone areas and applies a confidence penalty
6. finds candidate flats matching rent / BHK / size / parking / furnishing (grounded, best-effort)
7. ranks into a shortlist with a confidence score and a Google Maps link to verify each commute

## Architecture

Clean Architecture, dependencies point inward. Outer layers implement inner-layer ports.

- `domain/models.py` - entities (`UserBrief`, `AreaRecommendation`, `Listing`, `Shortlist`) and ports (`MapsProvider`, `ReviewsProvider`, `SocietiesProvider`, `ListingsProvider`, `HazardProvider`, `LLMPort`). No framework or vendor imports.
- `agents/` - reasoning units. `orchestrator.py` runs area -> commute -> sentiment -> listings -> rank. Each agent maps to a problem in `docs/`.
- `infrastructure/` - concrete adapters: `gemini_llm.py`, `gemini_reviews.py`, `gemini_listings.py`, `google_maps.py` (Routes), `places.py`, `hazards.py`, and `stubs.py` (keyless fakes).
- `application/container.py` - composition root and the only place adapters are chosen (stub vs real) and wired. Fail-fast on missing keys.
- `main.py` - FastAPI presentation layer (`/health`, `POST /shortlist`).

## Setup

```bash
pip install -e ".[dev]"          # install with dev deps (Python 3.11+)
cp .env.example .env             # fill keys, or set USE_STUB_ADAPTERS=true
```

Real mode needs:
- `GEMINI_API_KEY` - Google AI Studio key (area proposal, grounded sentiment, grounded listings)
- `GOOGLE_MAPS_API_KEY` - one key with Routes API, Places API (New), and Geocoding API enabled

No Reddit or other key is required; sentiment uses Gemini + Google Search grounding.

## Run

```bash
# API
uvicorn property_finder.main:app --reload        # http://127.0.0.1:8000/health
# keyless demo (in-memory fakes, no external calls)
USE_STUB_ADAPTERS=true uvicorn property_finder.main:app --reload
```

`POST /shortlist` body:

```json
{
  "city": "Mumbai",
  "office_location": "Goregaon East, Mumbai",
  "transport_mode": "own_car",
  "monthly_budget_inr": 50000,
  "bhk": "1 BHK",
  "min_sqft": 500,
  "needs_car_parking": true,
  "furnishing": "semi-furnished",
  "preferences": ["near metro"]
}
```

## Comparing rounds

`scripts/run_shortlist.py` runs a brief and appends a timestamped block (prompt +
parsed brief + output + per-row Google Maps verify links + candidate listings) to
`docs/runs/shortlist-runs.md`, so rounds stack for comparison.

```bash
PYTHONPATH=src python scripts/run_shortlist.py \
  --label "round 1" --city Mumbai --office "Goregaon East, Mumbai" \
  --budget 50000 --bhk "1 BHK" --min-sqft 500 --parking --furnishing "semi-furnished"
```

Useful flags: `--commute-target`, `--skip-sentiment` (1 Gemini call, frugal),
`--prompt-file` (record the verbatim prompt), `--mode`, `--top-n`.

## Tests and lint

```bash
pytest                           # business logic and wiring; external calls mocked/stubbed
pytest tests/test_health.py::test_health_reports_default_city   # single test
ruff check .
```

## Known limitations

- Listing attributes (rent, BHK, size, parking, furnishing) are grounded best-effort and `verified=False`. Indian portals have no official API and prohibit scraping, so confirm on the listing page and at visit.
- Commute times are Google Routes estimates (treated as approximate); each row has a Maps link to verify the live time.
- Monsoon flood zones use a static per-city heuristic list, not live civic flood maps.
- Society coverage from Places is not exhaustive.

See `docs/` for the product thinking: `property-finder-brief.md`, `prd.md`,
`personas.md`, `success-metrics.md`, `discovery-notes.md`, `user-stories.md`.
