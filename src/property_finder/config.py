from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # External credentials. Optional so stub mode runs without keys; the composition
    # root (application/container.py) fails fast if a real adapter needs a missing key.
    # Sentiment uses Gemini + Google Search grounding, so no Reddit key is needed.
    gemini_api_key: str | None = None
    google_maps_api_key: str | None = None

    # When true, the container wires in-memory fake adapters (no external calls).
    use_stub_adapters: bool = False

    # Optional convenience default. The city is normally supplied per search in the
    # UserBrief; this is only a fallback for demos. Leave blank to require it per request.
    default_city: str | None = None


def load_settings() -> Settings:
    """Validate config at startup. Crashes early on missing/bad values."""
    return Settings()
