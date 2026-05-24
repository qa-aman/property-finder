# Discovery Notes

**Date:** 24-05-2026
**Status:** Q1-Q4 researched (findings below). All desk research, pending validation with real test users.

These track the open questions from the PRD. Findings below are desk research with validated sources, not user interviews. Validate with real test users before committing the build.

---

> **City is a variable.** The POC takes the city as a per-search input, so it works for any city (Mumbai, Bangalore, Pune, ...). The data strategy below is the same across Indian metros; three things resolve per city at runtime: the **subreddit** (r/<city>), the **state RERA portal** (MahaRERA for Maharashtra, RERA Karnataka for Bangalore, MahaRERA only covers Maharashtra), and **local hazard zones** (e.g. monsoon flood areas in coastal cities). Mumbai is used below as a worked example, not a hardcoded target.

## Decisions for the POC (summary)

- **Sentiment sources:** Research recommended **Reddit (official API) + Google Maps reviews**. **POC implementation note (24-05-2026):** switched to **Gemini + Google Search grounding** instead, since the Reddit "script" app could not be created and grounded search needs no extra key while staying current and sourced. Same trust principle (grounded, not model-memory), different retrieval. (See Q1.)
- **Commute signal:** Use **Google Routes API** with `TRAFFIC_AWARE_OPTIMAL` + `trafficModel: PESSIMISTIC` + a future peak-hour `departureTime`. Query DRIVE, TWO_WHEELER (auto proxy), and TRANSIT, at 9am and 6pm. Manual Rapido spot-check + monsoon penalty for the final 3-5. (See Q2.)
- **Decision-confidence measurement:** Moderated think-aloud with ~5 users; primary metric is a 7-point confidence Likert, plus per-recommendation "would you visit?" yes/no, plus SEQ. (See Q4.)
- **Society sourcing:** **Google Places API (New)** as primary, the **state RERA portal** (e.g. MahaRERA) scrape for post-2017 projects, OSM for area geometry only. No source gives exhaustive coverage; 100% enumeration is not a POC goal. (See Q3.)

---

## Q1: Neighbourhood sentiment sources

| Source | India coverage | Trustworthiness | Programmatic access | Fake-review risk |
|---|---|---|---|---|
| Google Maps / Place reviews | Very high | Medium (motivated reviews) | Official API, max 5 reviews/place, paid | Medium-high |
| Reddit (r/<city> e.g. r/mumbai, r/bangalore, r/pune; plus r/india) | High for metros | High (pseudonymous, no seller incentive) | Official API, OAuth2, free tier | Low |
| NoBroker locality reviews | Medium | Medium-low (SEO, thin) | No API, scraping ToS-prohibited | High |
| Housing / MagicBricks / 99acres | Medium | Low-medium (editorial/SEO) | No API, 403/406 | High |
| Quora | High for metros | Medium (stale, 2-5 yrs old) | No API | Low-medium |
| Facebook / WhatsApp groups | Very high | Very high (verified residents) | Technically inaccessible | Very low |
| X (Twitter) | Low | Low relevance | API v2 paid ($100/mo) | Low |

**Implementation note (POC):** The POC now sources sentiment via **Gemini with Google Search grounding** (one Gemini call per area that runs a live Google Search and returns a grounded, sourced summary), because the Reddit script-app could not be created and grounding needs no extra credential. The research recommendation below still stands as the more direct grounded source if a Reddit key becomes available.

**Recommendation:** Reddit + Google Maps reviews together. They cover each other's failure modes: Reddit has authentic depth but thin non-metro coverage and no structure; Google Maps has breadth and structure but gameable ratings. Use Google Maps for geographic coverage, Reddit for genuine sentiment. Use Google review **text** sentiment (not the star score) given fake-review prevalence in India. Both have official APIs and no ToS/scraping risk. The relocating IT professional is exactly the Reddit demographic, and the content is recent and searchable today. **Per city:** resolve the subreddit from the brief's city (r/<city>) and fall back to r/india; Reddit coverage is strong for metros and thinner for tier-2/3 cities, so confidence should scale with available signal.

Sources (validated):
- Google Places (Legacy) Details API: https://developers.google.com/maps/documentation/places/web-service/legacy/details
- Google Maps Platform pricing: https://mapsplatform.google.com/pricing
- Reddit API OAuth2: https://github.com/reddit-archive/reddit/wiki/OAuth2
- Reddit Data API Terms: https://www.redditinc.com/policies/data-api-terms

---

## Q2: Better commute-time signal

Why basic Google Maps feels off: comparing areas days/weeks ahead, the naive estimate falls back to near free-flow conditions and understates peak congestion (40-100% on major arterial corridors at 9am; example: Mumbai's Western Express Highway). The fix is to explicitly set a future `departure_time` and a pessimistic traffic model. This holds for any congested metro, not just Mumbai.

| Signal | City road coverage | Peak-hour traffic | Auto proxy | Trains | Future departure | POC cost |
|---|---|---|---|---|---|---|
| Google Routes API (pessimistic + traffic-aware) | Excellent | Best available | TWO_WHEELER (beta) | Yes (TRANSIT) | Yes | Advanced SKU |
| Google Distance Matrix (pessimistic) | Excellent | Yes | driving proxy | Yes | Yes | ~$0.005/element |
| TomTom Routing | Good | Yes | taxi mode | No | Yes | 2,500 free/day |
| HERE Routing | Good | Yes | scooter mode | Weak (separate API) | Yes | Free tier |
| Mappls (MapmyIndia) | Best geometry | Partial (low probe density) | No | No | Partial | Registration |
| Rapido / Ola / Uber ETA | n/a | Live only | Rapido = real autos | n/a | No | No public API |
| Resident/community signal | n/a | Implicit | Yes | Yes | Implicit | Free, manual |

**Recommendation:** Google Routes API as the primary signal: `TRAFFIC_AWARE_OPTIMAL` + `trafficModel: PESSIMISTIC` + future `departureTime` (next Monday 9am and 6pm local time). Run three modes per area-to-office pair: DRIVE (own car), TWO_WHEELER (closest auto-rickshaw proxy, follows service lanes), TRANSIT (local trains/metro/bus; Google's transit coverage is strong across Indian metros). That is 6 data points per candidate. Google's Android GPS probe volume in India is the structural reason it beats TomTom/HERE/Mappls for peak prediction. This works the same for any city; transit quality varies by city's transit data availability.

Two manual layers for the final 3-5 candidates:
- **Rapido spot-check** for real auto ETA ground truth. If Rapido says 55 min where the API says 25, penalize.
- **Local hazard penalty:** no API models seasonal hazards (e.g. monsoon flooding in coastal cities). For areas near the city's known hazard zones, add a buffer (30-60 min in flood cases), cross-referenced with the local civic body's hazard maps. Example: Mumbai monsoon (June-Sept) flood zones such as Hindmata, Sion, Malad, Andheri subway, via MCGM flood-prone maps. Resolve the equivalent zones/source per city.

Sources (validated):
- Routes API traffic model: https://developers.google.com/maps/documentation/routes/traffic-model
- Routes API travel modes: https://developers.google.com/maps/documentation/routes/reference/rest/v2/RouteTravelMode
- Routes API routing preference: https://developers.google.com/maps/documentation/routes/reference/rest/v2/RoutingPreference
- Distance Matrix API: https://developers.google.com/maps/documentation/distance-matrix/distance-matrix
- TomTom Routing: https://developer.tomtom.com/routing-api/documentation/routing/calculate-route
- HERE Routing: https://developer.here.com/documentation/routing-api/dev_guide/index.html
- Mappls API: https://about.mappls.com/api/

---

## Q3: Sourcing named societies per area

The honest gap: no single source gives clean, exhaustive coverage. Indian metros have very large stocks of registered co-operative societies, most predating RERA with no Google Maps presence (Mumbai alone has an estimated 100,000+ statewide). For the POC, target the most relevant subset (new projects + well-known named complexes), and flag in scope that 100% enumeration is not a POC goal.

Per city: the RERA source is the **state portal** for the city's state, not a single national one (MahaRERA for Maharashtra/Mumbai/Pune, RERA Karnataka for Bangalore, and so on). Resolve it from the brief's city.

| Source | City coverage | Locality filter | API access | POC cost | Freshness |
|---|---|---|---|---|---|
| Google Places API (New) | Moderate (better inner suburbs, poor old co-ops) | Bounding box + text | Official REST API | Free at POC scale | Near real-time |
| OpenStreetMap (Overpass) | Poor for named societies | Bounding box | Free, no key | Free | Volunteer-dependent |
| NoBroker / MagicBricks / 99acres / Housing | Excellent for active inventory | By locality | No API; scraping ToS-prohibited | n/a (blocked) | Daily |
| State RERA portal (e.g. MahaRERA) | Good post-2017 projects; no pre-RERA | District + taluka + free-text | No API; HTML scrape | Free (scrape risk) | Live |
| PropEquity / CRE Matrix | Very good, consistent | City + locality | No public API; enterprise contract | INR 5-30L/year | Near real-time |
| Justdial / Sulekha | Partial, inconsistent | Text only | No official API | n/a (blocked) | Stale |

**Recommendation:**
1. **Google Places API (New)** as the primary live lookup. Nearby Search with `includedTypes: ["apartment_complex","housing_complex"]` in a bounding box on the area; fall back to Text Search ("housing society <area> <city>") where typed results are thin. Expect ~50-70% coverage in well-mapped suburbs, lower elsewhere. Free at POC volume (under ~200 calls/month within Google's $200 credit). Watch for duplicate Place IDs and inconsistent type tagging on Indian residential buildings. Works for any city out of the box.
2. **State RERA portal scrape** as the gap-filler for post-2017 projects (project name + promoter + taluka + locality). Resolve the portal from the city's state (e.g. MahaRERA for Mumbai/Pune; ~48,000 projects statewide, no official API or bulk export yet, export page "coming soon" as of 24-05-2026). Each state portal differs, so the scrape adapter is per-state. Gap: pre-2017 co-op societies absent.
3. **OpenStreetMap (Overpass)** only as a free geometry layer for area boundary polygons to center the Places query, not as a society-name source (named coverage too thin in Indian metros).
4. **PropEquity** is the right long-term data partner if the POC gets funded (1.73 lakh+ projects, consistent locality tagging, monthly updates), but enterprise-only, so out of scope for the POC.

Sources (validated 24-05-2026):
- Google Places types: https://developers.google.com/maps/documentation/places/web-service/place-types
- Google Places Nearby Search: https://developers.google.com/maps/documentation/places/web-service/nearby-search
- Google Maps pricing: https://developers.google.com/maps/billing-and-pricing/pricing
- State RERA portal (example, MahaRERA) project search: https://maharera.maharashtra.gov.in/projects-search-result
- Overpass API wiki: https://wiki.openstreetmap.org/wiki/Overpass_API
- OSM India wiki: https://wiki.openstreetmap.org/wiki/India
- PropEquity: https://www.propequity.in/
- Open City Mumbai datasets: https://data.opencity.in/dataset?city=Mumbai

---

## Q4: Measuring decision confidence

No user data yet, so this is a measurement plan grounded in UX-research literature. Key caveat: the "5 users" rule (Nielsen Norman) is for finding problems qualitatively, not for statistically valid metrics. At n=5 treat numbers as directional and pass thresholds as decision rules, not statistical claims (reliable quantitative studies need ~20+ users).

**Recommended battery** (45-min moderated think-aloud, ~5 users, asked after the user reviews their shortlist):

1. **Primary - decision confidence (7-point Likert):** "Based on the shortlist you just saw, how confident do you feel about which areas are worth visiting in person?" (1 = not at all, 7 = very). Follow up: "What would raise your confidence?"
2. **Behavioural intent (yes/no per recommendation):** "Would you actually go visit this place?" Count the yeses.
3. **Secondary - Single Ease Question (7-point):** "How would you rate the difficulty of finding a shortlist of areas to visit?" Flags whether UI friction (not recommendation quality) is suppressing confidence.

**Pass threshold (proceed to next sprint if all met):**
- Confidence median >= 5/7, and
- >= 4 of 5 users say "yes" to at least one recommendation, and
- SEQ median >= 5/7.

Diagnostic: low confidence but high visit-intent = shortlist logic works, UI fails to communicate reasoning. Low visit-intent = recommendation quality is the problem.

Skip SUS (10-item overhead, needs n=10+) and the Decisional Conflict Scale (needs n=30+, built for medical decisions) at POC stage.

Sources (validated):
- NNG, Why You Only Need to Test with 5 Users: https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/
- NNG, Quantitative Studies: How Many Users to Test?: https://www.nngroup.com/articles/quantitative-studies-how-many-users/
- NNG, Thinking Aloud: https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/
- NNG, Measuring Perceived Usability (SUS, NASA-TLX, SEQ): https://www.nngroup.com/articles/measuring-perceived-usability/
- MeasuringU, Single Ease Question: https://measuringu.com/seq10/
- MeasuringU, System Usability Scale: https://measuringu.com/sus/

---

## Product boundaries (unchanged)

- The in-person visit stays mandatory. The tool shortlists; it does not finalize. Aman's own approach: shortlist online, then visit twice (day and evening).
- Rental-only framing (11-month) deliberately avoids long-term "how is the area evolving" uncertainty.

## Reference model

- Europe trip planned end-to-end with an LLM + hostels.com: personality + days + "near city center" produced a usable itinerary. The housing equivalent is the target.
- Zillow (US) provides photos/videos for level-1 rejection before visiting. No trusted India equivalent yet.
