"""UI display functions using rich for beautiful terminal output."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from loldle.models.base import ComparisonResult
from loldle.utils.constants import MATCH_EMOJIS

if TYPE_CHECKING:
    from loldle.games.base import BaseGame, GameState
    from loldle.models.base import Character
    from loldle.solvers.entropy import EntropyScore

console = Console()


def print_header(game_name: str) -> None:
    """Print the game header."""
    text = Text(game_name, style="bold cyan")
    panel = Panel(text, border_style="cyan")
    console.print(panel)


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]{message}[/bold green]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[cyan]{message}[/cyan]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]{message}[/yellow]")


def print_comparison_result(
    result: ComparisonResult,
    category_headers: str,
    show_character_name: bool = True,
) -> None:
    """
    Print a single comparison result.

    Args:
        result: The comparison result to display
        category_headers: Emoji/text headers for categories
        show_character_name: Whether to show the character name
    """
    emoji_str = result.to_emoji_string()

    if show_character_name:
        console.print(f"{emoji_str} {result.tested_character}")
    else:
        console.print(emoji_str)


def print_game_history(
    game: BaseGame,
    category_headers: str | None = None,
) -> None:
    """
    Print the history of guesses in the game.

    Args:
        game: The game instance
        category_headers: Optional category headers to display
    """
    if category_headers:
        console.print(f"\n{category_headers}")

    if not game.state.tested_characters:
        print_info("No guesses yet.")
        return

    # Print in reverse order (most recent first shown last, like the original)
    for i in range(len(game.state.tested_characters) - 1, -1, -1):
        character = game.state.tested_characters[i]
        result = game.state.comparison_results[i]
        print_comparison_result(result, category_headers or "")


def print_possible_characters(
    characters: list[Character],
    max_display: int = 10,
) -> None:
    """
    Print list of possible remaining characters.

    Args:
        characters: List of possible characters
        max_display: Maximum number to display before truncating
    """
    if not characters:
        print_warning("No possible characters remaining!")
        return

    count = len(characters)
    console.print(f"\n[cyan]Possible characters remaining: {count}[/cyan]")

    if count <= max_display:
        for char in characters:
            console.print(f"  • {char.name}")
    else:
        for char in characters[:max_display]:
            console.print(f"  • {char.name}")
        console.print(f"  ... and {count - max_display} more")


def print_entropy_recommendations(
    recommendations: list[EntropyScore],
    title: str = "Recommended guesses (by information gain):",
) -> None:
    """
    Print entropy-based recommendations.

    Args:
        recommendations: List of EntropyScore objects
        title: Title to display
    """
    if not recommendations:
        return

    console.print(f"\n[bold cyan]{title}[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Character", style="bold")
    table.add_column("Entropy", justify="right")
    table.add_column("Exp. Remaining", justify="right")

    for i, score in enumerate(recommendations, 1):
        table.add_row(
            f"#{i}",
            score.character.name,
            f"{score.entropy:.3f}",
            f"{score.expected_remaining:.1f}",
        )

    console.print(table)


def print_game_summary(game: BaseGame) -> None:
    """
    Print a summary of the completed game.

    Args:
        game: The game instance
    """
    summary = game.get_game_summary()

    console.print("\n" + "=" * 50)

    if summary["is_won"]:
        print_success(f"🎉 You won in {summary['num_guesses']} guesses!")
        console.print(f"[green]The answer was: {summary['target']}[/green]")
    else:
        print_error("Game over - no possibilities remaining!")
        console.print(f"[yellow]The answer was: {summary['target']}[/yellow]")

    console.print("=" * 50 + "\n")


def print_character_details(character: Character) -> None:
    """
    Print detailed information about a character.

    Args:
        character: The character to display
    """
    # Try to get detailed display if available
    if hasattr(character, "to_display_string"):
        console.print(character.to_display_string())
    else:
        console.print(str(character))


def clear_screen() -> None:
    """Clear the terminal screen."""
    console.clear()


def print_welcome_message(game_name: str) -> None:
    """
    Print welcome message for the game.

    Args:
        game_name: Name of the game
    """
    welcome_text = Text()
    welcome_text.append("Welcome to ", style="bold")
    welcome_text.append(game_name, style="bold cyan")
    welcome_text.append("!", style="bold")

    panel = Panel(
        welcome_text,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)


def print_mode_selection(modes: list[str]) -> None:
    """
    Print available game modes.

    Args:
        modes: List of mode names
    """
    console.print("\n[bold cyan]Available modes:[/bold cyan]")
    for i, mode in enumerate(modes, 1):
        console.print(f"  {i}. {mode}")


def print_match_legend() -> None:
    """Print legend explaining the match symbols."""
    console.print("\n[bold]Match Legend:[/bold]")
    console.print(f"  {MATCH_EMOJIS[0]} Exact match")
    console.print(f"  {MATCH_EMOJIS[1]} Partial match (at least one element matches)")
    console.print(f"  {MATCH_EMOJIS[2]} No match")
    console.print(f"  {MATCH_EMOJIS[3]} Target value is before/lower")
    console.print(f"  {MATCH_EMOJIS[4]} Target value is after/higher")
    console.print()
