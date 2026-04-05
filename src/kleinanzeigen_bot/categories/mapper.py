"""Kategorie-Zuordnung mithilfe der Ollama-KI."""

import json
import logging
from pathlib import Path
from typing import Any

from ollama import AsyncClient

from kleinanzeigen_bot.models import CategoryInfo
from kleinanzeigen_bot.vision.prompts import CATEGORIZE_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

TREE_PATH = Path(__file__).parent / "tree.json"

CategoryDict = dict[str, Any]


class CategoryMapper:
    """Ordnet Gegenstände Kleinanzeigen-Kategorien zu."""

    def __init__(self, host: str, model: str) -> None:
        """Initialisiere den Kategorie-Mapper.

        Args:
            host: Ollama API Host URL.
            model: Name des Modells.
        """
        self._client = AsyncClient(host=host)
        self._model = model
        self._tree: dict[str, list[CategoryDict]] = _load_category_tree()

    async def map_category(self, item_description: str) -> CategoryInfo:
        """Ordne einen Gegenstand einer Kategorie zu.

        Zweistufiger Prozess:
        1. Top-Level-Kategorie per KI bestimmen
        2. Unterkategorie per KI bestimmen (falls vorhanden)

        Args:
            item_description: Beschreibung des Gegenstands (Titel + Beschreibung).

        Returns:
            CategoryInfo mit ID und lesbarem Pfad.
        """
        categories = self._tree["categories"]

        # Schritt 1: Top-Level-Kategorie
        top_level = await self._ask_category(item_description, categories)

        if not top_level:
            logger.warning("Keine passende Kategorie gefunden, verwende 'Sonstiges'")
            return CategoryInfo(category_id="999", category_path="Sonstiges")

        # Schritt 2: Unterkategorie (falls vorhanden)
        if top_level.get("children"):
            sub_category = await self._ask_category(
                item_description,
                top_level["children"],
            )
            if sub_category:
                path = f"{top_level['name']} > {sub_category['name']}"
                return CategoryInfo(
                    category_id=str(sub_category["id"]),
                    category_path=path,
                )

        return CategoryInfo(
            category_id=str(top_level["id"]),
            category_path=str(top_level["name"]),
        )

    def get_all_categories(self) -> list[CategoryDict]:
        """Gib den gesamten Kategoriebaum zurück."""
        return self._tree["categories"]

    async def _ask_category(
        self,
        item_description: str,
        categories: list[CategoryDict],
    ) -> CategoryDict | None:
        """Frage die KI nach der passenden Kategorie.

        Args:
            item_description: Beschreibung des Gegenstands.
            categories: Liste verfügbarer Kategorien.

        Returns:
            Das gewählte Kategorie-Dict oder None.
        """
        category_list = "\n".join(
            f"{cat['id']}: {cat['name']}" for cat in categories
        )

        prompt = CATEGORIZE_PROMPT_TEMPLATE.format(
            item_description=item_description,
            categories=category_list,
        )

        response = await self._client.chat(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )

        answer: str = response["message"]["content"].strip()
        logger.debug("Kategorie-KI-Antwort: %s", answer)

        for cat in categories:
            cat_name = str(cat["name"])
            if str(cat["id"]) == answer or cat_name.lower() in answer.lower():
                return cat

        return None


def _load_category_tree() -> dict[str, list[CategoryDict]]:
    """Lade den Kategoriebaum aus der JSON-Datei.

    Returns:
        Kategoriebaum als Dictionary.

    Raises:
        FileNotFoundError: Wenn tree.json nicht gefunden wird.
    """
    with open(TREE_PATH, encoding="utf-8") as f:
        result: dict[str, list[CategoryDict]] = json.load(f)
        return result
