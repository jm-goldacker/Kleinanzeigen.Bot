"""Preisrecherche durch Scraping von Kleinanzeigen.de und eBay."""

import asyncio
import logging
import random

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    ),
]

REQUEST_DELAY_MIN = 1.0
REQUEST_DELAY_MAX = 3.0


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
        """Suche Preise auf Kleinanzeigen.de und eBay für gegebene Suchbegriffe.

        Args:
            keywords: Liste von Suchbegriffen.

        Returns:
            Kombinierte Liste aller gefundenen Preise.
        """
        query = " ".join(keywords)
        logger.info("Starte Preisrecherche für: '%s'", query)

        kleinanzeigen_task = self._search_kleinanzeigen(query)
        ebay_task = self._search_ebay(query)

        results = await asyncio.gather(
            kleinanzeigen_task, ebay_task, return_exceptions=True
        )

        all_prices: list[PriceSource] = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Scraping-Fehler: %s", result)
            else:
                all_prices.extend(result)

        logger.info("Insgesamt %d Preise gefunden", len(all_prices))
        return all_prices

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
