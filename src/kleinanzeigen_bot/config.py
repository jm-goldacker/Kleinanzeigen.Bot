"""Konfiguration aus .env-Datei laden."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Anwendungskonfiguration, geladen aus .env-Datei."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Kleinanzeigen.de Zugangsdaten
    kleinanzeigen_email: str = Field(description="E-Mail-Adresse für Kleinanzeigen.de")
    kleinanzeigen_password: str = Field(description="Passwort für Kleinanzeigen.de")

    # Ollama
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama API Host")
    ollama_model: str = Field(default="llava", description="Ollama Vision-Modell")

    # Browser
    browser_headless: bool = Field(default=True, description="Browser im Headless-Modus starten")
    browser_slow_mo: int = Field(
        default=100, description="Verzögerung zwischen Browser-Aktionen in ms"
    )

    # Standort
    location_zip: str = Field(default="", description="PLZ für Anzeigen")
    location_city: str = Field(default="", description="Stadt für Anzeigen")


def load_settings() -> Settings:
    """Lade Einstellungen aus .env-Datei.

    Returns:
        Settings-Objekt mit allen Konfigurationswerten.

    Raises:
        ValidationError: Wenn Pflichtfelder fehlen oder ungültig sind.
    """
    return Settings()  # type: ignore[call-arg]
