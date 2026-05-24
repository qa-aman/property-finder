from property_finder.agents.area_agent import AreaAgent
from property_finder.agents.commute_agent import CommuteAgent
from property_finder.agents.sentiment_agent import SentimentAgent
from property_finder.domain.models import CommuteEstimate, TransportMode, UserBrief


# --- test doubles -------------------------------------------------------------

class FakeLLM:
    def __init__(self, reply: str):
        self.reply = reply
        self.calls = 0

    def chat(self, system, user, response_schema=None):
        self.calls += 1
        return self.reply


class FakeSocieties:
    def find_societies(self, area, city):
        return [f"{area} One", f"{area} Two"]


class FakeMaps:
    def __init__(self, morning, evening):
        self._m, self._e = morning, evening

    def commute_estimate(self, origin, area, mode):
        return CommuteEstimate(
            minutes_morning_peak=self._m, minutes_evening_peak=self._e,
            feasible_for_mode=True, notes="",
        )


def _brief():
    return UserBrief(city="Mumbai", office_location="BKC",
                     transport_mode=TransportMode.own_car, monthly_budget_inr=50000)


# --- AreaAgent ----------------------------------------------------------------

def test_area_agent_parses_json_and_attaches_societies():
    agent = AreaAgent(FakeLLM('["Powai", "Andheri"]'), FakeSocieties())
    result = agent.propose_areas(_brief())
    assert [a for a, _ in result] == ["Powai", "Andheri"]
    assert result[0][1] == ["Powai One", "Powai Two"]


def test_area_agent_handles_malformed_json_with_regex_fallback():
    agent = AreaAgent(FakeLLM('Here you go: "Powai" and "Bandra".'), FakeSocieties())
    result = agent.propose_areas(_brief())
    assert [a for a, _ in result] == ["Powai", "Bandra"]


# --- CommuteAgent -------------------------------------------------------------

def test_commute_agent_feasible_for_short_drive():
    agent = CommuteAgent(FakeMaps(30, 40))
    est = agent.estimate("BKC", "Powai", TransportMode.own_car)
    assert est.feasible_for_mode is True
    assert est.notes


def test_commute_agent_infeasible_for_long_auto():
    agent = CommuteAgent(FakeMaps(50, 70))  # 70 > auto ceiling (45)
    est = agent.estimate("BKC", "FarPlace", TransportMode.auto)
    assert est.feasible_for_mode is False


# --- SentimentAgent -----------------------------------------------------------

class StubReviewsText:
    def __init__(self, text): self.text = text
    def neighbourhood_sentiment(self, area, city): return self.text


def test_sentiment_agent_summarizes_when_text_present():
    llm = FakeLLM("Green and well-connected.")
    agent = SentimentAgent(StubReviewsText("some reddit text"), llm)
    assert agent.summarize("Powai", "Mumbai") == "Green and well-connected."
    assert llm.calls == 1


def test_sentiment_agent_skips_llm_when_no_source_text():
    llm = FakeLLM("should not be used")
    agent = SentimentAgent(StubReviewsText("   "), llm)
    out = agent.summarize("Powai", "Mumbai")
    assert "Limited public data" in out
    assert llm.calls == 0
