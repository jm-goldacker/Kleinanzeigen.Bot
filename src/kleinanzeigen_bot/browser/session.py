"""Playwright Browser-Session-Management."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger(__name__)


@asynccontextmanager
async def create_browser_session(
    headless: bool = True,
    slow_mo: int = 100,
) -> AsyncGenerator[Page, None]:
    """Erstelle eine Playwright-Browser-Session.

    Verwendet Chrome-Channel für geringere Bot-Erkennung.

    Args:
        headless: Browser im Headless-Modus starten.
        slow_mo: Verzögerung zwischen Aktionen in Millisekunden.

    Yields:
        Playwright Page-Objekt.
    """
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(
            headless=headless,
            slow_mo=slow_mo,
            channel="chrome",
        )
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="de-DE",
            timezone_id="Europe/Berlin",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page: Page = await context.new_page()

        logger.info(
            "Browser-Session gestartet (headless=%s, slow_mo=%dms)",
            headless,
            slow_mo,
        )

        try:
            yield page
        finally:
            await context.close()
            await browser.close()
            logger.info("Browser-Session beendet")
