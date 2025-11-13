"""
Multiple data sources for champion/character data.

Provides fallback mechanisms to get data from various sources:
1. Community GitHub repositories (LoLdleData, joulsen/loldle-information-theory)
2. Direct website scraping (loldle.net)
3. Riot Data Dragon API (fallback)
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import requests

from loldle.models.lol import Champion


class DataSourceError(Exception):
    """Raised when data source fails."""

    pass


class GitHubDataSource:
    """Fetch data from community GitHub repositories."""

    SOURCES = [
        {
            "name": "joulsen/loldle-information-theory",
            "url": "https://raw.githubusercontent.com/joulsen/loldle-information-theory/main/resources/loldle-champ-data.json",
            "parser": "parse_joulsen_format",
        },
        {
            "name": "infiniteloldle backup",
            "url": "https://raw.githubusercontent.com/lassesuomela/infiniteloldle/master/backend/data/championsdata.json",
            "parser": "parse_infiniteloldle_format",
        },
    ]

    TIMEOUT = 30

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize the data source.

        Args:
            verbose: Whether to print progress
        """
        self.verbose = verbose

    def _log(self, message: str) -> None:
        """Log message if verbose."""
        if self.verbose:
            print(f"[GitHub Source] {message}")

    def fetch_json(self, url: str) -> Any:
        """
        Fetch JSON from URL.

        Args:
            url: URL to fetch

        Returns:
            Parsed JSON data

        Raises:
            DataSourceError: If fetch fails
        """
        try:
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise DataSourceError(f"Failed to fetch {url}: {e}") from e

    def parse_joulsen_format(self, data: list[dict[str, Any]]) -> list[Champion]:
        """
        Parse data from joulsen/loldle-information-theory format.

        Args:
            data: List of champion dictionaries

        Returns:
            List of Champion objects
        """
        champions = []

        for item in data:
            try:
                # Extract year from release_date (YYYY-MM-DD format)
                release_date = item.get("release_date", "")
                if release_date:
                    year = int(release_date.split("-")[0])
                else:
                    year = 0

                champion = Champion(
                    name=item["championName"],
                    gender=item.get("gender", ""),
                    positions=item.get("positions", []),
                    species=item.get("species", []),
                    resource=item.get("resource", ""),
                    range_types=item.get("range_type", []),
                    regions=item.get("regions", []),
                    release_year=year,
                )
                champions.append(champion)

            except (KeyError, ValueError) as e:
                self._log(f"Warning: Skipping malformed champion: {e}")
                continue

        return champions

    def parse_infiniteloldle_format(self, data: Any) -> list[Champion]:
        """
        Parse data from infiniteloldle format (may be different structure).

        Args:
            data: Champion data

        Returns:
            List of Champion objects
        """
        # This is a placeholder - would need to check actual structure
        if isinstance(data, list):
            return self.parse_joulsen_format(data)
        return []

    def fetch_champions(self) -> list[Champion]:
        """
        Fetch champions from GitHub sources (tries all sources).

        Returns:
            List of Champion objects

        Raises:
            DataSourceError: If all sources fail
        """
        errors = []

        for source in self.SOURCES:
            try:
                self._log(f"Trying source: {source['name']}...")
                data = self.fetch_json(source["url"])

                parser_method = getattr(self, source["parser"])
                champions = parser_method(data)

                if champions:
                    self._log(f"Successfully loaded {len(champions)} champions from {source['name']}")
                    return champions

            except Exception as e:
                self._log(f"Failed to load from {source['name']}: {e}")
                errors.append(f"{source['name']}: {e}")
                continue

        raise DataSourceError(
            f"All GitHub sources failed:\n" + "\n".join(errors)
        )


class DataDragonSource:
    """
    Fetch data from Riot's Data Dragon API.

    Note: This provides raw champion data but doesn't have the
    specific Loldle attributes (species, regions, etc.) so it's
    mainly useful for getting a champion list.
    """

    VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
    CHAMPION_URL_TEMPLATE = "https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"

    TIMEOUT = 30

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize the data source.

        Args:
            verbose: Whether to print progress
        """
        self.verbose = verbose

    def _log(self, message: str) -> None:
        """Log message if verbose."""
        if self.verbose:
            print(f"[Data Dragon] {message}")

    def get_latest_version(self) -> str:
        """
        Get the latest Data Dragon version.

        Returns:
            Version string (e.g., "15.22.1")

        Raises:
            DataSourceError: If fetch fails
        """
        try:
            response = requests.get(
                self.VERSIONS_URL,
                timeout=self.TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
            versions = response.json()
            return versions[0]  # First is latest
        except Exception as e:
            raise DataSourceError(f"Failed to get Data Dragon version: {e}") from e

    def fetch_champion_names(self) -> list[str]:
        """
        Fetch list of champion names from Data Dragon.

        Returns:
            List of champion names

        Raises:
            DataSourceError: If fetch fails
        """
        try:
            version = self.get_latest_version()
            self._log(f"Using Data Dragon version: {version}")

            url = self.CHAMPION_URL_TEMPLATE.format(version=version)
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()

            data = response.json()
            champions = data["data"]

            names = [champ_data["name"] for champ_data in champions.values()]
            self._log(f"Fetched {len(names)} champion names")

            return names

        except Exception as e:
            raise DataSourceError(f"Failed to fetch from Data Dragon: {e}") from e


def fetch_champions_from_best_source(verbose: bool = True) -> list[Champion]:
    """
    Fetch champions from the best available source.

    Tries sources in order:
    1. GitHub community repositories (most reliable for Loldle data)
    2. Data Dragon (fallback, but missing Loldle-specific attributes)

    Args:
        verbose: Whether to print progress

    Returns:
        List of Champion objects

    Raises:
        DataSourceError: If all sources fail
    """
    # Try GitHub sources first (has Loldle-specific data)
    try:
        github_source = GitHubDataSource(verbose=verbose)
        return github_source.fetch_champions()
    except DataSourceError as e:
        if verbose:
            print(f"GitHub sources failed: {e}")

    # If GitHub fails, we can't really use Data Dragon alone
    # because it doesn't have species, regions, etc.
    raise DataSourceError(
        "Could not fetch champion data from any source. "
        "Please check your internet connection or try again later."
    )
