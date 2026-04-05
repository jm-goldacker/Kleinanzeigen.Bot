"""Tests für die Preisschätzung."""

from kleinanzeigen_bot.models import PriceSource
from kleinanzeigen_bot.pricing.estimator import (
    _filter_outliers,
    _round_to_euros,
    _weighted_median,
    estimate_price,
)


class TestEstimatePrice:
    """Tests für die Preisschätzungs-Logik."""

    def test_estimate_with_no_sources_returns_zero(self) -> None:
        """Keine Quellen → Preis 0, Konfidenz 'none'."""
        result = estimate_price([])
        assert result.suggested_price_cents == 0
        assert result.confidence == "none"

    def test_estimate_with_sources_returns_valid_estimate(self) -> None:
        """Mehrere Quellen → gültige Schätzung."""
        sources = [
            PriceSource(platform="ebay", title=f"Item {i}", price_cents=p)
            for i, p in enumerate([30000, 32000, 35000, 28000, 31000])
        ] + [
            PriceSource(platform="kleinanzeigen", title=f"KA {i}", price_cents=p)
            for i, p in enumerate([35000, 38000, 33000, 36000, 34000])
        ]
        result = estimate_price(sources)
        assert result.suggested_price_cents > 0
        assert result.min_price_cents <= result.suggested_price_cents
        assert result.max_price_cents >= result.suggested_price_cents
        assert result.confidence == "high"

    def test_estimate_with_few_sources_returns_low_confidence(self) -> None:
        """Wenige Quellen → niedrige Konfidenz."""
        sources = [
            PriceSource(platform="ebay", title="Item 1", price_cents=20000),
            PriceSource(platform="ebay", title="Item 2", price_cents=22000),
        ]
        result = estimate_price(sources)
        assert result.confidence == "low"

    def test_estimate_rounds_to_whole_euros(self) -> None:
        """Preise werden auf ganze Euro gerundet."""
        sources = [
            PriceSource(platform="ebay", title=f"Item {i}", price_cents=p)
            for i, p in enumerate([15050, 15150, 15250])
        ]
        result = estimate_price(sources)
        assert result.suggested_price_cents % 100 == 0


class TestFilterOutliers:
    """Tests für die Ausreißer-Filterung."""

    def test_filter_with_few_prices_returns_all(self) -> None:
        """Weniger als 5 Preise → keine Filterung."""
        prices = [100, 200, 300]
        assert _filter_outliers(prices) == prices

    def test_filter_removes_extreme_values(self) -> None:
        """Extreme Werte werden entfernt."""
        prices = [100, 200, 200, 210, 220, 200, 190, 195, 205, 10000]
        filtered = _filter_outliers(prices)
        assert 10000 not in filtered


class TestWeightedMedian:
    """Tests für den gewichteten Median."""

    def test_weighted_median_with_both_sources(self) -> None:
        """Beide Quellen → gewichteter Wert."""
        result = _weighted_median([30000], [40000])
        # 30000 * 0.6 + 40000 * 0.4 = 18000 + 16000 = 34000
        assert result == 34000

    def test_weighted_median_ebay_only(self) -> None:
        """Nur eBay → eBay-Median."""
        assert _weighted_median([30000, 32000, 34000], []) == 32000

    def test_weighted_median_kleinanzeigen_only(self) -> None:
        """Nur Kleinanzeigen → Kleinanzeigen-Median."""
        assert _weighted_median([], [30000, 35000, 40000]) == 35000

    def test_weighted_median_no_sources_returns_zero(self) -> None:
        """Keine Quellen → 0."""
        assert _weighted_median([], []) == 0


class TestRoundToEuros:
    """Tests für die Euro-Rundung."""

    def test_round_up(self) -> None:
        assert _round_to_euros(1550) == 1600

    def test_round_down(self) -> None:
        assert _round_to_euros(1540) == 1500

    def test_exact_euros(self) -> None:
        assert _round_to_euros(1500) == 1500
