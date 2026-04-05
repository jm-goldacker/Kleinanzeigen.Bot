"""Preisrecherche durch Scraping von Kleinanzeigen.de und eBay."""

import asyncio
import logging
import random
from itertools import combinations

import httpx

from kleinanzeigen_bot.models import PriceSource
from kleinanzeigen_bot.pricing.parser import parse_ebay_results, parse_kleinanzeigen_results

logger = logging.getLogger(__name__)

KLEINANZEIGEN_SEARCH_URL = "https://www.kleinanzeigen.de/s-{query}/k0"
EBAY_SEARCH_URL = (
    "https://www.ebay.de/sch/i.html?_nkw={query}&LH_Complete=1&LH_Sold=1&_ipg=60"
)

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) "
        "Gecko/20100101 Firefox/133.0"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    ),
]

REQUEST_DELAY_MIN = 1.0
REQUEST_DELAY_MAX = 3.0
MIN_RESULTS_THRESHOLD = 3


def build_query_variants(keywords: list[str]) -> list[str]:
    """Erzeuge Suchvarianten mit abnehmender Spezifität.

    Beginnt mit allen Keywords, dann Kombinationen mit einem
    Keyword weniger, bis hin zu einzelnen Keywords.

    Args:
        keywords: Liste von Suchbegriffen.

    Returns:
        Liste von Suchstrings, spezifischste zuerst.
    """
    if not keywords:
        return []

    variants: list[str] = []
    seen: set[str] = set()

    for length in range(len(keywords), 0, -1):
        for combo in combinations(keywords, length):
            query = " ".join(combo)
            if query not in seen:
                seen.add(query)
                variants.append(query)

    return variants


class PriceScraper:
    """Scraping-Client für Preisrecherche auf Kleinanzeigen.de und eBay."""

    def __init__(self) -> None:
        """Initialisiere den Scraper mit HTTP-Client."""
        self._client = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={"Accept-Language": "de-DE,de;q=0.9"},
        )

    async def close(self) -> None:
        """Schließe den HTTP-Client."""
        await self._client.aclose()

    async def search_prices(self, keywords: list[str]) -> list[PriceSource]:
        """Suche Preise mit Fallback auf weniger spezifische Suchanfragen.

        Versucht zuerst alle Keywords zusammen. Falls zu wenige Ergebnisse
        gefunden werden, wird mit weniger Keywords erneut gesucht.

        Args:
            keywords: Liste von Suchbegriffen.

        Returns:
            Kombinierte Liste aller gefundenen Preise.
        """
        variants = build_query_variants(keywords)
        all_prices: list[PriceSource] = []
        tried_queries: list[str] = []

        for query in variants:
            logger.info("Preisrecherche für: '%s'", query)
            tried_queries.append(query)

            prices = await self._search_both_platforms(query)
            all_prices.extend(prices)

            if len(all_prices) >= MIN_RESULTS_THRESHOLD:
                logger.info(
                    "%d Preise nach %d Suchanfrage(n) gefunden",
                    len(all_prices),
                    len(tried_queries),
                )
                return all_prices

        logger.info(
            "%d Preise nach allen %d Suchanfragen gefunden",
            len(all_prices),
            len(tried_queries),
        )
        return all_prices

    async def _search_both_platforms(self, query: str) -> list[PriceSource]:
        """Suche parallel auf Kleinanzeigen.de und eBay.

        Args:
            query: Suchbegriff.

        Returns:
            Kombinierte Ergebnisse beider Plattformen.
        """
        results = await asyncio.gather(
            self._search_kleinanzeigen(query),
            self._search_ebay(query),
            return_exceptions=True,
        )

        prices: list[PriceSource] = []
        for result in results:
            if isinstance(result, BaseException):
                logger.warning("Scraping-Fehler: %s", result)
            else:
                prices.extend(result)

        return prices

    async def _search_kleinanzeigen(self, query: str) -> list[PriceSource]:
        """Suche auf Kleinanzeigen.de."""
        url = KLEINANZEIGEN_SEARCH_URL.format(query=query.replace(" ", "-"))
        html = await self._fetch(url)
        return parse_kleinanzeigen_results(html)

    async def _search_ebay(self, query: str) -> list[PriceSource]:
        """Suche auf eBay.de (verkaufte Artikel)."""
        await asyncio.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        url = EBAY_SEARCH_URL.format(query=query.replace(" ", "+"))
        html = await self._fetch(url)
        return parse_ebay_results(html)

    async def _fetch(self, url: str) -> str:
        """HTTP GET mit zufälligem User-Agent.

        Args:
            url: Ziel-URL.

        Returns:
            HTML-Inhalt als String.

        Raises:
            httpx.HTTPError: Bei Netzwerkfehlern.
        """
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        logger.debug("Fetching: %s", url)
        response = await self._client.get(url, headers=headers)
        response.raise_for_status()
        return response.text
