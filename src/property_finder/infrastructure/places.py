"""Google Places adapter. Implements SocietiesProvider.

Turns an area into named housing societies: geocode the area, then Places (New)
Nearby Search for residential complexes, falling back to Text Search when the
typed results are thin. Coverage is not exhaustive (a known POC limitation,
see docs/discovery-notes.md Q3).
"""
from __future__ import annotations

import httpx

_GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json"
_NEARBY = "https://places.googleapis.com/v1/places:searchNearby"
_TEXT = "https://places.googleapis.com/v1/places:searchText"
_INCLUDED_TYPES = ["apartment_complex", "housing_complex"]
_RADIUS_M = 2000.0
_MAX = 5


class GooglePlacesAdapter:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def find_societies(self, area: str, city: str) -> list[str]:
        location = f"{area}, {city}, India"
        coords = self._geocode(location)
        names: list[str] = []
        if coords is not None:
            names = self._nearby(coords)
        if len(names) < 2:
            names = self._merge(names, self._text_search(area, city))
        return names[:_MAX]

    def _geocode(self, address: str) -> tuple[float, float] | None:
        resp = httpx.get(
            _GEOCODE, params={"address": address, "key": self._api_key}, timeout=15.0
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if not results:
            return None
        loc = results[0]["geometry"]["location"]
        return (loc["lat"], loc["lng"])

    def _nearby(self, coords: tuple[float, float]) -> list[str]:
        body = {
            "includedTypes": _INCLUDED_TYPES,
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": coords[0], "longitude": coords[1]},
                    "radius": _RADIUS_M,
                }
            },
        }
        return self._place_names(_NEARBY, body)

    def _text_search(self, area: str, city: str) -> list[str]:
        body = {"textQuery": f"housing society {area} {city} India", "maxResultCount": 10}
        return self._place_names(_TEXT, body)

    def _place_names(self, url: str, body: dict) -> list[str]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": "places.displayName",
        }
        resp = httpx.post(url, json=body, headers=headers, timeout=15.0)
        resp.raise_for_status()
        places = resp.json().get("places") or []
        return [p["displayName"]["text"] for p in places if p.get("displayName")]

    @staticmethod
    def _merge(first: list[str], second: list[str]) -> list[str]:
        seen = {n.lower() for n in first}
        return first + [n for n in second if n.lower() not in seen]
