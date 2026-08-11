import pytest

from app.llm import gemini_client


def test_gemini_client_requires_api_key(monkeypatch):

    monkeypatch.setattr(
        gemini_client.settings,
        "GROQ_API_KEY",
        "",
    )

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is not set",
    ):
        gemini_client.GeminiClient()