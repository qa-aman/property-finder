import importlib

from fastapi.testclient import TestClient


def _stub_client(monkeypatch):
    monkeypatch.setenv("USE_STUB_ADAPTERS", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "")
    import property_finder.main as m
    importlib.reload(m)  # re-read settings with stub mode on
    return TestClient(m.app)


def _brief(city="Bangalore"):
    return {
        "city": city,
        "office_location": "Indiranagar",
        "transport_mode": "own_car",
        "monthly_budget_inr": 40000,
        "preferences": ["quiet", "near metro"],
    }


def test_shortlist_returns_ranked_recommendations(monkeypatch):
    with _stub_client(monkeypatch) as client:
        resp = client.post("/shortlist", json=_brief())

    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "Bangalore"
    recs = data["recommendations"]
    assert 0 < len(recs) <= 5

    for rec in recs:
        assert rec["area_name"]
        assert isinstance(rec["society_names"], list)
        assert "minutes_morning_peak" in rec["commute"]
        assert rec["sentiment_summary"]
        assert 0.0 <= rec["confidence"] <= 1.0

    confidences = [r["confidence"] for r in recs]
    assert confidences == sorted(confidences, reverse=True)


def test_shortlist_rejects_invalid_brief(monkeypatch):
    bad = _brief()
    bad["monthly_budget_inr"] = 0
    with _stub_client(monkeypatch) as client:
        resp = client.post("/shortlist", json=bad)
    assert resp.status_code == 422


def test_works_for_a_different_city(monkeypatch):
    with _stub_client(monkeypatch) as client:
        resp = client.post("/shortlist", json=_brief(city="Mumbai"))
    assert resp.status_code == 200
    assert resp.json()["city"] == "Mumbai"
