"""Kleinanzeigen-Bot: KI-gestützter Bot zum automatischen Erstellen von Kleinanzeigen."""

import sys
from pathlib import Path


def get_base_path() -> Path:
    """Ermittle den Basispfad für Ressourcen (PyInstaller-kompatibel)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "kleinanzeigen_bot"  # type: ignore[attr-defined]
    return Path(__file__).parent
