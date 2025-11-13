"""Constants and enums used throughout the application."""

from __future__ import annotations

from enum import IntEnum, auto
from pathlib import Path


class MatchType(IntEnum):
    """Types of matches for character attributes."""

    EXACT = 0  # Perfect match (🟩)
    PARTIAL = 1  # Partial match - at least one element matches (🟧)
    WRONG = 2  # No match (🟥)
    BEFORE = 3  # Value is before/earlier (⬇️)
    AFTER = 4  # Value is after/later (⬆️)


# Emoji representations for visual output
MATCH_EMOJIS = {
    MatchType.EXACT: "🟩",
    MatchType.PARTIAL: "🟧",
    MatchType.WRONG: "🟥",
    MatchType.BEFORE: "⬇️",
    MatchType.AFTER: "⬆️",
}

# Reverse mapping for parsing emoji input
EMOJI_TO_MATCH = {v: k for k, v in MATCH_EMOJIS.items()}
# Handle emoji variations (with and without variation selector)
EMOJI_TO_MATCH["⬇"] = MatchType.BEFORE
EMOJI_TO_MATCH["⬆"] = MatchType.AFTER

# Category icons for display
CATEGORY_ICONS = {
    "gender": "🚹",
    "position": "📍",
    "species": "🦄",
    "resource": "⭐️",
    "range_type": "🗡️",
    "region": "🌎",
    "release_year": "🕰️",
    # Pokemon categories
    "type": "🔥",
    "habitat": "🏞️",
    "color": "🎨",
    "evolution_stage": "🔄",
    "height": "📏",
    "weight": "⚖️",
}

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
SRC_DIR = PROJECT_ROOT / "src"

# Number of categories to compare (for LoL)
LOL_NUM_CATEGORIES = 7
