"""Preisschätzung basierend auf Marktdaten."""

import logging
import statistics
from typing import Literal

from kleinanzeigen_bot.models import PriceEstimate, PriceSource

logger = logging.getLogger(__name__)

MIN_SOURCES_FOR_HIGH_CONFIDENCE = 10
MIN_SOURCES_FOR_MEDIUM_CONFIDENCE = 5
EBAY_WEIGHT = 0.6
KLEINANZEIGEN_WEIGHT = 0.4
PERCENTILE_LOW = 5
PERCENTILE_HIGH = 95


def estimate_price(sources: list[PriceSource]) -> PriceEstimate:
    """Schätze einen Preis basierend auf Marktdaten.

    Algorithmus:
    1. Ausreißer filtern (< 5. Perzentil, > 95. Perzentil)
    2. Gewichteter Median berechnen (eBay 60%, Kleinanzeigen 40%)
    3. Interquartilsbereich als Preisspanne

    Args:
        sources: Liste von Preisquellen.

    Returns:
        PriceEstimate mit Vorschlag, Spanne und Konfidenz.
    """
    if not sources:
        logger.warning("Keine Preisquellen vorhanden")
        return PriceEstimate(
            suggested_price_cents=0,
            min_price_cents=0,
            max_price_cents=0,
            sources=[],
            confidence="none",
        )

    prices = [s.price_cents for s in sources]
    filtered_prices = _filter_outliers(prices)

    if not filtered_prices:
        filtered_prices = prices

    ebay_prices = [
        s.price_cents for s in sources if s.platform == "ebay" and s.price_cents in filtered_prices
    ]
    ka_prices = [
        s.price_cents
        for s in sources
        if s.platform == "kleinanzeigen" and s.price_cents in filtered_prices
    ]

    suggested = _weighted_median(ebay_prices, ka_prices)
    sorted_prices = sorted(filtered_prices)
    min_price = sorted_prices[0]
    max_price = sorted_prices[-1]

    # IQR als Preisspanne wenn genügend Daten
    if len(sorted_prices) >= 4:
        q1_idx = len(sorted_prices) // 4
        q3_idx = (3 * len(sorted_prices)) // 4
        min_price = sorted_prices[q1_idx]
        max_price = sorted_prices[q3_idx]

    confidence = _assess_confidence(len(sources))

    # Auf ganze Euro runden
    suggested = _round_to_euros(suggested)
    min_price = _round_to_euros(min_price)
    max_price = _round_to_euros(max_price)

    logger.info(
        "Preisschätzung: %d€ (Spanne: %d€ - %d€, Konfidenz: %s)",
        suggested // 100,
        min_price // 100,
        max_price // 100,
        confidence,
    )

    return PriceEstimate(
        suggested_price_cents=suggested,
        min_price_cents=min_price,
        max_price_cents=max_price,
        sources=sources,
        confidence=confidence,
    )


def _filter_outliers(prices: list[int]) -> list[int]:
    """Filtere Ausreißer anhand von Perzentilen.

    Args:
        prices: Liste von Preisen in Cent.

    Returns:
        Gefilterte Liste ohne Ausreißer.
    """
    if len(prices) < 5:
        return prices

    sorted_prices = sorted(prices)
    low_idx = max(0, int(len(sorted_prices) * PERCENTILE_LOW / 100))
    high_idx = min(
        len(sorted_prices) - 1,
        int(len(sorted_prices) * PERCENTILE_HIGH / 100) - 1,
    )

    low_threshold = sorted_prices[low_idx]
    high_threshold = sorted_prices[high_idx]

    return [p for p in prices if low_threshold <= p <= high_threshold]


def _weighted_median(
    ebay_prices: list[int], kleinanzeigen_prices: list[int]
) -> int:
    """Berechne gewichteten Median aus eBay und Kleinanzeigen-Preisen.

    eBay-Verkaufspreise werden stärker gewichtet (60%), da sie
    tatsächliche Verkaufspreise widerspiegeln. Kleinanzeigen-Preise
    sind Angebotspreise und typischerweise höher (40%).

    Args:
        ebay_prices: Preise von eBay (verkaufte Artikel).
        kleinanzeigen_prices: Preise von Kleinanzeigen.de.

    Returns:
        Gewichteter Median in Cent.
    """
    if not ebay_prices and not kleinanzeigen_prices:
        return 0

    if not ebay_prices:
        return int(statistics.median(kleinanzeigen_prices))

    if not kleinanzeigen_prices:
        return int(statistics.median(ebay_prices))

    ebay_median = statistics.median(ebay_prices)
    ka_median = statistics.median(kleinanzeigen_prices)

    return int(ebay_median * EBAY_WEIGHT + ka_median * KLEINANZEIGEN_WEIGHT)


def _assess_confidence(source_count: int) -> Literal["high", "medium", "low", "none"]:
    """Bewerte die Konfidenz basierend auf der Anzahl der Quellen."""
    if source_count >= MIN_SOURCES_FOR_HIGH_CONFIDENCE:
        return "high"
    if source_count >= MIN_SOURCES_FOR_MEDIUM_CONFIDENCE:
        return "medium"
    if source_count > 0:
        return "low"
    return "none"


def _round_to_euros(price_cents: int) -> int:
    """Runde auf ganze Euro."""
    return round(price_cents / 100) * 100
