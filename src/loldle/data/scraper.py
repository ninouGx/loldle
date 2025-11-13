"""
Intelligent data scraper for Loldle and variant games.

This module provides scrapers that extract champion/character data directly
from game websites without using Selenium. It parses the JavaScript bundles
to extract embedded data.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from loldle.data.loader import save_champions_to_csv
from loldle.models.lol import Champion
from loldle.utils.constants import DATA_DIR


class ScraperError(Exception):
    """Raised when scraping fails."""

    pass


class LoldleScraper:
    """
    Scraper for loldle.net champion data.

    Extracts champion data from the website's JavaScript bundle
    without using Selenium.
    """

    BASE_URL = "https://loldle.net"
    TIMEOUT = 30

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize the scraper.

        Args:
            verbose: Whether to print progress messages
        """
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def _log(self, message: str) -> None:
        """Print message if verbose mode is on."""
        if self.verbose:
            print(f"[Scraper] {message}")

    def fetch_page(self, url: str) -> str:
        """
        Fetch a web page.

        Args:
            url: URL to fetch

        Returns:
            Page HTML content

        Raises:
            ScraperError: If request fails
        """
        self._log(f"Fetching {url}...")

        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ScraperError(f"Failed to fetch {url}: {e}") from e

    def find_js_bundles(self, html: str) -> list[str]:
        """
        Find JavaScript bundle URLs in HTML.

        Args:
            html: HTML content

        Returns:
            List of JS bundle URLs
        """
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script", src=True)

        bundles = []
        for script in scripts:
            src = script["src"]
            if "app" in src.lower() or "main" in src.lower() or "chunk" in src.lower():
                if not src.startswith("http"):
                    src = f"{self.BASE_URL}/{src.lstrip('/')}"
                bundles.append(src)

        return bundles

    def extract_champion_data_from_js(self, js_content: str) -> list[dict[str, Any]]:
        """
        Extract champion data from JavaScript bundle.

        The data is usually embedded as a large array/object in the minified JS.

        Args:
            js_content: JavaScript file content

        Returns:
            List of champion dictionaries

        Raises:
            ScraperError: If data extraction fails
        """
        self._log("Extracting champion data from JS...")

        # Look for patterns that might contain champion data
        patterns = [
            # Look for arrays containing champion data
            r"championId.*?\[({.*?})\]",
            r"champions\s*[:=]\s*(\[.*?\])",
            # Look for large JSON-like structures
            r"(\[{[^}]*championId[^}]*}.*?\])",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.DOTALL)
            for match in matches:
                try:
                    # Try to parse as JSON
                    data = json.loads(match)
                    if isinstance(data, list) and len(data) > 50:  # Should have 150+ champions
                        # Validate it looks like champion data
                        if all(isinstance(item, dict) for item in data):
                            self._log(f"Found {len(data)} champions in data")
                            return data
                except json.JSONDecodeError:
                    continue

        # If we couldn't find embedded data, try alternative approach
        # Look for variable assignments
        var_pattern = r"var\s+\w+\s*=\s*(\[{.*?}\])"
        matches = re.findall(var_pattern, js_content, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, list) and len(data) > 50:
                    return data
            except json.JSONDecodeError:
                continue

        raise ScraperError(
            "Could not extract champion data from JavaScript. "
            "The website structure may have changed."
        )

    def parse_champion_from_loldle_data(self, data: dict[str, Any]) -> Champion:
        """
        Parse a champion from loldle.net data format.

        Args:
            data: Champion data dictionary

        Returns:
            Champion instance
        """
        # Map loldle.net fields to our Champion model
        # Field names may vary, so we try multiple possibilities

        name = data.get("name") or data.get("championId") or data.get("id", "")

        gender = data.get("gender", "")

        # Positions (roles)
        positions_raw = data.get("positions") or data.get("roles") or data.get("position", [])
        if isinstance(positions_raw, str):
            positions = [positions_raw]
        elif isinstance(positions_raw, list):
            positions = positions_raw
        else:
            positions = []

        # Species
        species_raw = data.get("species", [])
        if isinstance(species_raw, str):
            species = [species_raw]
        elif isinstance(species_raw, list):
            species = species_raw
        else:
            species = []

        resource = data.get("resource", "")

        # Range types
        range_raw = data.get("rangeType") or data.get("range", [])
        if isinstance(range_raw, str):
            range_types = [range_raw]
        elif isinstance(range_raw, list):
            range_types = range_raw
        else:
            range_types = []

        # Regions
        regions_raw = data.get("regions") or data.get("region", [])
        if isinstance(regions_raw, str):
            regions = [regions_raw]
        elif isinstance(regions_raw, list):
            regions = regions_raw
        else:
            regions = []

        # Release year
        release_year = int(data.get("releaseYear", 0))

        return Champion(
            name=name,
            gender=gender,
            positions=positions,
            species=species,
            resource=resource,
            range_types=range_types,
            regions=regions,
            release_year=release_year,
        )

    def scrape_champions(self) -> list[Champion]:
        """
        Scrape all champions from loldle.net.

        Returns:
            List of Champion objects

        Raises:
            ScraperError: If scraping fails
        """
        self._log("Starting loldle.net scrape...")

        # Fetch main page
        html = self.fetch_page(self.BASE_URL)

        # Find JS bundles
        bundles = self.find_js_bundles(html)
        self._log(f"Found {len(bundles)} JS bundles")

        if not bundles:
            raise ScraperError("No JavaScript bundles found on page")

        # Try each bundle until we find champion data
        for bundle_url in bundles:
            try:
                self._log(f"Checking bundle: {bundle_url}")
                js_content = self.fetch_page(bundle_url)

                champion_data = self.extract_champion_data_from_js(js_content)

                # Parse into Champion objects
                champions = []
                for data in champion_data:
                    try:
                        champion = self.parse_champion_from_loldle_data(data)
                        champions.append(champion)
                    except Exception as e:
                        self._log(f"Warning: Failed to parse champion: {e}")
                        continue

                if champions:
                    self._log(f"Successfully extracted {len(champions)} champions")
                    return champions

            except ScraperError:
                continue

        raise ScraperError(
            "Failed to extract champion data from any bundle. "
            "The website structure may have changed significantly."
        )

    def save_to_csv(self, champions: list[Champion], output_path: Path | str | None = None) -> None:
        """
        Save scraped champions to CSV.

        Args:
            champions: List of champions to save
            output_path: Where to save. If None, uses default location.
        """
        if output_path is None:
            output_path = DATA_DIR / "champions_data.csv"

        save_champions_to_csv(champions, output_path, overwrite=True)
        self._log(f"Saved {len(champions)} champions to {output_path}")


def scrape_loldle_data(verbose: bool = True, save: bool = True) -> list[Champion]:
    """
    Convenience function to scrape loldle.net data.

    Args:
        verbose: Whether to print progress
        save: Whether to save to CSV

    Returns:
        List of scraped champions
    """
    scraper = LoldleScraper(verbose=verbose)
    champions = scraper.scrape_champions()

    if save:
        scraper.save_to_csv(champions)

    return champions
