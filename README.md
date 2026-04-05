# Kleinanzeigen-Bot

AI-powered bot for automatically creating classified ads. Upload photos, let the AI identify the item, estimate the price, and publish the listing on Kleinanzeigen.de.

## Features

- **AI Image Recognition**: Local image analysis with Ollama (LLaVA) – no cloud, no costs
- **Automatic Price Estimation**: Based on current listings from Kleinanzeigen.de and eBay
- **Category Suggestion**: AI suggests a matching Kleinanzeigen category
- **Batch Processing**: Process multiple items at once
- **Edit Before Publishing**: Adjust title, description, price, and category before publishing
- **Browser Automation**: Listings are automatically created via Playwright

## Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) with a vision model (e.g. `llava`)
- Google Chrome (for browser automation)

## Setup

### 1. Install Ollama and download a model

```bash
# Install Ollama: https://ollama.com/download
# Download a vision model:
ollama pull llava
```

### 2. Set up the project

```bash
# Clone the repository
git clone <repo-url>
cd kleinanzeigen-bot

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### 3. Configuration

```bash
# Create .env file from template
cp .env.example .env
```

Edit `.env` and enter your credentials:

```env
KLEINANZEIGEN_EMAIL=your-email@example.com
KLEINANZEIGEN_PASSWORD=your-password
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llava
LOCATION_ZIP=12345
LOCATION_CITY=Berlin
```

## Usage

### Option A: Download the executable

Download the latest release for your platform from the [Releases](https://github.com/jm-goldacker/Kleinanzeigen.Bot/releases) page. Place a `.env` file next to the executable and run it. The app opens automatically in your browser.

### Option B: Run from source

```bash
python -m kleinanzeigen_bot
```

The web app is then available at `http://127.0.0.1:8000`.

### Workflow

1. **Upload images**: Upload images via drag & drop or file selection
2. **AI analysis**: The AI identifies the item, creates a title and description
3. **Review price**: Review and adjust the price suggestion based on market data
4. **Edit**: All fields can be edited before publishing
5. **Publish**: The listing is automatically created on Kleinanzeigen.de

## Configuration

| Variable | Description | Default |
|---|---|---|
| `KLEINANZEIGEN_EMAIL` | Email for Kleinanzeigen.de | *Required* |
| `KLEINANZEIGEN_PASSWORD` | Password for Kleinanzeigen.de | *Required* |
| `OLLAMA_HOST` | Ollama API address | `http://localhost:11434` |
| `OLLAMA_MODEL` | Vision model | `llava` |
| `BROWSER_HEADLESS` | Run browser without window | `true` |
| `BROWSER_SLOW_MO` | Delay in ms | `100` |
| `LOCATION_ZIP` | Zip code for listings | – |
| `LOCATION_CITY` | City for listings | – |

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov

# Linting
ruff check src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
src/kleinanzeigen_bot/
├── app.py              # FastAPI web app
├── config.py           # Configuration (.env)
├── models.py           # Data models
├── vision/             # AI image analysis (Ollama)
├── pricing/            # Price estimation (scraping)
├── categories/         # Category mapping
├── browser/            # Browser automation (Playwright)
└── static/             # Web frontend (HTML/CSS/JS)
```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE.md).
