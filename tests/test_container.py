import pytest

from property_finder.agents.orchestrator import Orchestrator
from property_finder.application.container import build_orchestrator
from property_finder.config import Settings


def test_stub_mode_builds_orchestrator_without_keys():
    settings = Settings(use_stub_adapters=True)
    orch = build_orchestrator(settings)
    assert isinstance(orch, Orchestrator)


def test_real_mode_fails_fast_on_missing_keys():
    # Explicit empty creds so the test is independent of any ambient env / .env.
    settings = Settings(
        use_stub_adapters=False,
        gemini_api_key=None,
        google_maps_api_key=None,
    )
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        build_orchestrator(settings)
