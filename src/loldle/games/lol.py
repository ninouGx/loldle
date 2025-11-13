"""League of Legends Loldle game implementation."""

from __future__ import annotations

from loldle.data.loader import load_champions_from_csv
from loldle.games.base import BaseGame
from loldle.models.lol import Champion, get_category_icons


class LoldleGame(BaseGame[Champion]):
    """Loldle game for League of Legends champions."""

    def __init__(self, champions: list[Champion] | None = None) -> None:
        """
        Initialize Loldle game.

        Args:
            champions: List of champions. If None, loads from default CSV.
        """
        if champions is None:
            champions = load_champions_from_csv()

        super().__init__(champions)

    def get_game_name(self) -> str:
        """Get the name of this game variant."""
        return "Loldle (League of Legends)"

    def get_category_headers(self) -> str:
        """Get emoji headers for the comparison categories."""
        return get_category_icons()

    @classmethod
    def create_from_csv(cls, csv_path: str | None = None) -> LoldleGame:
        """
        Create a Loldle game from a CSV file.

        Args:
            csv_path: Path to CSV file. If None, uses default.

        Returns:
            LoldleGame instance
        """
        champions = load_champions_from_csv(csv_path)
        return cls(champions)
