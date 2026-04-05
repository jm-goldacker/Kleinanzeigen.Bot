"""Tests für die Datenmodelle."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from kleinanzeigen_bot.models import (
    Article,
    ArticleStatus,
    CategoryInfo,
    ImageFile,
    PriceEstimate,
    PriceSource,
    PriceType,
    VisionResult,
)


class TestImageFile:
    """Tests für das ImageFile-Modell."""

    def test_valid_image_path_creates_image_file(self, sample_image: Path) -> None:
        """Gültiger Bildpfad → ImageFile erstellt."""
        img = ImageFile(path=sample_image)
        assert img.path == sample_image

    def test_nonexistent_path_raises_validation_error(self) -> None:
        """Nicht existierender Pfad → ValidationError."""
        with pytest.raises(ValidationError, match="existiert nicht"):
            ImageFile(path=Path("/nonexistent/image.jpg"))

    def test_unsupported_format_raises_validation_error(self, tmp_path: Path) -> None:
        """Nicht unterstütztes Format → ValidationError."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not an image")
        with pytest.raises(ValidationError, match="Nicht unterstütztes Bildformat"):
            ImageFile(path=txt_file)

    def test_all_supported_formats_are_accepted(self, tmp_path: Path) -> None:
        """Alle unterstützten Formate werden akzeptiert."""
        from PIL import Image

        for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]:
            path = tmp_path / f"test{ext}"
            img = Image.new("RGB", (10, 10))
            img.save(path)
            image_file = ImageFile(path=path)
            assert image_file.path == path


class TestPriceSource:
    """Tests für PriceSource."""

    def test_valid_price_source_creates_model(self) -> None:
        """Gültige Preisquelle → Modell erstellt."""
        source = PriceSource(
            platform="ebay",
            title="iPhone 12",
            price_cents=35000,
        )
        assert source.platform == "ebay"
        assert source.price_cents == 35000

    def test_negative_price_raises_validation_error(self) -> None:
        """Negativer Preis → ValidationError."""
        with pytest.raises(ValidationError):
            PriceSource(platform="ebay", title="Test", price_cents=-100)


class TestPriceEstimate:
    """Tests für PriceEstimate."""

    def test_valid_estimate_creates_model(self) -> None:
        """Gültige Schätzung → Modell erstellt."""
        estimate = PriceEstimate(
            suggested_price_cents=30000,
            min_price_cents=25000,
            max_price_cents=35000,
            confidence="high",
        )
        assert estimate.suggested_price_cents == 30000
        assert estimate.confidence == "high"

    def test_empty_sources_by_default(self) -> None:
        """Leere Quellenliste als Default."""
        estimate = PriceEstimate(
            suggested_price_cents=100,
            min_price_cents=50,
            max_price_cents=150,
        )
        assert estimate.sources == []
        assert estimate.confidence == "none"


class TestVisionResult:
    """Tests für VisionResult."""

    def test_valid_vision_result_creates_model(self) -> None:
        """Gültiges Vision-Ergebnis → Modell erstellt."""
        result = VisionResult(
            title="Apple iPhone 12, 64GB, schwarz",
            description="Gut erhaltenes iPhone 12 in schwarz.",
            search_keywords=["iPhone 12", "64GB"],
            condition="gut",
        )
        assert result.title == "Apple iPhone 12, 64GB, schwarz"

    def test_title_exceeding_max_length_raises_validation_error(self) -> None:
        """Titel über 70 Zeichen → ValidationError."""
        with pytest.raises(ValidationError):
            VisionResult(
                title="A" * 71,
                description="Test",
                search_keywords=["test"],
                condition="gut",
            )

    def test_empty_keywords_raises_validation_error(self) -> None:
        """Leere Suchbegriffe → ValidationError."""
        with pytest.raises(ValidationError):
            VisionResult(
                title="Test",
                description="Test",
                search_keywords=[],
                condition="gut",
            )


class TestArticle:
    """Tests für das Article-Modell."""

    def test_valid_article_creates_model(self, sample_image: Path) -> None:
        """Gültiger Artikel → Modell erstellt."""
        article = Article(
            images=[ImageFile(path=sample_image)],
            title="Test Artikel",
            description="Beschreibung",
            price_cents=1500,
            category=CategoryInfo(category_id="161", category_path="Elektronik"),
        )
        assert article.title == "Test Artikel"
        assert article.status == ArticleStatus.DRAFT
        assert article.price_type == PriceType.NEGOTIABLE

    def test_price_euros_conversion(self, sample_image: Path) -> None:
        """Cent-zu-Euro-Konvertierung funktioniert."""
        article = Article(
            images=[ImageFile(path=sample_image)],
            title="Test",
            description="Test",
            price_cents=1599,
            category=CategoryInfo(category_id="1", category_path="Test"),
        )
        assert article.price_euros == 15.99

    def test_empty_images_raises_validation_error(self) -> None:
        """Keine Bilder → ValidationError."""
        with pytest.raises(ValidationError):
            Article(
                images=[],
                title="Test",
                description="Test",
                price_cents=100,
                category=CategoryInfo(category_id="1", category_path="Test"),
            )

    def test_too_many_images_raises_validation_error(self, tmp_path: Path) -> None:
        """Mehr als 10 Bilder → ValidationError."""
        from PIL import Image

        images = []
        for i in range(11):
            path = tmp_path / f"img_{i}.jpg"
            Image.new("RGB", (10, 10)).save(path)
            images.append(ImageFile(path=path))

        with pytest.raises(ValidationError):
            Article(
                images=images,
                title="Test",
                description="Test",
                price_cents=100,
                category=CategoryInfo(category_id="1", category_path="Test"),
            )
