"""Data loading functionality for champions and characters."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TypeVar

from loldle.models.base import Character
from loldle.models.lol import Champion
from loldle.utils.constants import DATA_DIR

T = TypeVar("T", bound=Character)


class DataLoadError(Exception):
    """Raised when data loading fails."""

    pass


def load_champions_from_csv(csv_path: Path | str | None = None) -> list[Champion]:
    """
    Load LoL champions from CSV file.

    Args:
        csv_path: Path to CSV file. If None, uses default path.

    Returns:
        List of Champion objects

    Raises:
        DataLoadError: If file doesn't exist or is malformed
    """
    if csv_path is None:
        csv_path = DATA_DIR / "champions_data.csv"
    else:
        csv_path = Path(csv_path)

    if not csv_path.exists():
        raise DataLoadError(f"Champion data file not found: {csv_path}")

    champions = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                try:
                    champions.append(Champion.from_csv_row(row))
                except (KeyError, ValueError) as e:
                    raise DataLoadError(f"Malformed CSV row: {e}") from e

    except Exception as e:
        raise DataLoadError(f"Failed to load champions: {e}") from e

    if not champions:
        raise DataLoadError("No champions loaded from CSV")

    return champions


def load_champion_names(json_path: Path | str | None = None) -> list[str]:
    """
    Load champion names from JSON file.

    Args:
        json_path: Path to JSON file. If None, uses default path.

    Returns:
        List of champion names

    Raises:
        DataLoadError: If file doesn't exist or is malformed
    """
    if json_path is None:
        json_path = DATA_DIR / "champions.json"
    else:
        json_path = Path(json_path)

    if not json_path.exists():
        raise DataLoadError(f"Champion names file not found: {json_path}")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            names = json.load(f)

        if not isinstance(names, list):
            raise DataLoadError("JSON file should contain a list of names")

        return names

    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON file: {e}") from e
    except Exception as e:
        raise DataLoadError(f"Failed to load champion names: {e}") from e


def save_champions_to_csv(
    champions: list[Champion],
    csv_path: Path | str,
    overwrite: bool = False,
) -> None:
    """
    Save champions to CSV file.

    Args:
        champions: List of Champion objects to save
        csv_path: Path where to save the CSV
        overwrite: Whether to overwrite existing file

    Raises:
        DataLoadError: If file exists and overwrite=False, or write fails
    """
    csv_path = Path(csv_path)

    if csv_path.exists() and not overwrite:
        raise DataLoadError(f"File already exists: {csv_path}. Use overwrite=True to replace.")

    try:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")

            # Write header
            writer.writerow(
                [
                    "Champion Name",
                    "Gender",
                    "Position(s)",
                    "Species",
                    "Resource",
                    "Range type",
                    "Region(s)",
                    "Release year",
                ]
            )

            # Write champion data
            for champ in champions:
                writer.writerow(
                    [
                        champ.name,
                        champ.gender,
                        ",".join(champ.positions),
                        ",".join(champ.species),
                        champ.resource,
                        ",".join(champ.range_types),
                        ",".join(champ.regions),
                        champ.release_year,
                    ]
                )

    except Exception as e:
        raise DataLoadError(f"Failed to save champions: {e}") from e


def get_character_by_name(
    characters: list[T],
    name: str,
    case_sensitive: bool = False,
) -> T | None:
    """
    Find a character by name.

    Args:
        characters: List of characters to search
        name: Name to search for
        case_sensitive: Whether to do case-sensitive matching

    Returns:
        Character if found, None otherwise
    """
    if case_sensitive:
        for char in characters:
            if char.name == name:
                return char
    else:
        name_lower = name.lower()
        for char in characters:
            if char.name.lower() == name_lower:
                return char

    return None


def filter_characters_by_prefix(
    characters: list[T],
    prefix: str,
    case_sensitive: bool = False,
) -> list[T]:
    """
    Filter characters whose names start with the given prefix.

    Args:
        characters: List of characters to filter
        prefix: Prefix to match
        case_sensitive: Whether to do case-sensitive matching

    Returns:
        List of matching characters
    """
    if case_sensitive:
        return [c for c in characters if c.name.startswith(prefix)]
    else:
        prefix_lower = prefix.lower()
        return [c for c in characters if c.name.lower().startswith(prefix_lower)]
