"""Einstiegspunkt: Startet den Kleinanzeigen-Bot Webserver."""

import logging
import sys

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Starte den FastAPI-Webserver."""
    logger.info("Starte Kleinanzeigen-Bot...")

    try:
        from kleinanzeigen_bot.config import load_settings
        load_settings()
        logger.info("Konfiguration geladen")
    except Exception as e:
        logger.error("Konfigurationsfehler: %s", e)
        logger.error("Bitte .env-Datei erstellen (siehe .env.example)")
        sys.exit(1)

    uvicorn.run(
        "kleinanzeigen_bot.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
