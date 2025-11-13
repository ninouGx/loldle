# Adding New Game Variants to Loldle Solver

This guide shows how to add new game variants (like Pokedle, Dotadle, etc.) to the Loldle Solver framework.

## Overview

The architecture is designed to make adding new variants trivial. You only need to:
1. Create a Character model (dataclass)
2. Implement comparison logic
3. Create a Game class
4. Add data sources
5. Register in CLI

## Step-by-Step Guide

### 1. Create Character Model

Create a new file: `src/loldle/models/pokemon.py` (or `dota.py`, etc.)

```python
"""Pokemon character model for Pokedle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loldle.models.base import (
    Character,
    ComparisonResult,
    compare_lists,
    compare_numbers,
    compare_values,
)


@dataclass
class Pokemon(Character):
    """Pokemon character for Pokedle."""

    type1: str = ""
    type2: str = ""
    habitat: str = ""
    color: str = ""
    evolution_stage: int = 0
    height: float = 0.0  # in meters
    weight: float = 0.0  # in kg

    def get_comparable_attributes(self) -> list[Any]:
        """Get attributes in comparison order."""
        return [
            self.type1,
            self.type2,
            self.habitat,
            self.color,
            self.evolution_stage,
            self.height,
            self.weight,
        ]

    def compare_with(self, other: Character) -> ComparisonResult:
        """Compare this Pokemon with another."""
        if not isinstance(other, Pokemon):
            raise TypeError(f"Cannot compare Pokemon with {type(other)}")

        matches = [
            compare_values(self.type1, other.type1),
            compare_values(self.type2, other.type2),
            compare_values(self.habitat, other.habitat),
            compare_values(self.color, other.color),
            compare_numbers(self.evolution_stage, other.evolution_stage),
            compare_numbers(self.height, other.height),
            compare_numbers(self.weight, other.weight),
        ]

        return ComparisonResult(
            matches=matches,
            tested_character=self.name,
            target_character=other.name,
        )

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> Pokemon:
        """Create Pokemon from CSV row."""
        return cls(
            name=row["Pokemon"],
            type1=row["Type 1"],
            type2=row.get("Type 2", ""),
            habitat=row.get("Habitat", ""),
            color=row.get("Color", ""),
            evolution_stage=int(row.get("Evolution Stage", "0")),
            height=float(row.get("Height", "0")),
            weight=float(row.get("Weight", "0")),
        )
```

### 2. Create Game Class

Create: `src/loldle/games/pokemon.py`

```python
"""Pokedle game implementation."""

from __future__ import annotations

from loldle.games.base import BaseGame
from loldle.models.pokemon import Pokemon


class PokedleGame(BaseGame[Pokemon]):
    """Pokedle game for Pokemon."""

    def __init__(self, pokemon: list[Pokemon] | None = None) -> None:
        """Initialize Pokedle game."""
        if pokemon is None:
            # Load from CSV
            from loldle.data.loader import load_pokemon_from_csv
            pokemon = load_pokemon_from_csv()

        super().__init__(pokemon)

    def get_game_name(self) -> str:
        """Get the name of this game variant."""
        return "Pokedle (Pokemon)"

    def get_category_headers(self) -> str:
        """Get emoji headers for comparison categories."""
        return "🔥💧🏞️🎨🔄📏⚖️"  # Type1, Type2, Habitat, Color, Evolution, Height, Weight
```

### 3. Add Data Loader

Add to `src/loldle/data/loader.py`:

```python
def load_pokemon_from_csv(csv_path: Path | str | None = None) -> list[Pokemon]:
    """
    Load Pokemon from CSV file.

    Args:
        csv_path: Path to CSV file. If None, uses default path.

    Returns:
        List of Pokemon objects
    """
    if csv_path is None:
        csv_path = DATA_DIR / "pokemon_data.csv"
    else:
        csv_path = Path(csv_path)

    if not csv_path.exists():
        raise DataLoadError(f"Pokemon data file not found: {csv_path}")

    pokemon = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            pokemon.append(Pokemon.from_csv_row(row))

    return pokemon
```

### 4. Create Data Source

Add to `src/loldle/data/sources.py`:

```python
class PokedleGitHubSource:
    """Fetch Pokemon data from community repositories."""

    SOURCES = [
        {
            "name": "pokedle-community-data",
            "url": "https://raw.githubusercontent.com/USER/REPO/main/pokemon.json",
            "parser": "parse_pokedle_format",
        },
    ]

    # ... implement similar to GitHubDataSource
```

### 5. Register in CLI

Add to `src/loldle/cli.py`:

```python
@main.command("play-pokemon")
@click.option(
    "--mode",
    type=click.Choice(["classic", "assisted", "online-helper"]),
    default="classic",
)
def play_pokemon(mode: str) -> None:
    """Play Pokedle (Pokemon variant)."""
    from loldle.games.pokemon import PokedleGame

    try:
        game = PokedleGame()
    except Exception as e:
        print_error(f"Failed to load Pokemon data: {e}")
        sys.exit(1)

    # Rest is the same as play() command...
```

### 6. CSV Data Format

Create `Data/pokemon_data.csv`:

```csv
Pokemon;Type 1;Type 2;Habitat;Color;Evolution Stage;Height;Weight
Pikachu;Electric;;Forest;Yellow;1;0.4;6.0
Charizard;Fire;Flying;Mountain;Red;2;1.7;90.5
```

## That's It!

The entire entropy solver, UI, and game logic automatically work with your new variant!

## Benefits of This Architecture

1. **No code duplication** - Game logic is inherited from BaseGame
2. **Automatic entropy calculations** - EntropySolver works with any Character type
3. **UI reuse** - All display and input functions work automatically
4. **Type safety** - Full type hints ensure correctness
5. **Extensibility** - Easy to add more variants

## Testing

```python
# Test your new variant
from loldle.games.pokemon import PokedleGame
from loldle.solvers.entropy import EntropySolver

game = PokedleGame()
game.start_new_game()

solver = EntropySolver()
best = solver.find_best_guess(game.characters, game.characters)
print(f"Best starting Pokemon: {best.character.name}")
```

## Examples of Potential Variants

- **Dotadle** - Dota 2 heroes
- **Narutodle** - Naruto characters
- **Smashdle** - Super Smash Bros characters
- **Poeltl** - NBA players
- **Footdle** - Soccer/football players

Each follows the same pattern!
