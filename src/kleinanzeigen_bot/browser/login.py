"""Login-Flow für Kleinanzeigen.de."""

import logging

from playwright.async_api import Page

from kleinanzeigen_bot.browser import selectors

logger = logging.getLogger(__name__)


class LoginError(Exception):
    """Fehler beim Login auf Kleinanzeigen.de."""


async def login(page: Page, email: str, password: str) -> None:
    """Logge sich bei Kleinanzeigen.de ein.

    Args:
        page: Playwright Page-Objekt.
        email: E-Mail-Adresse.
        password: Passwort.

    Raises:
        LoginError: Wenn der Login fehlschlägt.
    """
    logger.info("Starte Login auf Kleinanzeigen.de")

    await page.goto(
        selectors.LOGIN_URL, wait_until="domcontentloaded",
        timeout=selectors.PAGE_LOAD_TIMEOUT * 1000,
    )

    # Cookie-Banner akzeptieren (falls vorhanden)
    await _accept_cookies(page)

    # Login-Daten eingeben
    await page.fill(selectors.LOGIN_EMAIL_INPUT, email)
    await page.fill(selectors.LOGIN_PASSWORD_INPUT, password)
    await page.click(selectors.LOGIN_SUBMIT_BUTTON)

    # Auf erfolgreichen Login warten
    try:
        await page.wait_for_selector(
            selectors.LOGIN_SUCCESS_INDICATOR,
            timeout=selectors.PAGE_LOAD_TIMEOUT * 1000,
        )
        logger.info("Login erfolgreich")
    except Exception as e:
        raise LoginError(
            "Login fehlgeschlagen. Bitte prüfe E-Mail und Passwort."
        ) from e


async def _accept_cookies(page: Page) -> None:
    """Akzeptiere den Cookie-Banner, falls vorhanden."""
    try:
        cookie_btn = page.locator(selectors.COOKIE_ACCEPT_BUTTON)
        await cookie_btn.click(timeout=3000)
        logger.debug("Cookie-Banner akzeptiert")
    except Exception:
        logger.debug("Kein Cookie-Banner gefunden")
