"""Scores commute feasibility by transport mode and time of day.

Solves problem statement P3 (commute reality is opaque): raw map distance is
not enough. A 7 km area can be fine by car but impractical by auto, especially
under local seasonal hazards (e.g. monsoon flooding in coastal cities). Treats
maps data as approximate, not ground truth. City comes from the brief.
"""
from __future__ import annotations

from property_finder.domain.models import CommuteEstimate, MapsProvider, TransportMode

# Max acceptable one-way peak commute (minutes) before a mode is judged impractical.
_FEASIBLE_CEILING = {
    TransportMode.own_car: 60,
    TransportMode.auto: 45,
    TransportMode.public: 75,
}

# Above this, an intra-city peak estimate is almost certainly a routing anomaly
# (e.g. the proposed area is the office's own locality, or geocoding degenerated).
_MAX_PLAUSIBLE_MIN = 180


class CommuteAgent:
    def __init__(self, maps: MapsProvider) -> None:
        self._maps = maps

    def estimate(self, office: str, area: str, mode: TransportMode) -> CommuteEstimate:
        raw = self._maps.commute_estimate(origin=office, area=area, mode=mode)
        worst = max(raw.minutes_morning_peak, raw.minutes_evening_peak)

        if worst > _MAX_PLAUSIBLE_MIN:
            notes = (
                f"Commute estimate looks unreliable ({raw.minutes_morning_peak}/"
                f"{raw.minutes_evening_peak} min), likely the office's own area or a routing "
                "anomaly. Treat as not validated and verify manually."
            )
            return raw.model_copy(
                update={"feasible_for_mode": False, "reliable": False, "notes": notes}
            )

        ceiling = _FEASIBLE_CEILING[mode]
        feasible = worst <= ceiling
        worse_window = (
            "morning" if raw.minutes_morning_peak >= raw.minutes_evening_peak else "evening"
        )
        verdict = "feasible" if feasible else f"likely impractical by {mode.value}"
        notes = (
            f"~{raw.minutes_morning_peak} min morning, ~{raw.minutes_evening_peak} min evening "
            f"({worse_window} worse); {verdict}. Map times are approximate."
        )
        return raw.model_copy(
            update={"feasible_for_mode": feasible, "reliable": True, "notes": notes}
        )
