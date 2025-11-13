"""Base models for characters and game logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from loldle.utils.constants import MatchType


@dataclass
class Character(ABC):
    """Abstract base class for game characters."""

    name: str

    @abstractmethod
    def get_comparable_attributes(self) -> list[Any]:
        """
        Get list of attributes to compare in order.

        Returns:
            List of attribute values for comparison
        """
        pass

    @abstractmethod
    def compare_with(self, other: Character) -> ComparisonResult:
        """
        Compare this character with another.

        Args:
            other: Character to compare against

        Returns:
            ComparisonResult containing match types for each attribute
        """
        pass

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Character):
            return False
        return self.name == other.name


@dataclass
class ComparisonResult:
    """Result of comparing two characters."""

    matches: list[MatchType]
    tested_character: str
    target_character: str | None = None

    def is_perfect_match(self) -> bool:
        """Check if all attributes match exactly."""
        return all(m == MatchType.EXACT for m in self.matches)

    def to_base5(self) -> int:
        """Convert comparison result to base-5 integer representation."""
        return int("".join(str(int(m)) for m in self.matches), 5)

    @classmethod
    def from_base5(cls, value: int, num_categories: int, tested_char: str) -> ComparisonResult:
        """
        Create ComparisonResult from base-5 integer.

        Args:
            value: Base-5 integer representation
            num_categories: Number of categories being compared
            tested_char: Name of tested character

        Returns:
            ComparisonResult instance
        """
        matches = []
        for _ in range(num_categories):
            matches.insert(0, MatchType(value % 5))
            value //= 5
        return cls(matches=matches, tested_character=tested_char)

    @classmethod
    def from_emoji_string(cls, emoji_str: str, tested_char: str) -> ComparisonResult:
        """
        Create ComparisonResult from emoji string.

        Args:
            emoji_str: String of emoji characters representing matches
            tested_char: Name of tested character

        Returns:
            ComparisonResult instance
        """
        from loldle.utils.constants import EMOJI_TO_MATCH

        matches = []
        # Filter out emoji variation selectors (️)
        cleaned = "".join(c for c in emoji_str if c != "️")

        for char in cleaned:
            if char in EMOJI_TO_MATCH:
                matches.append(EMOJI_TO_MATCH[char])
            else:
                # Unknown emoji, treat as wrong
                matches.append(MatchType.WRONG)

        return cls(matches=matches, tested_character=tested_char)

    @classmethod
    def from_number_string(cls, num_str: str, tested_char: str) -> ComparisonResult:
        """
        Create ComparisonResult from number string (0-4 for each category).

        Args:
            num_str: String of numbers 0-4
            tested_char: Name of tested character

        Returns:
            ComparisonResult instance
        """
        matches = [MatchType(int(c)) for c in num_str if c.isdigit() and int(c) <= 4]
        return cls(matches=matches, tested_character=tested_char)

    def to_emoji_string(self) -> str:
        """Convert to emoji representation."""
        from loldle.utils.constants import MATCH_EMOJIS

        return "".join(MATCH_EMOJIS[m] for m in self.matches)

    def to_number_string(self) -> str:
        """Convert to number representation (0-4)."""
        return "".join(str(int(m)) for m in self.matches)


def compare_lists(list1: list[str], list2: list[str]) -> MatchType:
    """
    Compare two lists of values (for multi-value attributes like positions, species).

    Args:
        list1: First list to compare
        list2: Second list to compare

    Returns:
        EXACT if lists match exactly (same elements),
        PARTIAL if there's any overlap,
        WRONG if no overlap
    """
    set1 = set(list1)
    set2 = set(list2)

    if set1 == set2:
        return MatchType.EXACT
    elif set1 & set2:  # Intersection exists
        return MatchType.PARTIAL
    else:
        return MatchType.WRONG


def compare_values(val1: Any, val2: Any) -> MatchType:
    """
    Compare two single values.

    Args:
        val1: First value
        val2: Second value

    Returns:
        EXACT if values match, WRONG otherwise
    """
    return MatchType.EXACT if val1 == val2 else MatchType.WRONG


def compare_numbers(num1: int | float, num2: int | float) -> MatchType:
    """
    Compare two numeric values with ordering.

    Args:
        num1: First number (tested)
        num2: Second number (target)

    Returns:
        EXACT if equal,
        AFTER if num1 < num2 (target is later/higher),
        BEFORE if num1 > num2 (target is earlier/lower)
    """
    if num1 == num2:
        return MatchType.EXACT
    elif num1 < num2:
        return MatchType.AFTER
    else:
        return MatchType.BEFORE
