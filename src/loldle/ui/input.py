"""User input handling functions."""

from __future__ import annotations

from typing import TypeVar

from rich.prompt import Prompt

from loldle.data.loader import filter_characters_by_prefix, get_character_by_name
from loldle.models.base import Character, ComparisonResult
from loldle.ui.display import console, print_error, print_info, print_warning

T = TypeVar("T", bound=Character)


def prompt_character_selection(
    characters: list[T],
    prompt_text: str = "Enter character name",
    allow_partial: bool = True,
) -> T | None:
    """
    Prompt user to select a character with autocomplete.

    Args:
        characters: List of available characters
        prompt_text: Text to show in the prompt
        allow_partial: Whether to allow partial name matching

    Returns:
        Selected character, or None if cancelled
    """
    while True:
        try:
            user_input = Prompt.ask(f"\n[cyan]{prompt_text}[/cyan]").strip()

            if not user_input:
                print_warning("Empty input. Try again or press Ctrl+C to cancel.")
                continue

            # Check for exact match first (case-insensitive)
            exact_match = get_character_by_name(characters, user_input, case_sensitive=False)
            if exact_match:
                return exact_match

            # If partial matching allowed, find candidates
            if allow_partial:
                matches = filter_characters_by_prefix(
                    characters, user_input, case_sensitive=False
                )

                if len(matches) == 0:
                    print_error(f"No characters found starting with '{user_input}'")
                    continue
                elif len(matches) == 1:
                    print_info(f"Selected: {matches[0].name}")
                    return matches[0]
                else:
                    print_info(f"Multiple matches found ({len(matches)}):")
                    for char in matches[:10]:  # Show max 10
                        console.print(f"  • {char.name}")
                    if len(matches) > 10:
                        console.print(f"  ... and {len(matches) - 10} more")
                    print_warning("Please be more specific")
                    continue
            else:
                print_error(f"Character '{user_input}' not found")
                continue

        except KeyboardInterrupt:
            print_warning("\nCancelled")
            return None
        except EOFError:
            return None


def prompt_comparison_result(
    character_name: str,
    num_categories: int,
) -> ComparisonResult | None:
    """
    Prompt user to enter a comparison result.

    Accepts either:
    - Emoji string (🟩🟥🟧⬇️⬆️)
    - Number string (0-4 for each category)

    Args:
        character_name: Name of the character being compared
        num_categories: Expected number of categories

    Returns:
        ComparisonResult, or None if cancelled
    """
    while True:
        try:
            prompt_text = (
                f"\n[cyan]Enter result for {character_name}[/cyan]\n"
                f"(Use emojis 🟩🟥🟧⬇️⬆️ or numbers 0-4)"
            )
            user_input = Prompt.ask(prompt_text).strip()

            if not user_input:
                print_warning("Empty input. Try again or press Ctrl+C to cancel.")
                continue

            # Try to parse as emoji first
            if any(c in user_input for c in "🟩🟥🟧⬇️⬆️⬇⬆"):
                result = ComparisonResult.from_emoji_string(user_input, character_name)
            # Try to parse as numbers
            elif user_input.replace(" ", "").isdigit():
                clean_input = user_input.replace(" ", "")
                result = ComparisonResult.from_number_string(clean_input, character_name)
            else:
                print_error("Invalid format. Use emojis or numbers 0-4.")
                continue

            # Validate length
            if len(result.matches) != num_categories:
                print_error(
                    f"Expected {num_categories} categories, got {len(result.matches)}"
                )
                continue

            return result

        except KeyboardInterrupt:
            print_warning("\nCancelled")
            return None
        except EOFError:
            return None
        except (ValueError, IndexError) as e:
            print_error(f"Invalid input: {e}")
            continue


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """
    Ask a yes/no question.

    Args:
        question: The question to ask
        default: Default answer if user presses Enter

    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    try:
        answer = Prompt.ask(f"[cyan]{question}[/cyan] [{default_str}]").strip().lower()

        if not answer:
            return default

        return answer in ("y", "yes", "true", "1")

    except (KeyboardInterrupt, EOFError):
        return default


def prompt_choice(
    options: list[str],
    prompt_text: str = "Select an option",
    show_numbers: bool = True,
) -> int | None:
    """
    Prompt user to select from a list of options.

    Args:
        options: List of option strings
        prompt_text: Text to show in the prompt
        show_numbers: Whether to show option numbers

    Returns:
        Index of selected option (0-based), or None if cancelled
    """
    if show_numbers:
        console.print(f"\n[cyan]{prompt_text}:[/cyan]")
        for i, option in enumerate(options, 1):
            console.print(f"  {i}. {option}")

    while True:
        try:
            choice = Prompt.ask("\n[cyan]Enter choice[/cyan]").strip()

            if not choice:
                print_warning("Please enter a choice")
                continue

            # Try to parse as number
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return idx
                else:
                    print_error(f"Please enter a number between 1 and {len(options)}")
                    continue

            # Try to match text
            for i, option in enumerate(options):
                if option.lower().startswith(choice.lower()):
                    return i

            print_error("Invalid choice")

        except KeyboardInterrupt:
            print_warning("\nCancelled")
            return None
        except EOFError:
            return None


def wait_for_enter(message: str = "Press Enter to continue...") -> None:
    """
    Wait for user to press Enter.

    Args:
        message: Message to display
    """
    try:
        Prompt.ask(f"\n[dim]{message}[/dim]", default="")
    except (KeyboardInterrupt, EOFError):
        pass
