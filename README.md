# Kleinanzeigen-Bot

KI-gestützter Bot zum automatischen Erstellen von Kleinanzeigen. Bilder hochladen, KI erkennt den Gegenstand, schätzt den Preis und veröffentlicht die Anzeige auf Kleinanzeigen.de.

## Features

- **KI-Bilderkennung**: Lokale Bildanalyse mit Ollama (LLaVA) – keine Cloud, keine Kosten
- **Automatische Preisschätzung**: Basierend auf aktuellen Angeboten von Kleinanzeigen.de und eBay
- **Kategorie-Vorschlag**: KI schlägt passende Kleinanzeigen-Kategorie vor
- **Batch-Verarbeitung**: Mehrere Artikel auf einmal verarbeiten
- **Bearbeitung vor Upload**: Titel, Beschreibung, Preis und Kategorie vor Veröffentlichung anpassen
- **Browser-Automatisierung**: Anzeigen werden automatisch über Playwright eingestellt

## Voraussetzungen

- Python 3.12+
- [Ollama](https://ollama.com/) mit einem Vision-Modell (z.B. `llava`)
- Google Chrome (für Browser-Automatisierung)

## Setup

### 1. Ollama installieren und Modell herunterladen

```bash
# Ollama installieren: https://ollama.com/download
# Vision-Modell herunterladen:
ollama pull llava
```

### 2. Projekt einrichten

```bash
# Repository klonen
git clone <repo-url>
cd kleinanzeigen-bot

# Virtuelle Umgebung erstellen
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Abhängigkeiten installieren
pip install -e ".[dev]"

# Playwright-Browser installieren
playwright install chromium
```

### 3. Konfiguration

```bash
# .env-Datei aus Vorlage erstellen
cp .env.example .env
```

`.env` bearbeiten und Zugangsdaten eintragen:

```env
KLEINANZEIGEN_EMAIL=deine-email@example.com
KLEINANZEIGEN_PASSWORD=dein-passwort
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llava
LOCATION_ZIP=12345
LOCATION_CITY=Berlin
```

## Verwendung

### App starten

```bash
python -m kleinanzeigen_bot
```

Die Web-App ist dann unter `http://127.0.0.1:8000` erreichbar.

### Workflow

1. **Bilder hochladen**: Bilder per Drag & Drop oder Dateiauswahl hochladen
2. **KI-Analyse**: Die KI erkennt den Gegenstand, erstellt Titel und Beschreibung
3. **Preis prüfen**: Preisvorschlag basierend auf Marktdaten prüfen/anpassen
4. **Bearbeiten**: Alle Felder können vor der Veröffentlichung bearbeitet werden
5. **Veröffentlichen**: Anzeige wird automatisch auf Kleinanzeigen.de eingestellt

## Konfiguration

| Variable | Beschreibung | Default |
|---|---|---|
| `KLEINANZEIGEN_EMAIL` | E-Mail für Kleinanzeigen.de | *Pflicht* |
| `KLEINANZEIGEN_PASSWORD` | Passwort für Kleinanzeigen.de | *Pflicht* |
| `OLLAMA_HOST` | Ollama API-Adresse | `http://localhost:11434` |
| `OLLAMA_MODEL` | Vision-Modell | `llava` |
| `BROWSER_HEADLESS` | Browser ohne Fenster | `true` |
| `BROWSER_SLOW_MO` | Verzögerung in ms | `100` |
| `LOCATION_ZIP` | PLZ für Anzeigen | – |
| `LOCATION_CITY` | Stadt für Anzeigen | – |

## Entwicklung

```bash
# Tests ausführen
pytest

# Tests mit Coverage
pytest --cov

# Linting
ruff check src/ tests/

# Typ-Prüfung
mypy src/
```

## Projektstruktur

```
src/kleinanzeigen_bot/
├── app.py              # FastAPI Web-App
├── config.py           # Konfiguration (.env)
├── models.py           # Datenmodelle
├── vision/             # KI-Bildanalyse (Ollama)
├── pricing/            # Preisschätzung (Scraping)
├── categories/         # Kategorie-Mapping
├── browser/            # Browser-Automatisierung (Playwright)
└── static/             # Web-Frontend (HTML/CSS/JS)
```
