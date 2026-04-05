# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/)
und folgt [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added
- Modellauswahl im Frontend: Dropdown im Header zum Wechseln zwischen Ollama-Modellen (z.B. qwen2.5, gemma3)
- API-Endpunkt `GET /api/models` zum Auflisten aller verfügbaren Ollama-Modelle
- Initiale Projektstruktur mit FastAPI-Backend und Vanilla-JS-Frontend
- KI-Bildanalyse mit Ollama Vision-Modell (LLaVA)
- Automatische Preisschätzung durch Scraping von Kleinanzeigen.de und eBay
- Kategorie-Mapping mit KI-gestütztem Fuzzy-Matching
- Browser-Automatisierung mit Playwright für Kleinanzeigen.de
- Web-UI mit Drag & Drop Bild-Upload
- Batch-Verarbeitung für mehrere Artikel
- Artikel-Editor zum Bearbeiten vor Veröffentlichung
- Konfiguration über .env-Datei (pydantic-settings)
- Unit-Tests für Models, Config, Parser und Estimator
