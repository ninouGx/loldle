"""Base game engine for guessing games."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from loldle.models.base import Character, ComparisonResult

T = TypeVar("T", bound=Character)


@dataclass
class GameState(Generic[T]):
    """Represents the current state of a game."""

    target_character: T | None = None
    all_characters: list[T] = field(default_factory=list)
    tested_characters: list[T] = field(default_factory=list)
    comparison_results: list[ComparisonResult] = field(default_factory=list)
    possible_characters: list[T] = field(default_factory=list)
    is_won: bool = False
    num_guesses: int = 0

    def __post_init__(self) -> None:
        """Initialize possible characters if not set."""
        if not self.possible_characters and self.all_characters:
            self.possible_characters = self.all_characters.copy()


class BaseGame(ABC, Generic[T]):
    """
    Abstract base class for guessing games.

    Implements the core game logic while allowing subclasses to define
    character-specific behavior.
    """

    def __init__(self, characters: list[T]) -> None:
        """
        Initialize the game.

        Args:
            characters: List of all possible characters in the game
        """
        if not characters:
            raise ValueError("Cannot create game with empty character list")

        self.characters = characters
        self.state = GameState(all_characters=characters)

    def start_new_game(self, target: T | None = None) -> None:
        """
        Start a new game.

        Args:
            target: Specific character to guess. If None, chooses randomly.
        """
        if target is None:
            target = random.choice(self.characters)
        elif target not in self.characters:
            raise ValueError(f"Target character {target.name} not in character list")

        self.state = GameState(
            target_character=target,
            all_characters=self.characters,
            possible_characters=self.characters.copy(),
        )

    def make_guess(self, character: T) -> ComparisonResult:
        """
        Make a guess and update game state.

        Args:
            character: Character being guessed

        Returns:
            ComparisonResult showing how the guess compares to the target

        Raises:
            ValueError: If game hasn't started or character already guessed
        """
        if self.state.target_character is None:
            raise ValueError("Game not started. Call start_new_game() first.")

        if character in self.state.tested_characters:
            raise ValueError(f"Character {character.name} already guessed")

        # Compare with target
        result = character.compare_with(self.state.target_character)

        # Update state
        self.state.tested_characters.append(character)
        self.state.comparison_results.append(result)
        self.state.num_guesses += 1

        # Check if won
        if result.is_perfect_match():
            self.state.is_won = True

        # Update possible characters
        self.state.possible_characters = self._filter_compatible_characters(
            result, character
        )

        return result

    def _filter_compatible_characters(
        self, result: ComparisonResult, guessed_character: T
    ) -> list[T]:
        """
        Filter characters that are compatible with the given guess result.

        A character is compatible if comparing the guessed character with it
        produces a result that matches the given result pattern.

        Args:
            result: The result we got from guessing
            guessed_character: The character that was guessed

        Returns:
            List of characters that could still be the target
        """
        compatible = []

        for char in self.state.possible_characters:
            # Skip the character we just guessed
            if char == guessed_character:
                continue

            # Compare the guessed character with this potential target
            hypothetical_result = guessed_character.compare_with(char)

            # Check if the comparison matches what we observed
            if self._results_match(result, hypothetical_result):
                compatible.append(char)

        return compatible

    def _results_match(
        self, result1: ComparisonResult, result2: ComparisonResult
    ) -> bool:
        """
        Check if two comparison results match.

        Results match if each category has the same match type, or if
        result1 has PARTIAL and result2 has EXACT (partial is compatible with exact).

        Args:
            result1: First result (observed)
            result2: Second result (hypothetical)

        Returns:
            True if results are compatible
        """
        from loldle.utils.constants import MatchType

        if len(result1.matches) != len(result2.matches):
            return False

        for m1, m2 in zip(result1.matches, result2.matches):
            # Exact match required
            if m1 == m2:
                continue
            # Partial in observed allows exact in hypothetical
            elif m1 == MatchType.PARTIAL and m2 == MatchType.EXACT:
                continue
            else:
                return False

        return True

    def get_untested_characters(self) -> list[T]:
        """Get list of characters that haven't been guessed yet."""
        return [c for c in self.characters if c not in self.state.tested_characters]

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.state.is_won or len(self.state.possible_characters) == 0

    def get_game_summary(self) -> dict:
        """
        Get a summary of the current game state.

        Returns:
            Dictionary with game statistics
        """
        return {
            "num_guesses": self.state.num_guesses,
            "is_won": self.state.is_won,
            "target": self.state.target_character.name if self.state.target_character else None,
            "possible_remaining": len(self.state.possible_characters),
            "tested_characters": [c.name for c in self.state.tested_characters],
        }

    @abstractmethod
    def get_game_name(self) -> str:
        """Get the name of this game variant."""
        pass

    @abstractmethod
    def get_category_headers(self) -> str:
        """Get emoji/text headers for the comparison categories."""
        pass
