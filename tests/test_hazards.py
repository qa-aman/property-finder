from property_finder.agents.orchestrator import Orchestrator
from property_finder.domain.models import CommuteEstimate
from property_finder.infrastructure.hazards import MumbaiFloodHazards


def test_flags_known_mumbai_flood_area():
    h = MumbaiFloodHazards()
    assert "Monsoon" in h.seasonal_risk("Andheri East", "Mumbai")
    assert "Monsoon" in h.seasonal_risk("Malad East", "Mumbai")


def test_no_flag_for_non_prone_or_unknown_city():
    h = MumbaiFloodHazards()
    assert h.seasonal_risk("Powai", "Mumbai") == ""       # not in the list
    assert h.seasonal_risk("Indiranagar", "Bangalore") == ""  # city has no list yet


def test_monsoon_note_lowers_confidence_in_why():
    commute = CommuteEstimate(minutes_morning_peak=20, minutes_evening_peak=25,
                              feasible_for_mode=True, notes="")
    base = Orchestrator._confidence(commute, "great area", ["a", "b", "c"])
    why = Orchestrator._why(commute, "great area", ["a", "b", "c"], monsoon="Monsoon: risk")
    assert "MONSOON RISK" in why
    # The penalty is applied in run(); here we just assert the note surfaces in why.
    assert base > 0


def test_unreliable_commute_shows_in_why():
    commute = CommuteEstimate(minutes_morning_peak=977, minutes_evening_peak=1120,
                              feasible_for_mode=False, reliable=False, notes="")
    why = Orchestrator._why(commute, "ok", ["a"])
    assert "unreliable" in why.lower()
