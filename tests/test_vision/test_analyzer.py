"""Tests für den Vision-Analyzer."""

import pytest

from kleinanzeigen_bot.vision.analyzer import (
    VisionAnalysisError,
    _parse_vision_response,
)


class TestParseVisionResponse:
    """Tests für das Parsen der Ollama-Antworten."""

    def test_parse_valid_json_returns_vision_result(self) -> None:
        """Gültiges JSON → VisionResult."""
        raw = '''{
            "title": "Apple iPhone 12, 64GB, schwarz",
            "description": "Gut erhaltenes iPhone 12 in schwarz mit 64GB Speicher.",
            "search_keywords": ["iPhone 12", "64GB"],
            "condition": "gut"
        }'''
        result = _parse_vision_response(raw)
        assert result.title == "Apple iPhone 12, 64GB, schwarz"
        assert result.condition == "gut"
        assert len(result.search_keywords) == 2

    def test_parse_json_in_markdown_code_block_returns_vision_result(self) -> None:
        """JSON in Markdown-Codeblock → VisionResult."""
        raw = '''Hier ist meine Analyse:

```json
{
    "title": "Samsung Galaxy S21",
    "description": "Smartphone in gutem Zustand.",
    "search_keywords": ["Samsung", "Galaxy S21"],
    "condition": "sehr gut"
}
```'''
        result = _parse_vision_response(raw)
        assert result.title == "Samsung Galaxy S21"

    def test_parse_json_in_generic_code_block_returns_vision_result(self) -> None:
        """JSON in generischem Codeblock → VisionResult."""
        raw = '''```
{
    "title": "IKEA Regal",
    "description": "Weißes Regal.",
    "search_keywords": ["IKEA", "Regal"],
    "condition": "gut"
}
```'''
        result = _parse_vision_response(raw)
        assert result.title == "IKEA Regal"

    def test_parse_invalid_json_raises_vision_analysis_error(self) -> None:
        """Ungültiges JSON → VisionAnalysisError."""
        with pytest.raises(VisionAnalysisError, match="kein gültiges JSON"):
            _parse_vision_response("Das ist kein JSON")

    def test_parse_missing_fields_raises_vision_analysis_error(self) -> None:
        """Fehlende Pflichtfelder → VisionAnalysisError."""
        raw = '{"title": "Test"}'
        with pytest.raises(VisionAnalysisError, match="ungültiges Format"):
            _parse_vision_response(raw)

    def test_parse_title_too_long_raises_vision_analysis_error(self) -> None:
        """Titel über 70 Zeichen -> VisionAnalysisError."""
        title = "A" * 71
        raw = (
            f'{{"title": "{title}", "description": "Test", '
            f'"search_keywords": ["test"], "condition": "gut"}}'
        )
        with pytest.raises(VisionAnalysisError):
            _parse_vision_response(raw)

    def test_parse_too_many_keywords_truncates_to_five(self) -> None:
        """Mehr als 5 Keywords werden auf 5 gekürzt."""
        raw = '''{
            "title": "Furby Magenta",
            "description": "Seltenes Furby Sammlerstück.",
            "search_keywords": ["furby", "magenta", "pink", "plush", "vintage", "extra"],
            "condition": "gut"
        }'''
        result = _parse_vision_response(raw)
        assert len(result.search_keywords) == 5
        assert result.search_keywords == ["furby", "magenta", "pink", "plush", "vintage"]
