from unittest.mock import MagicMock, patch

from property_finder.infrastructure.gemini_llm import GeminiLLMAdapter


@patch("property_finder.infrastructure.gemini_llm.genai.Client")
def test_chat_returns_text_and_passes_model(mock_client_cls):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text="hello")
    mock_client_cls.return_value = mock_client

    adapter = GeminiLLMAdapter("key", model="gemini-2.5-flash-lite")
    out = adapter.chat("sys", "user")

    assert out == "hello"
    kwargs = mock_client.models.generate_content.call_args.kwargs
    assert kwargs["model"] == "gemini-2.5-flash-lite"
    assert kwargs["contents"] == "user"
    assert kwargs["config"].system_instruction == "sys"


@patch("property_finder.infrastructure.gemini_llm.genai.Client")
def test_chat_sets_json_schema_when_provided(mock_client_cls):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text="[]")
    mock_client_cls.return_value = mock_client

    adapter = GeminiLLMAdapter("key", model="gemini-2.5-flash")
    schema = {"type": "array", "items": {"type": "string"}}
    adapter.chat("sys", "user", response_schema=schema)

    config = mock_client.models.generate_content.call_args.kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == schema


@patch("property_finder.infrastructure.gemini_llm.genai.Client")
def test_chat_handles_none_text(mock_client_cls):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text=None)
    mock_client_cls.return_value = mock_client

    adapter = GeminiLLMAdapter("key", model="gemini-2.5-flash")
    assert adapter.chat("sys", "user") == ""
