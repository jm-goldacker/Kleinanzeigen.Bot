# Prompt-Log

Protokoll aller Claude-Interaktionen, die zu Code- oder Dokumentationsänderungen geführt haben.

## [2026-04-05 17:30] – Initiales Projekt aufsetzen

**Prompt:**
Ich möchte eine App erstellen. Dort möchte ich Bilder von Gegenständen hochladen. Eine lokale KI soll den Inhalt der
Bilder erkennen, den Preis schätzen, eine Beschreibung erstellen und nach Bestätigung des Nutzers den Artikel bei
Kleinanzeigen.de hochladen. Die Zugangsdaten dafür möchte ich lokal einstellen können.

Anforderungen:
- Web-App mit Browser-Automatisierung für Veröffentlichung
- Mehrere Bilder pro Artikel
- Preisschätzung anhand Kleinanzeigen.de und eBay
- Automatischer Kategorie-Vorschlag
- Nutzer kann alles vor Upload bearbeiten
- Batch-Verarbeitung (mehrere Artikel auf einmal)
- Keine Datenhaltung
- Lokale Zugangsdaten (.env)

**Ergebnis:**
- Vollständige Projektstruktur erstellt (Python/FastAPI + Vanilla JS)
- `src/kleinanzeigen_bot/config.py` – Konfiguration via .env
- `src/kleinanzeigen_bot/models.py` – Pydantic-Datenmodelle
- `src/kleinanzeigen_bot/vision/` – Ollama Vision-Integration
- `src/kleinanzeigen_bot/pricing/` – Preisrecherche und -schätzung
- `src/kleinanzeigen_bot/categories/` – Kategorie-Mapping
- `src/kleinanzeigen_bot/browser/` – Playwright Browser-Automatisierung
- `src/kleinanzeigen_bot/app.py` – FastAPI-Routen
- `src/kleinanzeigen_bot/static/` – Web-Frontend (HTML/CSS/JS)
- Tests für Config, Models, Vision-Parser, Pricing-Parser, Estimator
- `README.md`, `CHANGELOG.md`, `.env.example`, `.gitignore`

**Commits:**
- *(noch nicht committed)*

**Anmerkungen:**
- Python 3.12+ muss noch installiert werden
- Kategoriebaum in tree.json ist ein vereinfachtes Beispiel, sollte für Produktion von Kleinanzeigen.de gescrapt werden
- CSS-Selektoren in selectors.py müssen gegen die aktuelle Kleinanzeigen.de-Seite verifiziert werden
- Browser-Tests (E2E) sind nicht automatisiert, da sie echte Login-Daten benötigen
