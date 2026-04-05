"""Tests für die Konfiguration."""

import pytest
from pydantic import ValidationError

from kleinanzeigen_bot.config import Settings


class TestSettings:
    """Tests für die Settings-Klasse."""

    def test_settings_with_required_fields_creates_valid_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Pflichtfelder gesetzt → gültige Konfiguration."""
        monkeypatch.setenv("KLEINANZEIGEN_EMAIL", "test@example.com")
        monkeypatch.setenv("KLEINANZEIGEN_PASSWORD", "secret123")

        settings = Settings()

        assert settings.kleinanzeigen_email == "test@example.com"
        assert settings.kleinanzeigen_password == "secret123"

    def test_settings_without_email_raises_validation_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Fehlende E-Mail → ValidationError."""
        monkeypatch.delenv("KLEINANZEIGEN_EMAIL", raising=False)
        monkeypatch.setenv("KLEINANZEIGEN_PASSWORD", "secret123")

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_without_password_raises_validation_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Fehlendes Passwort → ValidationError."""
        monkeypatch.setenv("KLEINANZEIGEN_EMAIL", "test@example.com")
        monkeypatch.delenv("KLEINANZEIGEN_PASSWORD", raising=False)

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_defaults_are_applied(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default-Werte werden korrekt gesetzt."""
        monkeypatch.setenv("KLEINANZEIGEN_EMAIL", "test@example.com")
        monkeypatch.setenv("KLEINANZEIGEN_PASSWORD", "secret123")

        settings = Settings()

        assert settings.ollama_host == "http://localhost:11434"
        assert settings.ollama_model == "llava"
        assert settings.browser_headless is True
        assert settings.browser_slow_mo == 100
        assert settings.location_zip == ""
        assert settings.location_city == ""

    def test_settings_custom_values_override_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Benutzerdefinierte Werte überschreiben Defaults."""
        monkeypatch.setenv("KLEINANZEIGEN_EMAIL", "test@example.com")
        monkeypatch.setenv("KLEINANZEIGEN_PASSWORD", "secret123")
        monkeypatch.setenv("OLLAMA_MODEL", "llava:13b")
        monkeypatch.setenv("BROWSER_HEADLESS", "false")
        monkeypatch.setenv("LOCATION_ZIP", "80331")
        monkeypatch.setenv("LOCATION_CITY", "München")

        settings = Settings()

        assert settings.ollama_model == "llava:13b"
        assert settings.browser_headless is False
        assert settings.location_zip == "80331"
        assert settings.location_city == "München"
