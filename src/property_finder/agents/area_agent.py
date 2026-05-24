"""Proposes candidate areas and named societies for a brief.

Solves problem statement P2 (no neighbourhood intelligence for outsiders):
turns "I only know my office" into named areas and societies in range.
"""
from __future__ import annotations

import json
import re

from property_finder.domain.models import LLMPort, SocietiesProvider, UserBrief

_SYSTEM = (
    "You are a local real-estate advisor for Indian cities. Given a user's city, office "
    "location, transport mode, budget, and lifestyle preferences, propose 5 to 7 residential "
    "areas suitable for renting. Pick areas that are residential (not industrial or purely "
    "commercial), within a commute appropriate for the transport mode, and that have housing "
    "societies. Respond ONLY with a JSON array of area-name strings, no prose."
)

# Schema hint for provider-side structured output (list of strings).
_AREA_SCHEMA = {"type": "array", "items": {"type": "string"}}


class AreaAgent:
    def __init__(self, llm: LLMPort, societies: SocietiesProvider) -> None:
        self._llm = llm
        self._societies = societies

    def propose_areas(self, brief: UserBrief) -> list[tuple[str, list[str]]]:
        """Return (area_name, society_names) for each proposed area. City is read
        from brief.city, so this works for any city."""
        user = (
            f"City: {brief.city}\n"
            f"Office location: {brief.office_location}\n"
            f"Transport mode: {brief.transport_mode.value}\n"
            f"Monthly budget (INR): {brief.monthly_budget_inr}\n"
            f"Preferences: {', '.join(brief.preferences) or 'none specified'}\n\n"
            "Propose 5 to 7 residential areas."
        )
        raw = self._llm.chat(_SYSTEM, user, response_schema=_AREA_SCHEMA)
        areas = self._parse_areas(raw)

        result: list[tuple[str, list[str]]] = []
        for area in areas:
            societies = self._societies.find_societies(area, brief.city)
            result.append((area, societies))
        return result

    @staticmethod
    def _parse_areas(raw: str) -> list[str]:
        text = raw.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(a).strip() for a in parsed if str(a).strip()]
        except json.JSONDecodeError:
            pass
        # Belt-and-suspenders fallback: pull quoted strings out of the response.
        return [m.strip() for m in re.findall(r'"([^"]+)"', text) if m.strip()]
