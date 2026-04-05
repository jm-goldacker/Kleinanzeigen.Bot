"""HTML-Parser für Suchergebnisse von Kleinanzeigen.de und eBay."""

import logging
import re

from bs4 import BeautifulSoup

from kleinanzeigen_bot.models import PriceSource

logger = logging.getLogger(__name__)


def parse_kleinanzeigen_results(html: str) -> list[PriceSource]:
    """Parse Suchergebnisse von Kleinanzeigen.de.

    Args:
        html: HTML-Inhalt der Suchergebnisseite.

    Returns:
        Liste von PriceSource-Objekten mit extrahierten Preisen.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[PriceSource] = []

    ad_items = soup.select("article.aditem")

    for item in ad_items:
        title_elem = item.select_one("a.ellipsis")
        price_elem = item.select_one("p.aditem-main--middle--price-shipping--price")

        if not title_elem or not price_elem:
            continue

        title = title_elem.get_text(strip=True)
        price_text = price_elem.get_text(strip=True)
        price_cents = _parse_price_text(price_text)

        if price_cents is None or price_cents == 0:
            continue

        href = title_elem.get("href", "")
        url = f"https://www.kleinanzeigen.de{href}" if href else ""

        results.append(
            PriceSource(
                platform="kleinanzeigen",
                title=title,
                price_cents=price_cents,
                url=url,
            )
        )

    logger.info("Kleinanzeigen: %d Preise extrahiert", len(results))
    return results


def parse_ebay_results(html: str) -> list[PriceSource]:
    """Parse Suchergebnisse von eBay.de (verkaufte Artikel).

    Args:
        html: HTML-Inhalt der Suchergebnisseite.

    Returns:
        Liste von PriceSource-Objekten mit extrahierten Preisen.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[PriceSource] = []

    items = soup.select("li.s-item")

    for item in items:
        title_elem = item.select_one(".s-item__title span")
        price_elem = item.select_one(".s-item__price")
        link_elem = item.select_one("a.s-item__link")

        if not title_elem or not price_elem:
            continue

        title = title_elem.get_text(strip=True)
        if title.lower() in ("shop on ebay", "ergebnisse"):
            continue

        price_text = price_elem.get_text(strip=True)
        price_cents = _parse_price_text(price_text)

        if price_cents is None or price_cents == 0:
            continue

        url = str(link_elem.get("href", "")) if link_elem else ""

        results.append(
            PriceSource(
                platform="ebay",
                title=title,
                price_cents=price_cents,
                url=url,
            )
        )

    logger.info("eBay: %d Preise extrahiert", len(results))
    return results


def _parse_price_text(text: str) -> int | None:
    """Extrahiere Preis in Cent aus einem Preistext.

    Beispiele:
        "150 €" → 15000
        "25,50 €" → 2550
        "1.250,00 €" → 125000
        "VB" → None

    Args:
        text: Preistext wie "150 €" oder "25,50 €".

    Returns:
        Preis in Cent oder None wenn nicht parsebar.
    """
    cleaned = text.replace("€", "").replace("EUR", "").strip()

    if not cleaned or cleaned.upper() in ("VB", "ZU VERSCHENKEN"):
        return None

    # Muster: "1.250,50" oder "150" oder "25,50"
    match = re.search(r"(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)", cleaned)
    if not match:
        return None

    price_str = match.group(1)
    price_str = price_str.replace(".", "")  # Tausendertrennzeichen entfernen
    price_str = price_str.replace(",", ".")  # Dezimalkomma → Dezimalpunkt

    try:
        return int(float(price_str) * 100)
    except ValueError:
        return None
