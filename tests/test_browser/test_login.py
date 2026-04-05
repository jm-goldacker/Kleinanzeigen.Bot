"""Tests für den Login-Flow."""

from kleinanzeigen_bot.browser.selectors import (
    LOGIN_EMAIL_INPUT,
    LOGIN_PASSWORD_INPUT,
    LOGIN_SUBMIT_BUTTON,
    LOGIN_URL,
)


class TestSelectors:
    """Tests für die Selektor-Konstanten."""

    def test_login_url_is_https(self) -> None:
        """Login-URL verwendet HTTPS."""
        assert LOGIN_URL.startswith("https://")

    def test_login_selectors_are_non_empty(self) -> None:
        """Login-Selektoren sind nicht leer."""
        assert LOGIN_EMAIL_INPUT
        assert LOGIN_PASSWORD_INPUT
        assert LOGIN_SUBMIT_BUTTON
