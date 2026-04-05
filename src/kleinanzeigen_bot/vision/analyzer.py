"""Bildanalyse mit Ollama Vision-Modell."""

import base64
import json
import logging
from pathlib import Path

from ollama import AsyncClient

from kleinanzeigen_bot.models import VisionResult
from kleinanzeigen_bot.vision.prompts import ANALYZE_IMAGE_PROMPT

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Analysiert Bilder mithilfe eines lokalen Ollama Vision-Modells."""

    def __init__(self, host: str, model: str) -> None:
        """Initialisiere den Vision-Analyzer.

        Args:
            host: Ollama API Host URL.
            model: Name des Vision-Modells (z.B. 'llava').
        """
        self._client = AsyncClient(host=host)
        self._model = model

    async def analyze_images(self, image_paths: list[Path]) -> VisionResult:
        """Analysiere Bilder und erstelle Titel, Beschreibung und Suchbegriffe.

        Args:
            image_paths: Liste von Pfaden zu den Bilddateien.

        Returns:
            VisionResult mit Titel, Beschreibung, Suchbegriffen und Zustand.

        Raises:
            VisionAnalysisError: Bei Fehlern in der KI-Analyse.
        """
        images_b64 = [_encode_image(path) for path in image_paths]

        logger.info(
            "Analysiere %d Bild(er) mit Modell '%s'", len(image_paths), self._model
        )

        response = await self._client.chat(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": ANALYZE_IMAGE_PROMPT,
                    "images": images_b64,
                }
            ],
        )

        raw_content = response["message"]["content"]
        logger.debug("Ollama-Antwort: %s", raw_content)

        return _parse_vision_response(raw_content)

    async def check_availability(self) -> bool:
        """Prüfe, ob Ollama erreichbar ist und das Modell verfügbar ist.

        Returns:
            True wenn Ollama und das Modell bereit sind.
        """
        try:
            models = await self._client.list()
            available = [m["model"] for m in models.get("models", [])]
            if self._model in available or any(
                m.startswith(self._model) for m in available
            ):
                return True
            logger.warning(
                "Modell '%s' nicht gefunden. Verfügbar: %s",
                self._model,
                ", ".join(available),
            )
            return False
        except Exception:
            logger.exception("Ollama nicht erreichbar unter Host")
            return False

    async def list_models(self) -> list[str]:
        """Liste alle verfügbaren Ollama-Modelle auf.

        Returns:
            Liste von Modellnamen.
        """
        try:
            models = await self._client.list()
            return [m["model"] for m in models.get("models", [])]
        except Exception:
            logger.exception("Ollama nicht erreichbar")
            return []


class VisionAnalysisError(Exception):
    """Fehler bei der KI-Bildanalyse."""


def _encode_image(path: Path) -> str:
    """Bild als Base64-String kodieren."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _parse_vision_response(raw: str) -> VisionResult:
    """Parse die JSON-Antwort des Vision-Modells.

    Args:
        raw: Rohe Textantwort von Ollama.

    Returns:
        Validiertes VisionResult.

    Raises:
        VisionAnalysisError: Bei ungültigem JSON oder fehlenden Feldern.
    """
    # JSON aus der Antwort extrahieren (kann in Markdown-Codeblöcken stecken)
    cleaned = raw.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise VisionAnalysisError(
            f"KI-Antwort ist kein gültiges JSON: {e}\nAntwort: {raw}"
        ) from e

    # KI liefert manchmal zu viele Keywords – auf Maximum kürzen
    if "search_keywords" in data and isinstance(data["search_keywords"], list):
        data["search_keywords"] = data["search_keywords"][:5]

    try:
        return VisionResult(**data)
    except Exception as e:
        raise VisionAnalysisError(
            f"KI-Antwort hat ungültiges Format: {e}\nDaten: {data}"
        ) from e
