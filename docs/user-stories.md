# User Stories: Property Finder POC

**Date:** 24-05-2026
**Method:** User Story Mapping (Jeff Patton)
**Source of truth:** `prd.md`, `discovery-notes.md`

Primary user: **the relocating renter** (the outsider who only knows their office). Secondary: **the POC evaluator** (us, validating the concept with test users).

---

## Narrative spine (backbone)

The renter's journey, end to end:

`Enter brief -> Discover areas & societies -> Assess commute -> Assess neighbourhood sentiment -> Review ranked shortlist -> Decide what to visit`

Each backbone step maps to a layer in the code: brief intake (presentation), area_agent, commute_agent, sentiment_agent, orchestrator (rank), output.

---

## Walking skeleton

The thinnest slice that completes the whole journey for whichever city the user enters (e.g. Mumbai or Bangalore):

Submit a brief by API -> get 3-5 areas each with a few named societies (Google Places) -> a single drive-time commute estimate per area -> a one-line sentiment blurb -> a ranked list returned as JSON.

It will be rough (one transport mode, no peak windows, no confidence score), but it proves the flow runs end to end. Everything past Release 1 is enhancement.

---

## Stories by backbone step

### Step 1 - Enter brief

**S1.1 Submit a search brief**
As a relocating renter, I want to enter the city, my office location, transport mode, budget, and preferences, so that the tool can search the city I am moving to on the inputs I actually know.
```
Given I am on the brief intake (API endpoint or form)
When I submit city, office location, transport mode, monthly budget, and free-text preferences
Then the brief is validated and accepted
And the city drives which city-specific sources are used (subreddit, state RERA portal, hazard zones)
And missing or invalid fields (e.g. blank city, blank office, negative budget) are rejected with a clear reason
And an unrecognised transport mode is rejected
```
Release: R1. Depends on: none.

---

### Step 2 - Discover areas & societies

**S2.1 Get candidate areas for my office**
As a relocating renter, I want a shortlist of candidate areas near my office, so that I have somewhere to start in a city I do not know.
```
Given a validated brief with a city and an office location in that city
When the area_agent runs
Then it returns 3-5 candidate area names plausibly commutable to the office
And areas clearly outside any reasonable commute are excluded
And if no areas can be derived, the response says so rather than returning empty
```
Release: R1. Depends on: S1.1.

**S2.2 See named societies in each area**
As a relocating renter, I want named societies inside each candidate area, so that an area becomes concrete places I can look at.
```
Given a candidate area
When the area_agent queries the society source (Google Places New, includedTypes apartment_complex/housing_complex)
Then it returns named societies with an address/coordinate for that area
And it falls back to Text Search where typed results are thin
And duplicate societies (same place under multiple IDs) are de-duplicated
And the response notes that coverage is not exhaustive
```
Release: R1 (basic Places), de-dup in R2. Depends on: S2.1.

**S2.3 Fill gaps with newer projects**
As a relocating renter, I want recently built projects included, so that new societies that lack a Maps presence still show up.
```
Given a candidate area in the brief's city
When the society list is assembled
Then post-2017 projects from the city's state RERA portal (e.g. MahaRERA) for that locality are merged in
And RERA results are de-duplicated against the Places results
And the source of each society (Places / RERA portal) is retained
```
Release: R2. Depends on: S2.2.

---

### Step 3 - Assess commute

**S3.1 See commute time for my mode**
As a relocating renter, I want the commute time from each area to my office for my transport mode, so that I can rule out areas that are impractical to reach.
```
Given a candidate area and the brief's transport mode
When the commute_agent runs
Then it returns an estimated commute time from the area to the office
And the estimate uses a future peak departure time, not free-flow
And map estimates are treated as approximate, not exact
```
Release: R1 (drive only, single window), full modes in R2. Depends on: S2.1.

**S3.2 See realistic peak-hour estimates by mode and time**
As a relocating renter, I want commute estimates for car, auto, and train at morning and evening peak, so that I understand the real daily commute, not a best-case number.
```
Given a candidate area and office
When the commute_agent queries the Routes API
Then it returns estimates for DRIVE, TWO_WHEELER (auto proxy), and TRANSIT
And each is computed with trafficModel PESSIMISTIC and a future departureTime
And both a morning (~9am) and evening (~6pm) peak window are returned
And it flags where a mode makes an otherwise-close area impractical
```
Release: R2. Depends on: S3.1.

**S3.3 Flag commute caveats**
As a relocating renter, I want to be warned about hazard-prone and API-underestimated commutes, so that I am not misled by an optimistic number.
```
Given a candidate area with a computed commute
When the area is within a known hazard zone for the city (e.g. a monsoon flood-prone zone in a coastal city)
Then a hazard caveat (e.g. a monsoon Jun-Sep buffer) is attached to the commute
And the hazard zones/source are resolved per city, not hardcoded to one city
And for the final 3-5 areas, a manual Rapido auto-ETA spot-check can be recorded to catch underestimates
```
Release: R3. Depends on: S3.2.

---

### Step 4 - Assess neighbourhood sentiment

**S4.1 See what residents say about an area**
As a relocating renter, I want a short summary of resident sentiment for each area, so that I get the lived-experience view, not just listings.
```
Given a candidate area
When the sentiment_agent runs
Then it returns a short sentiment summary for the area
And the summary draws on real resident signal, not marketing copy
And if there is too little signal to summarise, it says so rather than inventing one
```
Release: R1 (single source), multi-source in R2. Depends on: S2.1.

**S4.2 Ground sentiment in trustworthy sources**
As a relocating renter, I want sentiment built from Reddit and Google Maps review text, so that I can trust it over incentivised platform ratings.
```
Given a candidate area
When the sentiment_agent gathers signal
Then it pulls grounded resident sentiment via Gemini + Google Search grounding (live web results with citations)
And it relies on review text sentiment, not the numeric star score
And listing-platform ratings are not used as a sentiment source
And the sources behind each summary are retained
```
Release: R2. Depends on: S4.1.

---

### Step 5 - Review ranked shortlist

**S5.1 Get a ranked shortlist**
As a relocating renter, I want the areas ranked into a shortlist, so that I know where to focus first.
```
Given commute and sentiment results for the candidate areas
When the orchestrator runs
Then it returns the top areas ranked, each with its societies, commute estimate, and sentiment summary
And the ranking reflects commute feasibility and sentiment, not an arbitrary order
And the result is returned in a consistent, machine-readable shape
```
Release: R1. Depends on: S2.2, S3.1, S4.1.

**S5.2 Understand why an area is recommended**
As a relocating renter, I want a short "why" and a confidence score per area, so that I can judge how much to trust each recommendation.
```
Given a ranked shortlist
When I view an area
Then it shows a one-line "why recommended"
And a confidence score (0-1) reflecting data coverage and signal strength
And low-confidence areas are clearly marked
```
Release: R2. Depends on: S5.1.

**S5.3 View the shortlist in a usable interface**
As a relocating renter, I want to see the shortlist in a simple UI, so that I can read it without parsing JSON.
```
Given a generated shortlist
When I open the result view
Then each area shows its societies, commute by mode/time, sentiment, why, and confidence
And the view is readable enough to support a decision (API-first is acceptable for R1)
```
Release: R2. Depends on: S5.1.

---

### Step 6 - Decide what to visit

**S6.1 Decide which areas to visit**
As a relocating renter, I want the shortlist to make me confident about which areas to visit in person, so that I can plan visits instead of staying stuck.
```
Given a ranked shortlist with why and confidence
When I review it
Then I can identify which areas I would actually visit
And the tool reminds me the in-person visit (day and evening) is the final step, not the tool's job
```
Release: R2. Depends on: S5.2.

**S6.2 Measure decision confidence (evaluator)**
As a POC evaluator, I want to capture each test user's decision confidence, so that we can decide whether the POC works before building further.
```
Given a test user has reviewed their shortlist
When I run the measurement battery
Then I record a 7-point confidence Likert, per-recommendation "would you visit?" yes/no, and an SEQ score
And results are stored per session for the n~5 cohort
And the pass threshold (confidence median >= 5/7, >= 4 of 5 say yes to at least one rec, SEQ median >= 5/7) is evaluated
```
Release: R3. Depends on: S6.1. Note: this is product-validation instrumentation, not renter-facing.

---

## Release slices (horizontal)

**Release 1 - Walking skeleton (flow runs end to end)**
S1.1, S2.1, S2.2 (basic Places), S3.1 (drive only, single window), S4.1 (single source), S5.1. Output as JSON. Proves: brief in, ranked shortlist out, for any city the user enters.

**Release 2 - Make it trustworthy and readable**
S2.2 de-dup, S2.3 (MahaRERA), S3.2 (multi-mode peak), S4.1 multi-source, S4.2, S5.2 (why + confidence), S5.3 (UI), S6.1. Proves: the shortlist is realistic, grounded, and decision-ready.

**Release 3 - Edge cases and validation**
S3.3 (monsoon + Rapido), S6.2 (decision-confidence measurement). Proves: caveats are handled and the POC is validated with real users.

---

## Dependency notes

- S1.1 gates everything.
- S2.1 (areas) gates S2.2, S3.x, S4.x. You cannot assess commute or sentiment without candidate areas.
- S5.1 (orchestrator) depends on at least one of each: societies (S2.2), commute (S3.1), sentiment (S4.1).
- S6.2 (measurement) needs a decision-ready shortlist (S6.1) and therefore comes last.
- External-data risk to watch: Google Places coverage gaps (S2.2) and state RERA portals having no API and differing per state (S2.3) are the likeliest schedule risks. Coverage also varies by city, so confidence should scale with available data. See `discovery-notes.md` Q3.
