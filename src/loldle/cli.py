"""Command-line interface for Loldle solver."""

from __future__ import annotations

import sys
from typing import cast

import click

from loldle.games.base import BaseGame
from loldle.games.lol import LoldleGame
from loldle.models.base import Character, ComparisonResult
from loldle.models.lol import Champion
from loldle.solvers.entropy import EntropySolver
from loldle.ui.display import (
    clear_screen,
    console,
    print_entropy_recommendations,
    print_error,
    print_game_history,
    print_game_summary,
    print_info,
    print_match_legend,
    print_possible_characters,
    print_success,
    print_welcome_message,
)
from loldle.ui.input import (
    prompt_character_selection,
    prompt_choice,
    prompt_comparison_result,
    prompt_yes_no,
)
from loldle.utils.constants import LOL_NUM_CATEGORIES


@click.group()
@click.version_option(version="2.0.0", prog_name="loldle")
def main() -> None:
    """
    Loldle Solver - Play and solve Loldle and its variants.

    A CLI tool for playing guessing games like Loldle (League of Legends)
    with AI-powered assistance using information theory.
    """
    pass


@main.command()
@click.option(
    "--mode",
    type=click.Choice(["classic", "assisted", "online-helper"]),
    default=None,
    help="Game mode (interactive if not specified)",
)
@click.option(
    "--show-legend/--no-legend",
    default=True,
    help="Show match symbol legend at start",
)
def play(mode: str | None, show_legend: bool) -> None:
    """
    Play Loldle in various modes.

    \b
    MODES (choose interactively or use --mode):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. classic        - Play yourself without help
    2. assisted       - Get AI-powered optimal move suggestions
    3. online-helper  - Interactive helper for loldle.net
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
    EXAMPLES:
      loldle play                          # Interactive mode selection
      loldle play --mode assisted          # Direct to assisted mode
      loldle play --mode online-helper     # Direct to online helper
    """
    try:
        game = LoldleGame()
    except Exception as e:
        print_error(f"Failed to load game data: {e}")
        sys.exit(1)

    # If no mode specified, prompt user interactively
    if mode is None:
        clear_screen()
        print_welcome_message(game.get_game_name())

        console.print("\n[bold cyan]Select Game Mode:[/bold cyan]")
        console.print("  [bold]1.[/bold] Classic - Play yourself")
        console.print("  [bold]2.[/bold] Assisted - Get AI recommendations")
        console.print("  [bold]3.[/bold] Online Helper - Help for loldle.net (interactive)")

        from loldle.ui.input import prompt_choice

        mode_options = ["classic", "assisted", "online-helper"]
        choice_idx = prompt_choice(
            mode_options,
            "Enter your choice (1-3)",
            show_numbers=False,
        )

        if choice_idx is None:
            return

        mode = mode_options[choice_idx]
    else:
        clear_screen()
        print_welcome_message(game.get_game_name())

    if show_legend:
        print_match_legend()

    if mode == "classic":
        _play_classic_mode(game)
    elif mode == "assisted":
        _play_assisted_mode(game)
    elif mode == "online-helper":
        _play_online_helper_mode(game)


def _play_classic_mode(game: LoldleGame) -> None:
    """
    Play classic mode - guess the champion yourself.

    Args:
        game: The game instance
    """
    print_info("Classic Mode: Guess the champion!")
    print_info("The computer has selected a champion. Try to guess it.\n")

    game.start_new_game()

    while not game.is_game_over():
        # Show current state
        print_game_history(game, game.get_category_headers())

        print_info(f"\nGuesses so far: {game.state.num_guesses}")
        print_info(f"Remaining possibilities: {len(game.state.possible_characters)}")

        # Get player's guess
        untested = game.get_untested_characters()
        guess = prompt_character_selection(
            untested,
            "Enter your guess",
        )

        if guess is None:
            if prompt_yes_no("Quit game?"):
                return
            continue

        # Make the guess
        try:
            result = game.make_guess(guess)
            clear_screen()

            if result.is_perfect_match():
                print_game_history(game, game.get_category_headers())
                print_game_summary(game)
                break

        except ValueError as e:
            print_error(str(e))
            continue

    if not game.state.is_won:
        print_game_summary(game)


def _play_assisted_mode(game: LoldleGame) -> None:
    """
    Play with AI assistance - get entropy-based recommendations.

    Args:
        game: The game instance
    """
    print_info("Assisted Mode: Get AI recommendations!")
    print_info("The computer will suggest optimal guesses based on information theory.\n")

    game.start_new_game()
    solver = EntropySolver()

    # Show first guess recommendation
    console.print("\n[bold cyan]Calculating optimal first guess...[/bold cyan]")
    best_first = solver.find_best_guess(game.characters, game.characters)

    if best_first:
        console.print(f"\n[bold green]Recommended first guess: {best_first.character.name}[/bold green]")
        console.print(f"Expected information gain: {best_first.entropy:.3f} bits")

    while not game.is_game_over():
        # Show current state
        print_game_history(game, game.get_category_headers())

        print_info(f"\nGuesses so far: {game.state.num_guesses}")

        # Show recommendations if not first guess
        if game.state.num_guesses > 0 and len(game.state.possible_characters) > 1:
            console.print("\n[bold cyan]Calculating recommendations...[/bold cyan]")
            recommendations = solver.get_top_guesses(
                game.characters,
                game.state.possible_characters,
                n=5,
            )
            print_entropy_recommendations(recommendations)

        # Show possible characters if few remain
        if len(game.state.possible_characters) <= 10:
            print_possible_characters(game.state.possible_characters)

        # Get player's guess
        untested = game.get_untested_characters()
        guess = prompt_character_selection(
            untested,
            "Enter your guess",
        )

        if guess is None:
            if prompt_yes_no("Quit game?"):
                return
            continue

        # Make the guess
        try:
            result = game.make_guess(guess)
            clear_screen()

            if result.is_perfect_match():
                print_game_history(game, game.get_category_headers())
                print_game_summary(game)
                break

        except ValueError as e:
            print_error(str(e))
            continue

    if not game.state.is_won:
        print_game_summary(game)


def _play_online_helper_mode(game: LoldleGame) -> None:
    """
    Helper mode for playing on loldle.net - suggests moves based on your results.

    Args:
        game: The game instance
    """
    print_info("Online Helper Mode!")
    print_info("This mode helps you play on loldle.net")
    print_info("Enter the results you get from the website, and I'll suggest the best next guess.\n")

    # Don't start a game - we're helping with an external game
    game.state.possible_characters = game.characters.copy()
    solver = EntropySolver()

    # First guess recommendation
    console.print("\n[bold cyan]Calculating optimal first guess...[/bold cyan]")
    best_first = solver.find_best_guess(game.characters, game.characters)

    if best_first:
        console.print(f"\n[bold green]Recommended first guess: {best_first.character.name}[/bold green]")
        console.print(f"Expected information gain: {best_first.entropy:.3f} bits")

    guess_count = 0

    while len(game.state.possible_characters) > 0:
        # Get the character they guessed
        console.print("\n" + "=" * 50)
        print_info("What did you guess on the website?")

        guessed_char = prompt_character_selection(
            game.characters,
            "Enter the champion you guessed",
        )

        if guessed_char is None:
            if prompt_yes_no("Exit helper?"):
                return
            continue

        # Get the result from the website
        print_info(f"\nEnter the result you got for {guessed_char.name}")
        print_info("(Copy the emoji row from the website, or enter numbers 0-4)")

        result = prompt_comparison_result(guessed_char.name, LOL_NUM_CATEGORIES)

        if result is None:
            continue

        # Check if they won
        if result.is_perfect_match():
            print_success(f"\n🎉 Congratulations! You found it in {guess_count + 1} guesses!")
            return

        # Update possible characters
        game.state.tested_characters.append(guessed_char)
        game.state.comparison_results.append(result)
        guess_count += 1

        # Filter compatible characters
        game.state.possible_characters = game._filter_compatible_characters(
            result, cast(Champion, guessed_char)
        )

        clear_screen()

        # Show history
        print_game_history(game, game.get_category_headers())

        # Show remaining possibilities
        print_info(f"\nRemaining possibilities: {len(game.state.possible_characters)}")

        if len(game.state.possible_characters) == 0:
            print_error("No possible champions remaining! Check your inputs.")
            return

        if len(game.state.possible_characters) <= 5:
            print_possible_characters(game.state.possible_characters)
            continue

        # Get recommendations
        console.print("\n[bold cyan]Calculating next best guess...[/bold cyan]")
        recommendations = solver.get_top_guesses(
            game.characters,
            game.state.possible_characters,
            n=5,
        )
        print_entropy_recommendations(recommendations)


@main.command()
@click.option(
    "--verbose/--quiet",
    default=False,
    help="Show detailed entropy calculations",
)
def solve(verbose: bool) -> None:
    """
    Calculate the optimal first guess for Loldle.

    This analyzes all champions and finds the one with the highest
    information gain for starting a game.
    """
    try:
        game = LoldleGame()
    except Exception as e:
        print_error(f"Failed to load game data: {e}")
        sys.exit(1)

    console.print("\n[bold cyan]Analyzing all champions to find optimal first guess...[/bold cyan]\n")

    solver = EntropySolver()

    if verbose:
        console.print("[dim]This may take a moment...[/dim]\n")

    top_guesses = solver.get_top_guesses(
        game.characters,
        game.characters,
        n=10,
        verbose=verbose,
    )

    console.print("\n[bold green]Top 10 starting champions:[/bold green]\n")

    print_entropy_recommendations(
        top_guesses,
        title="Best starting guesses (ranked by information gain):",
    )

    if top_guesses:
        console.print(
            f"\n[bold]Recommendation:[/bold] Start with [bold green]{top_guesses[0].character.name}[/bold green]"
        )


@main.command()
def info() -> None:
    """Show information about the loaded game data."""
    try:
        game = LoldleGame()
    except Exception as e:
        print_error(f"Failed to load game data: {e}")
        sys.exit(1)

    console.print(f"\n[bold cyan]{game.get_game_name()}[/bold cyan]")
    console.print(f"Total champions: {len(game.characters)}")
    console.print(f"Data categories: {LOL_NUM_CATEGORIES}")
    console.print(f"Category headers: {game.get_category_headers()}")

    # Show some statistics
    champions = cast(list[Champion], game.characters)

    genders = set(c.gender for c in champions)
    console.print(f"\nUnique genders: {len(genders)}")

    all_positions = set()
    for c in champions:
        all_positions.update(c.positions)
    console.print(f"Unique positions: {len(all_positions)}")

    years = [c.release_year for c in champions]
    console.print(f"Release years: {min(years)} - {max(years)}")

    console.print(f"\nNewest champion: {max(champions, key=lambda c: c.release_year).name}")
    console.print(f"Oldest champion: {min(champions, key=lambda c: c.release_year).name}")


@main.command("refresh-data")
@click.option(
    "--source",
    type=click.Choice(["auto", "github", "scraper"]),
    default="auto",
    help="Data source to use",
)
@click.option(
    "--backup/--no-backup",
    default=True,
    help="Backup existing data before refresh",
)
def refresh_data(source: str, backup: bool) -> None:
    """
    Refresh champion data from online sources.

    This command fetches the latest champion data and updates your local CSV file.
    By default, it backs up the existing data before updating.

    \b
    Sources:
    - auto: Try all sources automatically (recommended)
    - github: Use community GitHub repositories
    - scraper: Scrape directly from loldle.net (may be slower)
    """
    from datetime import datetime
    from pathlib import Path

    from loldle.data.sources import fetch_champions_from_best_source
    from loldle.utils.constants import DATA_DIR

    console.print("\n[bold cyan]Refreshing champion data...[/bold cyan]\n")

    # Backup existing data
    data_file = DATA_DIR / "champions_data.csv"
    if backup and data_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = DATA_DIR / f"champions_data.backup_{timestamp}.csv"
        try:
            import shutil

            shutil.copy2(data_file, backup_file)
            console.print(f"[dim]Backed up existing data to: {backup_file.name}[/dim]\n")
        except Exception as e:
            print_warning(f"Could not create backup: {e}")

    # Fetch new data
    try:
        if source == "auto" or source == "github":
            console.print("[cyan]Fetching from community GitHub repositories...[/cyan]")
            champions = fetch_champions_from_best_source(verbose=True)

        elif source == "scraper":
            console.print("[cyan]Scraping data from loldle.net...[/cyan]")
            from loldle.data.scraper import scrape_loldle_data

            champions = scrape_loldle_data(verbose=True, save=False)

        else:
            print_error(f"Unknown source: {source}")
            sys.exit(1)

        # Save to CSV
        from loldle.data.loader import save_champions_to_csv

        save_champions_to_csv(champions, data_file, overwrite=True)

        print_success(f"\n✓ Successfully updated data with {len(champions)} champions!")
        console.print(f"[dim]Data saved to: {data_file}[/dim]")

        # Show what changed
        if backup:
            console.print("\n[bold]You can run 'loldle info' to see the updated statistics.[/bold]")

    except Exception as e:
        print_error(f"Failed to refresh data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
