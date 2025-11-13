"""Entropy-based solver using information theory."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TypeVar

from loldle.models.base import Character

T = TypeVar("T", bound=Character)


@dataclass
class EntropyScore:
    """Represents an entropy score for a character."""

    character: Character
    entropy: float
    expected_remaining: float

    def __lt__(self, other: EntropyScore) -> bool:
        """Compare by entropy (higher is better)."""
        return self.entropy < other.entropy


class EntropySolver:
    """
    Solver that uses information theory to find optimal guesses.

    The solver calculates the expected information gain (entropy) for each
    possible guess and recommends the guess that provides the most information.
    """

    @staticmethod
    def calculate_entropy(
        candidate: T,
        possible_targets: list[T],
        verbose: bool = False,
    ) -> float:
        """
        Calculate the expected information gain from guessing a character.

        The entropy is calculated as:
        H = -Σ p(pattern) * log2(p(pattern))

        where p(pattern) is the probability of seeing each comparison pattern
        if we guess the candidate.

        Args:
            candidate: Character to evaluate as a guess
            possible_targets: List of characters that could be the target
            verbose: If True, print detailed calculation info

        Returns:
            Entropy value (higher is better)
        """
        if not possible_targets:
            return 0.0

        # Count how many targets produce each comparison pattern
        pattern_counts: Counter[int] = Counter()

        for target in possible_targets:
            result = candidate.compare_with(target)
            pattern = result.to_base5()
            pattern_counts[pattern] += 1

        # Calculate entropy
        total = len(possible_targets)
        entropy = 0.0

        for pattern, count in pattern_counts.items():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)

        if verbose:
            print(f"\n{candidate.name}:")
            print(f"  Creates {len(pattern_counts)} different patterns")
            print(f"  Entropy: {entropy:.3f} bits")
            print(f"  Patterns distribution:")
            for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:5]:
                prob = count / total
                print(f"    Pattern {pattern:>5}: {count:>3} chars ({prob:>6.1%})")

        return entropy

    @staticmethod
    def calculate_expected_remaining(
        candidate: T,
        possible_targets: list[T],
    ) -> float:
        """
        Calculate expected number of remaining possibilities after guessing.

        Args:
            candidate: Character to evaluate
            possible_targets: List of possible targets

        Returns:
            Expected number of remaining characters
        """
        if not possible_targets:
            return 0.0

        pattern_counts: Counter[int] = Counter()

        for target in possible_targets:
            result = candidate.compare_with(target)
            pattern = result.to_base5()
            pattern_counts[pattern] += 1

        # Calculate weighted average of remaining possibilities
        total = len(possible_targets)
        expected = sum(count * count / total for count in pattern_counts.values())

        return expected

    @classmethod
    def find_best_guess(
        cls,
        candidates: list[T],
        possible_targets: list[T],
        verbose: bool = False,
    ) -> EntropyScore | None:
        """
        Find the best character to guess based on maximum entropy.

        Args:
            candidates: Characters to evaluate (usually all characters)
            possible_targets: Characters that could be the target
            verbose: If True, show entropy for all candidates

        Returns:
            EntropyScore for the best guess, or None if no candidates
        """
        if not candidates:
            return None

        if not possible_targets:
            return None

        # If only one possibility left, guess it
        if len(possible_targets) == 1:
            return EntropyScore(
                character=possible_targets[0],
                entropy=0.0,
                expected_remaining=0.0,
            )

        best_score: EntropyScore | None = None

        for candidate in candidates:
            entropy = cls.calculate_entropy(candidate, possible_targets, verbose)
            expected_remaining = cls.calculate_expected_remaining(candidate, possible_targets)

            score = EntropyScore(
                character=candidate,
                entropy=entropy,
                expected_remaining=expected_remaining,
            )

            if best_score is None or score.entropy > best_score.entropy:
                best_score = score

        return best_score

    @classmethod
    def get_top_guesses(
        cls,
        candidates: list[T],
        possible_targets: list[T],
        n: int = 5,
        verbose: bool = False,
    ) -> list[EntropyScore]:
        """
        Get the top N best guesses ranked by entropy.

        Args:
            candidates: Characters to evaluate
            possible_targets: Characters that could be the target
            n: Number of top guesses to return
            verbose: If True, show calculation details

        Returns:
            List of top N EntropyScores, sorted by entropy (descending)
        """
        if not candidates or not possible_targets:
            return []

        scores = []
        for candidate in candidates:
            entropy = cls.calculate_entropy(candidate, possible_targets, verbose)
            expected_remaining = cls.calculate_expected_remaining(candidate, possible_targets)

            scores.append(
                EntropyScore(
                    character=candidate,
                    entropy=entropy,
                    expected_remaining=expected_remaining,
                )
            )

        # Sort by entropy (descending) and take top N
        scores.sort(key=lambda s: s.entropy, reverse=True)
        return scores[:n]


def get_optimal_first_guess(all_characters: list[T]) -> T | None:
    """
    Calculate the optimal first guess for a fresh game.

    This can be precomputed since it's the same for all games.

    Args:
        all_characters: All characters in the game

    Returns:
        Character with highest entropy for the first guess
    """
    solver = EntropySolver()
    best = solver.find_best_guess(all_characters, all_characters)
    return best.character if best else None
