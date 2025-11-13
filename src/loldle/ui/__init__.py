"""User interface components."""

from loldle.ui.display import (
    clear_screen,
    console,
    print_entropy_recommendations,
    print_error,
    print_game_history,
    print_game_summary,
    print_header,
    print_info,
    print_match_legend,
    print_possible_characters,
    print_success,
    print_warning,
)
from loldle.ui.input import (
    prompt_character_selection,
    prompt_choice,
    prompt_comparison_result,
    prompt_yes_no,
    wait_for_enter,
)

__all__ = [
    # Display
    "console",
    "clear_screen",
    "print_header",
    "print_error",
    "print_success",
    "print_info",
    "print_warning",
    "print_game_history",
    "print_possible_characters",
    "print_entropy_recommendations",
    "print_game_summary",
    "print_match_legend",
    # Input
    "prompt_character_selection",
    "prompt_comparison_result",
    "prompt_yes_no",
    "prompt_choice",
    "wait_for_enter",
]
