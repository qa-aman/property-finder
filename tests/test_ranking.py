from property_finder.agents.orchestrator import Orchestrator
from property_finder.domain.models import CommuteEstimate


def _commute(morning, evening, feasible):
    return CommuteEstimate(minutes_morning_peak=morning, minutes_evening_peak=evening,
                           feasible_for_mode=feasible, notes="")


def test_confidence_rewards_short_feasible_commute():
    near = Orchestrator._confidence(_commute(20, 25, True), "great area", ["a", "b", "c", "d", "e"])
    far = Orchestrator._confidence(_commute(70, 85, True), "great area", ["a", "b", "c", "d", "e"])
    assert near > far


def test_infeasible_commute_is_capped():
    infeasible = Orchestrator._confidence(_commute(80, 95, False), "great", ["a", "b", "c", "d", "e"])
    feasible = Orchestrator._confidence(_commute(80, 95, True), "great", ["a", "b", "c", "d", "e"])
    assert infeasible <= feasible


def test_bad_sentiment_lowers_score():
    good = Orchestrator._confidence(_commute(30, 35, True), "safe and green", ["a", "b"])
    bad = Orchestrator._confidence(_commute(30, 35, True), "unsafe and prone to flood", ["a", "b"])
    assert bad < good


def test_more_societies_raises_coverage():
    few = Orchestrator._confidence(_commute(30, 35, True), "ok", ["a"])
    many = Orchestrator._confidence(_commute(30, 35, True), "ok", ["a", "b", "c", "d", "e"])
    assert many > few
