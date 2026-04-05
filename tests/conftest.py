"""Gemeinsame Test-Fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Pfad zum Fixtures-Verzeichnis."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Erstelle ein minimales Test-Bild (100x100 JPEG)."""
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    path = tmp_path / "test_image.jpg"
    img.save(path)
    return path


@pytest.fixture
def sample_images(tmp_path: Path) -> list[Path]:
    """Erstelle mehrere Test-Bilder."""
    from PIL import Image

    paths = []
    for i in range(3):
        img = Image.new("RGB", (100, 100), color=("red", "green", "blue")[i])
        path = tmp_path / f"test_image_{i}.jpg"
        img.save(path)
        paths.append(path)
    return paths
