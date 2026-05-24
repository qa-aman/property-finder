# Property Finder - Product Brief

**Date:** 24-05-2026
**Source:** Build Hours session (NextLeap, Applied Generative AI Bootcamp)
**Status:** Problem framing for a POC, pre-discovery

---

## 1. Context

A relocating professional knows one thing about a new city: their office location. Everything else is unknown. Shreya described moving from Bangalore (and earlier Delhi) to Mumbai with no understanding of the city's geography, neighbourhoods, or commute realities.

Existing platforms (NoBroker, Housing, 99acres) list properties. None of them help a person who does not know the city decide *where* to live. The result: the user ends up frustrated, juggling three tools at once (a listing platform, an LLM, and Google Maps) and still cannot make a confident decision.

This brief covers only the Property Finder solution discussed in the session.

---

## 2. Problem Statements

**P1. Listings without context.**
Platforms show available flats but assume the user already knows which area suits them. A newcomer has no basis to filter. Searches return results from "anywhere and everywhere."

**P2. No neighbourhood intelligence for outsiders.**
The user does not know society names, which areas are good to live in, what is residential versus open land, or which societies are old versus newly built. The city feels "alien."

**P3. Commute reality is opaque and untrustworthy.**
Google Maps travel times are inconsistent (4.5 km showing 17-18 minutes; contradictory estimates for different directions). The mode of transport changes feasibility: a 7 km area may be fine by car but impractical by auto, especially during Mumbai monsoon. None of this is surfaced when browsing listings.

**P4. No level-1 rejection filter.**
In the US, Zillow provides photos and videos so users can reject options before visiting. India has no trusted equivalent. Users cannot pre-screen, so every shortlist requires a physical visit.

**P5. Decision paralysis, not option scarcity.**
Platforms show many options but do not *empower a decision*. The user wants the power to narrow down, not a longer list.

---

## 3. What We Want To Do

Build a tool that helps a person who does not understand a city decide where to rent, by translating their constraints into a short, ranked list of areas and societies worth an in-person visit.

Target the rental use case (11-month agreements), not buying. This deliberately sidesteps long-term "how is the area evolving" uncertainty, since the commitment is short.

Core capabilities to explore:
- Take the user's inputs: office location, transport mode (own car / auto / public), budget, lifestyle preferences, and tolerance for traffic.
- Map those to candidate areas and named societies, not just scattered pins.
- Layer in commute feasibility by transport mode and time of day (for example 9-10 AM, 5-6 PM, 7-8 PM), not raw map distance.
- Surface neighbourhood signals: society names in a chosen radius, old versus new, density, and reputation pulled from Google reviews and Reddit.
- Produce a level-1 shortlist the user can then validate in person.

Reference model: the Europe trip planned end-to-end with an LLM plus hostels.com. The user gave personality, number of days, and "live near city center," and received a usable itinerary. We want the housing equivalent: constraints in, confident shortlist out.

---

## 4. Goal

Build a POC that proves we can solve the core problem: helping a person who does not know a city decide where to rent.

Move the user from "I see options but cannot decide" to "I have 5 areas and a handful of societies I trust enough to go visit."

Success for the POC is a confident, narrowed-down shortlist for a city the user does not know, with the in-person visit reserved for final confirmation rather than basic screening.

---

## 5. Open Questions and Risks

**Data availability and trust (India).**
Reliable structured data on Indian societies (build year, infrastructure, real traffic) is thin compared to foreign markets. This is the central challenge for grounding any agent.

**Commute data accuracy.**
Google Maps cannot be trusted at face value. We need a better signal for real travel time by mode and time of day.

**In-person visit stays mandatory.**
The "feel" of an area (mood, aura, evening versus day) cannot be captured online. Aman's own approach when house-hunting in Ahmedabad: shortlist online, then visit twice, once by day and once in the evening. The tool reduces the shortlist, it does not replace the visit.

---

## 6. Scope Note

This is one of two threads from the session. The other is a reusable PM project folder structure (the "OS"). They are separate; this brief is the product problem, not the build setup.
