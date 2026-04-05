"""Tests für den HTML-Parser."""

import pytest

from kleinanzeigen_bot.pricing.parser import (
    _parse_price_text,
    parse_ebay_results,
    parse_kleinanzeigen_results,
)


class TestParsePrice:
    """Tests für die Preis-Extraktion aus Text."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("150 €", 15000),
            ("25,50 €", 2550),
            ("1.250 €", 125000),
            ("1.250,00 €", 125000),
            ("99 €", 9900),
            ("3,50 €", 350),
            ("12.345,67 €", 1234567),
        ],
    )
    def test_parse_valid_price_returns_cents(self, text: str, expected: int) -> None:
        """Gültiger Preistext → korrekte Cent-Beträge."""
        assert _parse_price_text(text) == expected

    @pytest.mark.parametrize(
        "text",
        ["VB", "Zu verschenken", "", "   "],
    )
    def test_parse_non_numeric_price_returns_none(self, text: str) -> None:
        """Nicht-numerische Preise → None."""
        assert _parse_price_text(text) is None

    def test_parse_price_with_eur_suffix(self) -> None:
        """EUR statt € → korrekt geparst."""
        assert _parse_price_text("50 EUR") == 5000


class TestParseKleinanzeigenResults:
    """Tests für das Parsen von Kleinanzeigen-Suchergebnissen."""

    def test_parse_empty_html_returns_empty_list(self) -> None:
        """Leeres HTML → leere Liste."""
        assert parse_kleinanzeigen_results("<html></html>") == []

    def test_parse_ad_items_extracts_prices(self) -> None:
        """HTML mit Anzeigen → Preise extrahiert."""
        html = """
        <article class="aditem">
            <a class="ellipsis" href="/s-anzeige/test/123">iPhone 12</a>
            <p class="aditem-main--middle--price-shipping--price">350 €</p>
        </article>
        <article class="aditem">
            <a class="ellipsis" href="/s-anzeige/test/456">Samsung S21</a>
            <p class="aditem-main--middle--price-shipping--price">250 €</p>
        </article>
        """
        results = parse_kleinanzeigen_results(html)
        assert len(results) == 2
        assert results[0].title == "iPhone 12"
        assert results[0].price_cents == 35000
        assert results[0].platform == "kleinanzeigen"
        assert "123" in results[0].url


class TestParseEbayResults:
    """Tests für das Parsen von eBay-Suchergebnissen."""

    def test_parse_empty_html_returns_empty_list(self) -> None:
        """Leeres HTML → leere Liste."""
        assert parse_ebay_results("<html></html>") == []

    def test_parse_sold_items_extracts_prices(self) -> None:
        """HTML mit verkauften Artikeln → Preise extrahiert."""
        html = """
        <li class="s-item">
            <div class="s-item__title"><span>iPhone 12 64GB</span></div>
            <span class="s-item__price">320,00 €</span>
            <a class="s-item__link" href="https://www.ebay.de/itm/123"></a>
        </li>
        """
        results = parse_ebay_results(html)
        assert len(results) == 1
        assert results[0].title == "iPhone 12 64GB"
        assert results[0].price_cents == 32000
        assert results[0].platform == "ebay"

    def test_parse_skips_shop_on_ebay_entries(self) -> None:
        """'Shop on eBay'-Einträge werden übersprungen."""
        html = """
        <li class="s-item">
            <div class="s-item__title"><span>Shop on eBay</span></div>
            <span class="s-item__price">0 €</span>
        </li>
        """
        results = parse_ebay_results(html)
        assert len(results) == 0
