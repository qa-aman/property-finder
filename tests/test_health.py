import importlib

from fastapi.testclient import TestClient


def test_health_reports_default_city(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test")
    monkeypatch.setenv("DEFAULT_CITY", "Bangalore")

    import property_finder.main as m
    importlib.reload(m)  # re-read settings with the patched env

    client = TestClient(m.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["default_city"] == "Bangalore"
