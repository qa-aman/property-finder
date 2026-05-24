# PRD: Property Finder POC

**Appetite:** Big batch (4-6 weeks)
**Status:** Draft
**Author:** Aman Parmar
**Date:** 24-05-2026

## Problem

A person relocating to a city they do not know can only anchor on one fact: their office location. They do not know society names, which areas are good to live in, what the commute is really like by their mode of transport, or how an area feels. Existing platforms (NoBroker, Housing, 99acres) list properties but assume the user already knows where they want to live, so searches return options from anywhere and everywhere. The user ends up juggling a listing platform, an LLM, Google Maps, and Reddit at once, and still cannot decide. The cost: relocation decisions made blind, or abandoned out of frustration, with every shortlisted option requiring a physical visit because nothing supports pre-screening.

## Solution

A tool that takes what the user knows and returns a ranked shortlist of areas and named societies worth visiting in person.

Broad strokes (fat marker sketch):

- The user submits a brief: office location, transport mode (own car / auto / public), monthly budget, and free-text preferences.
- The system proposes candidate areas and the named societies inside them for the target city.
- For each candidate, it estimates commute feasibility by the user's transport mode and time of day (morning peak, evening peak), and flags where a mode makes an otherwise close area impractical.
- For each candidate, it summarizes neighbourhood sentiment from public signal.
- It ranks and returns the top areas as a shortlist, each with societies, commute estimate, sentiment summary, and a short "why recommended" with a confidence score.

The output is a level-1 filter: enough for the user to confidently choose what to visit. The in-person visit (day and evening) remains the user's job, not the tool's.

City is an input to every search (`UserBrief.city`), not a fixed target. The POC is built city-agnostic so the same flow serves any city (Mumbai, Bangalore, Pune, and so on). City-specific data resolves at runtime: the city's subreddit, the relevant state RERA portal, and local hazard zones. For validation, exercise it against at least two different cities (e.g. Mumbai and Bangalore) rather than tuning to one.

## Rabbit Holes

- **Do not treat Google Maps times as ground truth.** They are inconsistent. The commute agent layers mode and time-of-day judgement on top; treat map output as one approximate input.
- **Do not build a data pipeline or scraping infrastructure.** Use direct API/source calls for the POC. Source-trust evaluation is discovery work, not build work.
- **Do not over-model the domain.** Keep entities to what the shortlist needs (brief, area recommendation, commute estimate, shortlist). No property-level inventory modeling.
- **Do not build accounts, auth, or persistence.** A single request-to-shortlist flow is enough to prove the problem.
- **Do not hardcode any city.** Keep the city a runtime input and resolve city-specific sources (subreddit, state RERA portal, hazard zones) from it. Do not bake one city's place names, corridors, or flood zones into prompts or logic.

## No-Gos

- No buying use case. Rental only (11-month framing).
- No long-term area-evolution forecasting.
- No revenue model or monetization features.
- No city-specific tuning that breaks other cities. The POC is city-agnostic by design, but we do not promise verified data quality for every Indian city in v1 (coverage varies by city). Start by validating a couple of cities.
- No replacement of the in-person visit. The tool shortlists; it never finalizes.
- No UI polish beyond what is needed to demo the shortlist (API-first is acceptable for the POC).
- No user-account, saved-search, or notification features.

## Open Questions

Desk-research answers for the resolved items are in `discovery-notes.md`. They still need validation with real test users before the build commits to them.

```
Q: Which neighbourhood-sentiment sources are trustworthy enough to ground recommendations (map reviews, Reddit, listings)?
Owner: Aman Parmar
Status: RESOLVED (desk research) - Reddit API + Google Maps Place reviews. See discovery-notes.md Q1.

Q: What is the better signal for real commute time by mode and time of day, given Google Maps is unreliable?
Owner: Aman Parmar
Status: RESOLVED (desk research) - Google Routes API, TRAFFIC_AWARE_OPTIMAL + PESSIMISTIC + future departureTime, modes DRIVE/TWO_WHEELER/TRANSIT, plus manual Rapido + monsoon layers. See discovery-notes.md Q2.

Q: How do we source named societies per candidate area for the target city (which API/source, and is coverage good enough)?
Owner: Aman Parmar
Status: RESOLVED (desk research) - Google Places API (New) primary, MahaRERA scrape for post-2017 projects, OSM for area geometry. No source is exhaustive; 100% enumeration is not a POC goal. See discovery-notes.md Q3.

Q: How is "decision confidence" measured with a real test user to validate the POC?
Owner: Aman Parmar
Status: RESOLVED (measurement plan) - moderated think-aloud, n~5: confidence Likert + per-recommendation visit intent + SEQ, with a pass threshold. See discovery-notes.md Q4.
```
