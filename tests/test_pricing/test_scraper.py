"""Tests für den Preis-Scraper."""

from kleinanzeigen_bot.pricing.scraper import (
    EBAY_SEARCH_URL,
    KLEINANZEIGEN_SEARCH_URL,
    USER_AGENTS,
    build_query_variants,
)


class TestScraperConfig:
    """Tests für die Scraper-Konfiguration."""

    def test_kleinanzeigen_url_contains_placeholder(self) -> None:
        """Kleinanzeigen-URL enthält {query}-Platzhalter."""
        assert "{query}" in KLEINANZEIGEN_SEARCH_URL

    def test_ebay_url_contains_sold_filter(self) -> None:
        """eBay-URL filtert auf verkaufte Artikel."""
        assert "LH_Sold=1" in EBAY_SEARCH_URL

    def test_user_agents_list_is_non_empty(self) -> None:
        """User-Agent-Liste enthält Einträge."""
        assert len(USER_AGENTS) > 0

    def test_user_agents_are_realistic(self) -> None:
        """User-Agents sehen realistisch aus."""
        for ua in USER_AGENTS:
            assert "Mozilla" in ua


class TestBuildQueryVariants:
    """Tests für die Erzeugung von Suchvarianten."""

    def test_empty_keywords_returns_empty_list(self) -> None:
        """Keine Keywords -> keine Varianten."""
        assert build_query_variants([]) == []

    def test_single_keyword_returns_one_variant(self) -> None:
        """Ein Keyword -> eine Variante."""
        result = build_query_variants(["iPhone"])
        assert result == ["iPhone"]

    def test_two_keywords_returns_three_variants(self) -> None:
        """Zwei Keywords -> 3 Varianten (beide, je einzeln)."""
        result = build_query_variants(["iPhone", "12"])
        assert result == ["iPhone 12", "iPhone", "12"]

    def test_three_keywords_returns_correct_order(self) -> None:
        """Drei Keywords -> spezifischste zuerst, dann weniger."""
        result = build_query_variants(["iPhone", "12", "64GB"])
        # Alle 3, dann 2er-Kombinationen, dann einzelne
        assert result[0] == "iPhone 12 64GB"
        assert len(result) == 7  # 1 + 3 + 3

    def test_most_specific_variant_is_first(self) -> None:
        """Die Variante mit allen Keywords steht immer zuerst."""
        keywords = ["Samsung", "Galaxy", "S21"]
        result = build_query_variants(keywords)
        assert result[0] == "Samsung Galaxy S21"

    def test_no_duplicate_variants(self) -> None:
        """Keine doppelten Varianten."""
        result = build_query_variants(["A", "B", "C"])
        assert len(result) == len(set(result))
