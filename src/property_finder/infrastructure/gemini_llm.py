"""Google Gemini adapter. Implements LLMPort via the google-genai SDK.

Used for two tasks with different models (wired in the container):
  - gemini-2.5-flash for area proposal (reasoning + structured JSON output)
  - gemini-2.5-flash-lite for sentiment summarization (cheap, high-volume)

No manual context caching: Gemini applies implicit caching, and our system
prompts are below the explicit-cache threshold.
"""
from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types


class GeminiLLMAdapter:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def chat(self, system: str, user: str, response_schema: Any | None = None) -> str:
        config = types.GenerateContentConfig(system_instruction=system)
        if response_schema is not None:
            config.response_mime_type = "application/json"
            config.response_json_schema = response_schema

        response = self._client.models.generate_content(
            model=self._model,
            contents=user,
            config=config,
        )
        return response.text or ""
