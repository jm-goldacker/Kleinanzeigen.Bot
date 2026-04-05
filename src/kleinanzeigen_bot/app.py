"""FastAPI-Anwendung mit API-Routen und statischem Frontend."""

import logging
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from kleinanzeigen_bot.browser.login import login, LoginError
from kleinanzeigen_bot.browser.publisher import publish_article, PublishError
from kleinanzeigen_bot.browser.session import create_browser_session
from kleinanzeigen_bot.categories.mapper import CategoryMapper
from kleinanzeigen_bot.config import Settings, load_settings
from kleinanzeigen_bot.models import (
    Article,
    ArticleStatus,
    CategoryInfo,
    ImageFile,
    PriceType,
)
from kleinanzeigen_bot.pricing.estimator import estimate_price
from kleinanzeigen_bot.pricing.scraper import PriceScraper
from kleinanzeigen_bot.vision.analyzer import VisionAnalyzer, VisionAnalysisError

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "kleinanzeigen-bot-uploads"

app = FastAPI(title="Kleinanzeigen-Bot", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_settings: Settings | None = None


def _get_settings() -> Settings:
    """Lade Settings (lazy)."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


@app.get("/")
async def index() -> FileResponse:
    """Hauptseite ausliefern."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health_check() -> JSONResponse:
    """Prüfe ob alle Dienste verfügbar sind."""
    settings = _get_settings()
    analyzer = VisionAnalyzer(settings.ollama_host, settings.ollama_model)
    ollama_ok = await analyzer.check_availability()

    return JSONResponse({
        "status": "ok" if ollama_ok else "degraded",
        "ollama": {
            "available": ollama_ok,
            "host": settings.ollama_host,
            "model": settings.ollama_model,
        },
    })


@app.post("/api/analyze")
async def analyze_images(files: list[UploadFile]) -> JSONResponse:
    """Analysiere hochgeladene Bilder mit KI.

    Führt Bildanalyse, Kategorie-Mapping und Preisschätzung durch.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Mindestens ein Bild erforderlich")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximal 10 Bilder pro Artikel")

    settings = _get_settings()

    # Bilder temporär speichern
    upload_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / upload_id
    upload_path.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    for file in files:
        if not file.filename:
            continue
        file_path = upload_path / file.filename
        content = await file.read()
        file_path.write_bytes(content)
        saved_paths.append(file_path)

    if not saved_paths:
        raise HTTPException(status_code=400, detail="Keine gültigen Bilder hochgeladen")

    # 1. Vision-Analyse
    analyzer = VisionAnalyzer(settings.ollama_host, settings.ollama_model)
    try:
        vision_result = await analyzer.analyze_images(saved_paths)
    except VisionAnalysisError as e:
        raise HTTPException(status_code=500, detail=f"KI-Analyse fehlgeschlagen: {e}") from e

    # 2. Kategorie-Mapping
    mapper = CategoryMapper(settings.ollama_host, settings.ollama_model)
    category = await mapper.map_category(
        f"{vision_result.title} - {vision_result.description}"
    )

    # 3. Preisschätzung
    scraper = PriceScraper()
    try:
        price_sources = await scraper.search_prices(vision_result.search_keywords)
    finally:
        await scraper.close()

    price_estimate = estimate_price(price_sources)

    return JSONResponse({
        "upload_id": upload_id,
        "vision": {
            "title": vision_result.title,
            "description": vision_result.description,
            "search_keywords": vision_result.search_keywords,
            "condition": vision_result.condition,
        },
        "category": {
            "category_id": category.category_id,
            "category_path": category.category_path,
        },
        "price_estimate": {
            "suggested_price_cents": price_estimate.suggested_price_cents,
            "min_price_cents": price_estimate.min_price_cents,
            "max_price_cents": price_estimate.max_price_cents,
            "confidence": price_estimate.confidence,
            "source_count": len(price_estimate.sources),
        },
        "images": [f.name for f in saved_paths],
    })


@app.post("/api/publish")
async def publish(data: dict) -> JSONResponse:  # type: ignore[type-arg]
    """Veröffentliche einen Artikel auf Kleinanzeigen.de.

    Erwartet JSON mit:
    - upload_id: ID des Uploads
    - title: Anzeigentitel
    - description: Beschreibung
    - price_cents: Preis in Cent
    - price_type: FIXED, NEGOTIABLE oder GIVEAWAY
    - category_id: Kategorie-ID
    - category_path: Kategoriepfad
    """
    settings = _get_settings()

    upload_id = data.get("upload_id", "")
    upload_path = UPLOAD_DIR / upload_id

    if not upload_path.exists():
        raise HTTPException(status_code=404, detail="Upload nicht gefunden")

    # Bilder laden
    image_paths = sorted(upload_path.glob("*"))
    if not image_paths:
        raise HTTPException(status_code=404, detail="Keine Bilder im Upload gefunden")

    # Artikel erstellen
    article = Article(
        images=[ImageFile(path=p) for p in image_paths],
        title=data["title"],
        description=data["description"],
        price_cents=data["price_cents"],
        price_type=PriceType(data.get("price_type", "NEGOTIABLE")),
        category=CategoryInfo(
            category_id=data["category_id"],
            category_path=data.get("category_path", ""),
        ),
    )

    # Browser-Session starten und Artikel veröffentlichen
    try:
        async with create_browser_session(
            headless=settings.browser_headless,
            slow_mo=settings.browser_slow_mo,
        ) as page:
            await login(page, settings.kleinanzeigen_email, settings.kleinanzeigen_password)
            article = await publish_article(page, article)
    except LoginError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except PublishError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return JSONResponse({
        "status": article.status.value,
        "title": article.title,
    })


@app.get("/api/categories")
async def get_categories() -> JSONResponse:
    """Gib den Kategoriebaum zurück."""
    settings = _get_settings()
    mapper = CategoryMapper(settings.ollama_host, settings.ollama_model)
    return JSONResponse({"categories": mapper.get_all_categories()})
