"""Anzeige bei Kleinanzeigen.de erstellen und veröffentlichen."""

import logging

from playwright.async_api import Page

from kleinanzeigen_bot.browser import selectors
from kleinanzeigen_bot.models import Article, ArticleStatus, PriceType

logger = logging.getLogger(__name__)


class PublishError(Exception):
    """Fehler beim Veröffentlichen einer Anzeige."""


async def publish_article(page: Page, article: Article) -> Article:
    """Veröffentliche einen Artikel auf Kleinanzeigen.de.

    Voraussetzung: Login wurde bereits durchgeführt.

    Args:
        page: Playwright Page-Objekt (eingeloggt).
        article: Zu veröffentlichender Artikel.

    Returns:
        Artikel mit aktualisiertem Status.

    Raises:
        PublishError: Bei Fehlern im Veröffentlichungs-Flow.
    """
    logger.info("Veröffentliche Artikel: '%s'", article.title)
    article.status = ArticleStatus.PUBLISHING

    try:
        # Zur Anzeigen-Seite navigieren
        await page.goto(
            selectors.POST_AD_URL,
            wait_until="domcontentloaded",
            timeout=selectors.PAGE_LOAD_TIMEOUT * 1000,
        )

        # "Anzeige aufgeben" klicken
        await page.click(selectors.NEW_AD_BUTTON)
        await page.wait_for_load_state("domcontentloaded")

        # Kategorie setzen
        await _set_category(page, article.category.category_id)

        # Formular ausfüllen
        await _fill_form(page, article)

        # Bilder hochladen
        await _upload_images(page, article)

        # Absenden
        await page.click(selectors.SUBMIT_AD_BUTTON)

        # Auf Erfolg warten
        await page.wait_for_selector(
            selectors.AD_SUCCESS_INDICATOR,
            timeout=selectors.UPLOAD_TIMEOUT * 1000,
        )

        article.status = ArticleStatus.PUBLISHED
        logger.info("Artikel erfolgreich veröffentlicht: '%s'", article.title)

    except PublishError:
        article.status = ArticleStatus.FAILED
        raise
    except Exception as e:
        article.status = ArticleStatus.FAILED
        raise PublishError(
            f"Fehler beim Veröffentlichen von '{article.title}': {e}"
        ) from e

    return article


async def _set_category(page: Page, category_id: str) -> None:
    """Wähle die Kategorie im Formular.

    Args:
        page: Playwright Page-Objekt.
        category_id: Kleinanzeigen Kategorie-ID.
    """
    logger.debug("Setze Kategorie: %s", category_id)

    # Kategorie-URL direkt aufrufen (zuverlässiger als UI-Navigation)
    current_url = page.url
    if "?" in current_url:
        category_url = f"{current_url}&categoryId={category_id}"
    else:
        category_url = f"{current_url}?categoryId={category_id}"

    await page.goto(category_url, wait_until="domcontentloaded")


async def _fill_form(page: Page, article: Article) -> None:
    """Fülle das Anzeigen-Formular aus.

    Args:
        page: Playwright Page-Objekt.
        article: Artikel mit den Formulardaten.
    """
    logger.debug("Fülle Formular aus")

    # Titel
    await page.fill(selectors.AD_FORM_TITLE, article.title)

    # Beschreibung
    await page.fill(selectors.AD_FORM_DESCRIPTION, article.description)

    # Preis
    price_euros = str(article.price_euros).replace(".", ",")
    await page.fill(selectors.AD_FORM_PRICE, price_euros)

    # Preisart
    price_type_selector = {
        PriceType.FIXED: selectors.AD_FORM_PRICE_TYPE_FIXED,
        PriceType.NEGOTIABLE: selectors.AD_FORM_PRICE_TYPE_NEGOTIABLE,
        PriceType.GIVEAWAY: selectors.AD_FORM_PRICE_TYPE_GIVEAWAY,
    }
    await page.click(price_type_selector[article.price_type])

    # Standort (falls konfiguriert)
    zip_input = page.locator(selectors.AD_FORM_ZIP)
    if await zip_input.is_visible():
        current_zip = await zip_input.input_value()
        if not current_zip:
            logger.debug("PLZ-Feld leer, wird nicht automatisch befüllt")


async def _upload_images(page: Page, article: Article) -> None:
    """Lade Bilder hoch.

    Args:
        page: Playwright Page-Objekt.
        article: Artikel mit Bildpfaden.
    """
    logger.debug("Lade %d Bild(er) hoch", len(article.images))

    file_input = page.locator(selectors.IMAGE_UPLOAD_INPUT)
    file_paths = [str(img.path) for img in article.images]

    await file_input.set_input_files(file_paths)

    # Warten bis alle Bilder hochgeladen sind
    for i in range(len(article.images)):
        await page.wait_for_selector(
            f"{selectors.IMAGE_PREVIEW}:nth-child({i + 1})",
            timeout=selectors.UPLOAD_TIMEOUT * 1000,
        )

    logger.debug("Alle Bilder hochgeladen")
