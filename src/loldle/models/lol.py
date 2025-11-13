"""League of Legends champion model."""

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
from loldle.utils.constants import LOL_NUM_CATEGORIES


@dataclass
class Champion(Character):
    """League of Legends champion."""

    gender: str = ""
    positions: list[str] = None  # type: ignore
    species: list[str] = None  # type: ignore
    resource: str = ""
    range_types: list[str] = None  # type: ignore
    regions: list[str] = None  # type: ignore
    release_year: int = 0

    def __post_init__(self) -> None:
        """Initialize list fields if None."""
        if self.positions is None:
            self.positions = []
        if self.species is None:
            self.species = []
        if self.range_types is None:
            self.range_types = []
        if self.regions is None:
            self.regions = []

    def get_comparable_attributes(self) -> list[Any]:
        """Get attributes in comparison order."""
        return [
            self.gender,
            self.positions,
            self.species,
            self.resource,
            self.range_types,
            self.regions,
            self.release_year,
        ]

    def compare_with(self, other: Character) -> ComparisonResult:
        """
        Compare this champion with another.

        Order of comparison:
        1. Gender (exact/wrong)
        2. Positions (exact/partial/wrong)
        3. Species (exact/partial/wrong)
        4. Resource (exact/wrong)
        5. Range types (exact/partial/wrong)
        6. Regions (exact/partial/wrong)
        7. Release year (exact/before/after)

        Args:
            other: Champion to compare against

        Returns:
            ComparisonResult with 7 match types
        """
        if not isinstance(other, Champion):
            raise TypeError(f"Cannot compare Champion with {type(other)}")

        matches = [
            compare_values(self.gender, other.gender),
            compare_lists(self.positions, other.positions),
            compare_lists(self.species, other.species),
            compare_values(self.resource, other.resource),
            compare_lists(self.range_types, other.range_types),
            compare_lists(self.regions, other.regions),
            compare_numbers(self.release_year, other.release_year),
        ]

        return ComparisonResult(
            matches=matches,
            tested_character=self.name,
            target_character=other.name,
        )

    def to_display_string(self) -> str:
        """Get a detailed string representation for display."""
        return (
            f"Name: {self.name}\n"
            f"Gender: {self.gender}\n"
            f"Positions: {', '.join(self.positions)}\n"
            f"Species: {', '.join(self.species)}\n"
            f"Resource: {self.resource}\n"
            f"Range Types: {', '.join(self.range_types)}\n"
            f"Regions: {', '.join(self.regions)}\n"
            f"Release Year: {self.release_year}"
        )

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> Champion:
        """
        Create a Champion from a CSV row dictionary.

        Args:
            row: Dictionary with keys matching CSV headers

        Returns:
            Champion instance
        """
        return cls(
            name=row["Champion Name"],
            gender=row["Gender"],
            positions=row["Position(s)"].split(",") if row["Position(s)"] else [],
            species=row["Species"].split(",") if row["Species"] else [],
            resource=row["Resource"],
            range_types=row["Range type"].split(",") if row["Range type"] else [],
            regions=row["Region(s)"].split(",") if row["Region(s)"] else [],
            release_year=int(row["Release year"]),
        )


def get_category_names() -> list[str]:
    """Get the names of all champion categories in comparison order."""
    return [
        "Gender",
        "Position(s)",
        "Species",
        "Resource",
        "Range type",
        "Region(s)",
        "Release year",
    ]


def get_category_icons() -> str:
    """Get emoji icons for all categories."""
    return "🚹📍🦄⭐️🗡️🌎🕰️"
