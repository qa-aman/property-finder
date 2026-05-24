"""Google Maps adapter. Implements MapsProvider via the Routes API.

Note: map travel times are treated as approximate. The commute_agent layers
mode and time-of-day judgement on top rather than trusting raw estimates.

R1 queries DRIVE only, at the next Monday 9am and 6pm (local IST) with a
pessimistic traffic model so the estimate reflects a bad-but-typical peak day,
not free-flow. Multi-mode (TWO_WHEELER, TRANSIT) is R2.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

from property_finder.domain.models import CommuteEstimate, TransportMode

_ENDPOINT = "https://routes.googleapis.com/directions/v2:computeRoutes"
_FIELD_MASK = "routes.duration,routes.distanceMeters"
_IST = timezone(timedelta(hours=5, minutes=30))


def _next_monday_utc(hour_ist: int) -> str:
    """ISO 8601 timestamp for the next Monday at hour_ist IST, always in the future."""
    now = datetime.now(_IST)
    days_ahead = (0 - now.weekday()) % 7  # Monday is weekday 0
    candidate = (now + timedelta(days=days_ahead)).replace(
        hour=hour_ist, minute=0, second=0, microsecond=0
    )
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class GoogleMapsProvider:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def commute_estimate(self, origin: str, area: str, mode: TransportMode) -> CommuteEstimate:
        morning = self._duration_minutes(origin, area, _next_monday_utc(9))
        evening = self._duration_minutes(origin, area, _next_monday_utc(18))
        return CommuteEstimate(
            minutes_morning_peak=morning,
            minutes_evening_peak=evening,
            feasible_for_mode=True,  # the CommuteAgent decides real feasibility
            notes="",
        )

    def _duration_minutes(self, origin: str, area: str, departure_time: str) -> int:
        body = {
            "origin": {"address": origin},
            "destination": {"address": area},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
            "departureTime": departure_time,
            "trafficModel": "PESSIMISTIC",
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": _FIELD_MASK,
        }
        resp = httpx.post(_ENDPOINT, json=body, headers=headers, timeout=15.0)
        resp.raise_for_status()
        routes = resp.json().get("routes") or []
        if not routes:
            raise RuntimeError(f"Routes API returned no route for {origin} -> {area}")
        seconds = int(str(routes[0]["duration"]).rstrip("s"))
        return round(seconds / 60)
