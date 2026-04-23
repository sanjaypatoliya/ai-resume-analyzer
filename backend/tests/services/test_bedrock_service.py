import json
from unittest.mock import MagicMock, patch

import pytest

from app.services.bedrock_service import analyze_resume

VALID_RESPONSE = {
    "overall_score": 72,
    "categories": [
        {"name": "Skills Match", "score": 80, "rationale": "Good match"},
        {"name": "Experience Level", "score": 70, "rationale": "Meets requirements"},
        {"name": "Education", "score": 90, "rationale": "Relevant degree"},
        {"name": "Keywords", "score": 60, "rationale": "Some missing"},
        {"name": "ATS Formatting", "score": 75, "rationale": "Clean format"},
    ],
    "skills": ["Python", "FastAPI", "AWS"],
    "experience": [{"title": "Developer", "company": "Acme", "duration": "2021-2024"}],
    "education": [{"degree": "BS CS", "institution": "University", "year": "2018"}],
    "suggestions": ["Add more keywords", "Quantify achievements"],
}


class TestAnalyzeResume:
    def test_returns_parsed_result(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(VALID_RESPONSE))]

        with patch("app.services.bedrock_service.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = mock_message

            result = analyze_resume("Resume text here", "Job description here")

        assert result["overall_score"] == 72
        assert "Python" in result["skills"]

    def test_strips_markdown_fences(self):
        wrapped = f"```json\n{json.dumps(VALID_RESPONSE)}\n```"
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=wrapped)]

        with patch("app.services.bedrock_service.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = mock_message

            result = analyze_resume("Resume text", "Job description")

        assert result["overall_score"] == 72

    def test_raises_on_invalid_json(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="not valid json at all")]

        with patch("app.services.bedrock_service.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = mock_message

            with pytest.raises(RuntimeError, match="Failed to parse AI response"):
                analyze_resume("Resume text", "Job description")

    def test_raises_on_api_error(self):
        import anthropic

        with patch("app.services.bedrock_service.anthropic.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = anthropic.APIConnectionError(request=MagicMock())

            with pytest.raises(RuntimeError, match="timed out"):
                analyze_resume("Resume text", "Job description")
