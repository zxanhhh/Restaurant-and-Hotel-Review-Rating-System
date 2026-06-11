import pytest
from unittest.mock import patch, MagicMock
from pipeline.claude_client import _strip_markdown, analyze_review
from pipeline.store import VALID_SENTIMENTS, CONFIDENCE_THRESHOLD
from pipeline.prompt import build_user_prompt, SYSTEM_PROMPT


class TestStripMarkdown:
    def test_no_markdown(self):
        raw = '{"categories": {}}'
        assert _strip_markdown(raw) == raw

    def test_json_fenced(self):
        raw = '```json\n{"categories": {}}\n```'
        assert _strip_markdown(raw) == '{"categories": {}}'

    def test_plain_fenced(self):
        raw = '```\n{"categories": {}}\n```'
        assert _strip_markdown(raw) == '{"categories": {}}'

    def test_strips_whitespace(self):
        raw = '   {"categories": {}}   '
        assert _strip_markdown(raw) == '{"categories": {}}'

    def test_multiline_json(self):
        raw = '```json\n{\n  "categories": {}\n}\n```'
        result = _strip_markdown(raw)
        assert result.startswith('{') and result.endswith('}')


class TestBuildPrompt:
    def test_contains_review_prefix(self):
        prompt = build_user_prompt("Đồ ăn ngon")
        assert prompt.startswith("Review:")
        assert "Đồ ăn ngon" in prompt

    def test_system_prompt_has_required_rules(self):
        assert "positive|neutral|negative" in SYSTEM_PROMPT
        assert "confidence"                in SYSTEM_PROMPT
        assert "raw JSON only"             in SYSTEM_PROMPT
        assert "null"                      in SYSTEM_PROMPT


class TestPipelineConstants:
    def test_valid_sentiments(self):
        assert VALID_SENTIMENTS == {"positive", "neutral", "negative"}

    def test_confidence_threshold(self):
        assert CONFIDENCE_THRESHOLD == 0.15


class TestAnalyzeReview:
    def test_json_parse_error_returns_none(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="NOT VALID JSON {{{{")]
        with patch("pipeline.claude_client.client") as mock_client:
            mock_client.messages.create.return_value = mock_response
            result = analyze_review("Some review text")
        assert result is None

    def test_missing_categories_key_returns_none(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"wrong_key": {}}')]
        with patch("pipeline.claude_client.client") as mock_client:
            mock_client.messages.create.return_value = mock_response
            result = analyze_review("Some review text")
        assert result is None

    def test_valid_response_returned(self):
        valid_json = '{"categories": {"Food": {"sentiment": "positive", "strength": "Ngon", "weakness": null, "confidence": 0.9}}}'
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=valid_json)]
        with patch("pipeline.claude_client.client") as mock_client:
            mock_client.messages.create.return_value = mock_response
            result = analyze_review("Đồ ăn rất ngon!")
        assert result is not None
        assert "categories" in result
        assert result["categories"]["Food"]["sentiment"] == "positive"
