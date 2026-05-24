"""Seasonal-hazard adapter. Implements HazardProvider.

POC heuristic: a static, per-city list of localities with chronic monsoon
waterlogging/flooding. Real implementation would use the city's civic-body flood
maps (e.g. MCGM for Mumbai, see docs/discovery-notes.md Q2). City is matched from
the brief, so adding a city is just adding a list. Unknown cities return "".
"""
from __future__ import annotations

# Lowercased keywords matched as substrings against the area name.
_FLOOD_PRONE: dict[str, set[str]] = {
    "mumbai": {
        "hindmata", "dadar", "parel", "sion", "kurla", "chunabhatti", "wadala",
        "king's circle", "kings circle", "matunga", "andheri", "milan", "santacruz",
        "khar", "malad", "kandivali", "dahisar", "bhandup", "chembur", "ghatkopar",
        "vidyavihar", "byculla", "nehru nagar", "gandhi market",
    },
}

_NOTE = (
    "Monsoon: {area} falls in or near a known {city} waterlogging belt. Avoid ground/"
    "low floors, check the society's drainage and approach-road flooding before signing."
)


class MumbaiFloodHazards:
    """Despite the name, keyed by city so other cities can be added to _FLOOD_PRONE."""

    def seasonal_risk(self, area: str, city: str) -> str:
        prone = _FLOOD_PRONE.get(city.strip().lower())
        if not prone:
            return ""
        area_l = area.lower()
        if any(keyword in area_l for keyword in prone):
            return _NOTE.format(area=area, city=city)
        return ""
