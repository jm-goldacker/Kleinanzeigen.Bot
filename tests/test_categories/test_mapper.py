"""Tests für den Kategorie-Mapper."""

from kleinanzeigen_bot.categories.mapper import _load_category_tree


class TestLoadCategoryTree:
    """Tests für das Laden des Kategoriebaums."""

    def test_load_tree_returns_categories(self) -> None:
        """Kategoriebaum wird geladen und enthält Einträge."""
        tree = _load_category_tree()
        assert "categories" in tree
        assert len(tree["categories"]) > 0

    def test_load_tree_categories_have_required_fields(self) -> None:
        """Jede Kategorie hat id, name und children."""
        tree = _load_category_tree()
        for cat in tree["categories"]:
            assert "id" in cat
            assert "name" in cat
            assert "children" in cat

    def test_load_tree_contains_elektronik(self) -> None:
        """Kategoriebaum enthält 'Elektronik'."""
        tree = _load_category_tree()
        names = [cat["name"] for cat in tree["categories"]]
        assert "Elektronik" in names

    def test_load_tree_elektronik_has_children(self) -> None:
        """Elektronik-Kategorie hat Unterkategorien."""
        tree = _load_category_tree()
        elektronik = next(
            cat for cat in tree["categories"] if cat["name"] == "Elektronik"
        )
        assert len(elektronik["children"]) > 0
