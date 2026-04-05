"""Tests für den Preis-Scraper."""

from kleinanzeigen_bot.pricing.scraper import (
    EBAY_SEARCH_URL,
    KLEINANZEIGEN_SEARCH_URL,
    USER_AGENTS,
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
