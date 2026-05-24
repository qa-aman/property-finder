from unittest.mock import MagicMock, patch

from property_finder.agents.orchestrator import _matches
from property_finder.domain.models import Listing, TransportMode, UserBrief
from property_finder.infrastructure.gemini_listings import GeminiGroundedListings


def _brief(**kw):
    base = dict(city="Mumbai", office_location="Goregaon East",
                transport_mode=TransportMode.own_car, monthly_budget_inr=50000)
    base.update(kw)
    return UserBrief(**base)


# --- filter logic -------------------------------------------------------------

def test_matches_keeps_unknown_attributes():
    brief = _brief(min_sqft=500, needs_car_parking=True, bhk="1 BHK")
    # All criteria unknown on the listing -> not excluded (best-effort data).
    assert _matches(Listing(title="X"), brief) is True


def test_excludes_over_budget():
    brief = _brief(monthly_budget_inr=40000)
    assert _matches(Listing(title="X", rent_inr=55000), brief) is False
    assert _matches(Listing(title="Y", rent_inr=38000), brief) is True


def test_excludes_too_small_and_no_parking():
    brief = _brief(min_sqft=500, needs_car_parking=True)
    assert _matches(Listing(title="small", sqft=400), brief) is False
    assert _matches(Listing(title="noparking", car_parking=False), brief) is False
    assert _matches(Listing(title="ok", sqft=600, car_parking=True), brief) is True


def test_bhk_and_furnishing_match():
    brief = _brief(bhk="1 BHK", furnishing="semi-furnished")
    assert _matches(Listing(title="a", bhk="2 BHK"), brief) is False
    assert _matches(Listing(title="b", bhk="1 BHK", furnishing="semi-furnished"), brief) is True
    assert _matches(Listing(title="c", furnishing="unfurnished"), brief) is False


# --- adapter parsing ----------------------------------------------------------

@patch("property_finder.infrastructure.gemini_listings.genai.Client")
def test_adapter_parses_json_listings(mock_client_cls):
    payload = (
        '[{"title":"Flat A","rent_inr":45000,"bhk":"1 BHK","sqft":550,'
        '"car_parking":true,"furnishing":"semi-furnished","source_url":"http://x"}]'
    )
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text=payload)
    mock_client_cls.return_value = mock_client

    out = GeminiGroundedListings("key").find_listings("Powai", _brief())
    assert len(out) == 1
    assert out[0].rent_inr == 45000 and out[0].sqft == 550
    assert out[0].car_parking is True
    assert out[0].verified is False


@patch("property_finder.infrastructure.gemini_listings.genai.Client")
def test_adapter_handles_fenced_and_dirty_numbers(mock_client_cls):
    payload = '```json\n[{"title":"B","rent_inr":"INR 42,000","sqft":"600 sq ft"}]\n```'
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text=payload)
    mock_client_cls.return_value = mock_client

    out = GeminiGroundedListings("key").find_listings("Powai", _brief())
    assert out[0].rent_inr == 42000
    assert out[0].sqft == 600


@patch("property_finder.infrastructure.gemini_listings.genai.Client")
def test_adapter_recovers_bhk_from_title(mock_client_cls):
    payload = (
        '[{"title":"1 BHK Flat in Sushanku Avenue, Goregaon East","rent_inr":42000,'
        '"bhk":null,"sqft":619},'
        '{"title":"Spacious 2.5 BHK near Marol","bhk":null}]'
    )
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text=payload)
    mock_client_cls.return_value = mock_client

    out = GeminiGroundedListings("key").find_listings("Goregaon East", _brief())
    assert out[0].bhk == "1 BHK"
    assert out[1].bhk == "2.5 BHK"


@patch("property_finder.infrastructure.gemini_listings.genai.Client")
def test_adapter_returns_empty_on_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("boom")
    mock_client_cls.return_value = mock_client
    assert GeminiGroundedListings("key").find_listings("Powai", _brief()) == []
