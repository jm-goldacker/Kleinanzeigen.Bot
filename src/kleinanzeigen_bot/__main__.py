"""Einstiegspunkt: Startet den Kleinanzeigen-Bot Webserver."""

import logging
import sys
import webbrowser
from threading import Timer

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

HOST = "127.0.0.1"
PORT = 8000


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

    # Browser nach kurzem Delay öffnen
    Timer(1.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()

    from kleinanzeigen_bot.app import app

    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
