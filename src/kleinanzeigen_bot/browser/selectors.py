"""CSS-Selektoren und XPath-Ausdrücke für Kleinanzeigen.de.

Alle Selektoren als benannte Konstanten, damit Änderungen an der
Seitenstruktur nur an einer Stelle angepasst werden müssen.
"""

# Login-Seite
LOGIN_URL = "https://www.kleinanzeigen.de/m-einloggen.html"
LOGIN_EMAIL_INPUT = "#login-email"
LOGIN_PASSWORD_INPUT = "#login-password"
LOGIN_SUBMIT_BUTTON = "#login-submit"
LOGIN_SUCCESS_INDICATOR = '[data-testid="user-menu"]'

# Cookie-Banner
COOKIE_ACCEPT_BUTTON = "#gdpr-banner-accept"

# Anzeige aufgeben
POST_AD_URL = "https://www.kleinanzeigen.de/m-meine-anzeigen.html"
NEW_AD_BUTTON = 'a[href*="anzeige-aufgeben"]'

# Anzeigen-Formular
AD_FORM_TITLE = "#postad-title"
AD_FORM_DESCRIPTION = "#pstad-descrptn"
AD_FORM_PRICE = "#postad-price"
AD_FORM_PRICE_TYPE_FIXED = 'input[value="FIXED"]'
AD_FORM_PRICE_TYPE_NEGOTIABLE = 'input[value="NEGOTIABLE"]'
AD_FORM_PRICE_TYPE_GIVEAWAY = 'input[value="GIVE_AWAY"]'
AD_FORM_ZIP = "#postad-zip"
AD_FORM_CITY = "#postad-city"

# Kategorie-Auswahl
CATEGORY_INPUT = "#postad-category-path"
CATEGORY_SUGGESTION = ".category-suggestion"

# Bild-Upload
IMAGE_UPLOAD_INPUT = 'input[type="file"][accept*="image"]'
IMAGE_PREVIEW = ".image-preview"

# Absenden
SUBMIT_AD_BUTTON = "#postad-submit"
AD_SUCCESS_INDICATOR = ".post-ad-success"

# Wartezeiten (Sekunden)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_TIMEOUT = 10
UPLOAD_TIMEOUT = 60
