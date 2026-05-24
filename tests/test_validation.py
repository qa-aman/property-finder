import pytest
from pydantic import ValidationError

from property_finder.domain.models import TransportMode, UserBrief


def test_valid_brief():
    brief = UserBrief(city="Pune", office_location="Hinjewadi",
                      transport_mode=TransportMode.public, monthly_budget_inr=30000)
    assert brief.city == "Pune"


@pytest.mark.parametrize("field,value", [("city", "  "), ("office_location", "")])
def test_blank_text_rejected(field, value):
    kwargs = dict(city="Pune", office_location="Hinjewadi",
                  transport_mode=TransportMode.public, monthly_budget_inr=30000)
    kwargs[field] = value
    with pytest.raises(ValidationError):
        UserBrief(**kwargs)


def test_non_positive_budget_rejected():
    with pytest.raises(ValidationError):
        UserBrief(city="Pune", office_location="Hinjewadi",
                  transport_mode=TransportMode.public, monthly_budget_inr=0)


def test_invalid_transport_mode_rejected():
    with pytest.raises(ValidationError):
        UserBrief(city="Pune", office_location="Hinjewadi",
                  transport_mode="helicopter", monthly_budget_inr=30000)
