from datetime import datetime, timezone

import pytest

from property_finder.domain.models import TransportMode
from property_finder.infrastructure.google_maps import GoogleMapsProvider, _next_monday_utc


def test_commute_estimate_parses_durations(httpx_mock):
    # Two calls (morning + evening); return different durations.
    httpx_mock.add_response(json={"routes": [{"duration": "2340s"}]})  # 39 min
    httpx_mock.add_response(json={"routes": [{"duration": "3000s"}]})  # 50 min

    provider = GoogleMapsProvider("key")
    est = provider.commute_estimate("Office", "Area", TransportMode.own_car)

    assert est.minutes_morning_peak == 39
    assert est.minutes_evening_peak == 50
    requests = httpx_mock.get_requests()
    assert len(requests) == 2
    assert requests[0].headers["X-Goog-Api-Key"] == "key"


def test_commute_estimate_raises_on_empty_routes(httpx_mock):
    httpx_mock.add_response(json={"routes": []})
    provider = GoogleMapsProvider("key")
    with pytest.raises(RuntimeError):
        provider.commute_estimate("Office", "Area", TransportMode.own_car)


def test_next_monday_is_in_future_and_monday():
    for hour in (9, 18):
        ts = _next_monday_utc(hour)
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        assert dt > datetime.now(timezone.utc)
        # 9 IST = 03:30 UTC, 18 IST = 12:30 UTC; weekday in IST must be Monday.
        from datetime import timedelta
        ist = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
        assert ist.weekday() == 0
        assert ist.hour == hour
