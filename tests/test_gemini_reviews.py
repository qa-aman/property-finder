from unittest.mock import MagicMock, patch

from property_finder.infrastructure.gemini_reviews import GeminiGroundedReviews


@patch("property_finder.infrastructure.gemini_reviews.genai.Client")
def test_returns_grounded_text_and_enables_search(mock_client_cls):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(text="Green, safe, busy mornings.")
    mock_client_cls.return_value = mock_client

    out = GeminiGroundedReviews("key").neighbourhood_sentiment("Powai", "Mumbai")

    assert out == "Green, safe, busy mornings."
    config = mock_client.models.generate_content.call_args.kwargs["config"]
    assert config.tools  # google_search tool attached


@patch("property_finder.infrastructure.gemini_reviews.genai.Client")
def test_returns_empty_on_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("boom")
    mock_client_cls.return_value = mock_client

    out = GeminiGroundedReviews("key").neighbourhood_sentiment("Powai", "Mumbai")
    assert out == ""
