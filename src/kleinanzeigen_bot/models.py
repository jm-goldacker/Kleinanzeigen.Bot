"""Pydantic-Datenmodelle für Artikel, Preisschätzungen und Bilder."""

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PriceType(StrEnum):
    """Art der Preisangabe."""

    FIXED = "FIXED"
    NEGOTIABLE = "NEGOTIABLE"
    GIVEAWAY = "GIVEAWAY"


class ArticleStatus(StrEnum):
    """Status eines Artikels im Workflow."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class ImageFile(BaseModel):
    """Ein hochgeladenes Bild mit Validierung."""

    path: Path = Field(description="Pfad zur Bilddatei")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """Prüfe, ob die Datei existiert und ein unterstütztes Bildformat hat."""
        if not v.exists():
            raise ValueError(f"Bilddatei existiert nicht: {v}")
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
        if v.suffix.lower() not in allowed_extensions:
            raise ValueError(
                f"Nicht unterstütztes Bildformat: {v.suffix}. "
                f"Erlaubt: {', '.join(sorted(allowed_extensions))}"
            )
        return v


class PriceSource(BaseModel):
    """Herkunft eines Preisdatenpunkts."""

    platform: Literal["kleinanzeigen", "ebay"] = Field(description="Plattform")
    title: str = Field(description="Titel der Referenz-Anzeige")
    price_cents: int = Field(ge=0, description="Preis in Cent")
    url: str = Field(default="", description="URL der Anzeige")


class PriceEstimate(BaseModel):
    """Preisschätzung basierend auf Marktdaten."""

    suggested_price_cents: int = Field(ge=0, description="Vorgeschlagener Preis in Cent")
    min_price_cents: int = Field(ge=0, description="Unteres Ende der Preisspanne")
    max_price_cents: int = Field(ge=0, description="Oberes Ende der Preisspanne")
    sources: list[PriceSource] = Field(default_factory=list, description="Preisquellen")
    confidence: Literal["high", "medium", "low", "none"] = Field(
        default="none", description="Konfidenz der Schätzung"
    )


class CategoryInfo(BaseModel):
    """Kategorie-Information für eine Anzeige."""

    category_id: str = Field(description="Kleinanzeigen Kategorie-ID")
    category_path: str = Field(
        description="Lesbarer Kategoriepfad, z.B. 'Elektronik > Handys'"
    )


class VisionResult(BaseModel):
    """Ergebnis der KI-Bildanalyse."""

    title: str = Field(max_length=70, description="Anzeigentitel (max. 70 Zeichen)")
    description: str = Field(max_length=4000, description="Anzeigenbeschreibung")
    search_keywords: list[str] = Field(
        min_length=1, max_length=5, description="Suchbegriffe für Preisrecherche"
    )
    condition: Literal["neu", "sehr gut", "gut", "akzeptabel", "defekt"] = Field(
        description="Zustand des Gegenstands"
    )


class Article(BaseModel):
    """Ein vollständiger Artikel für Kleinanzeigen.de."""

    images: list[ImageFile] = Field(min_length=1, max_length=10, description="Bilder des Artikels")
    title: str = Field(max_length=70, description="Anzeigentitel")
    description: str = Field(max_length=4000, description="Anzeigenbeschreibung")
    price_cents: int = Field(ge=0, description="Preis in Cent")
    price_type: PriceType = Field(default=PriceType.NEGOTIABLE, description="Preisart")
    category: CategoryInfo = Field(description="Kategorie")
    price_estimate: PriceEstimate | None = Field(
        default=None, description="Preisschätzung (optional)"
    )
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT, description="Workflow-Status")

    @property
    def price_euros(self) -> float:
        """Preis in Euro."""
        return self.price_cents / 100
