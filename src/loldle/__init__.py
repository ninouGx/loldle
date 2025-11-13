"""
Loldle Solver - A CLI tool for playing and solving Loldle and its variants.

This package provides a complete framework for playing guessing games like Loldle
(League of Legends), Pokedle (Pokemon), and potentially other variants,
with AI-powered solving using information theory and entropy calculations.
"""

__version__ = "2.0.0"
__author__ = "ninouGx"

from loldle.models.base import Character, ComparisonResult, MatchType
from loldle.games.base import BaseGame

__all__ = [
    "__version__",
    "__author__",
    "Character",
    "ComparisonResult",
    "MatchType",
    "BaseGame",
]
