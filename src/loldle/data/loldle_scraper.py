"""
Direct loldle.net scraper for getting CURRENT 2025 champion data.

This scraper gets data directly from loldle.net's live website,
ensuring we have the most up-to-date champions including 2024-2025 releases.
"""

from __future__ import annotations

import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from loldle.models.lol import Champion


class LoldleWebScraper:
    """Scrape champion data directly from loldle.net."""

    BASE_URL = "https://loldle.net"
    CLASSIC_URL = f"{BASE_URL}/classic"
    TIMEOUT = 30

    def __init__(self, verbose: bool = False) -> None:
        """Initialize scraper."""
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def _log(self, message: str) -> None:
        """Print if verbose."""
        if self.verbose:
            print(f"[Loldle Scraper] {message}")

    def fetch_page_html(self) -> str:
        """Fetch the main loldle.net page."""
        self._log(f"Fetching {self.CLASSIC_URL}...")
        try:
            response = self.session.get(self.CLASSIC_URL, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch loldle.net: {e}")

    def extract_js_from_html(self, html: str) -> list[str]:
        """Extract all JavaScript file URLs from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script", src=True)

        js_urls = []
        for script in scripts:
            src = script.get("src", "")
            if src:
                # Make absolute URL
                if src.startswith("//"):
                    src = f"https:{src}"
                elif src.startswith("/"):
                    src = f"{self.BASE_URL}{src}"
                elif not src.startswith("http"):
                    src = f"{self.BASE_URL}/{src}"

                js_urls.append(src)

        return js_urls

    def fetch_js_file(self, url: str) -> str:
        """Fetch a JavaScript file."""
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self._log(f"Failed to fetch {url}: {e}")
            return ""

    def extract_champion_data_from_js(self, js_content: str) -> list[dict[str, Any]] | None:
        """
        Extract champion data from JavaScript code.

        Loldle embeds champion data as a JavaScript array/object.
        We need to find and parse it.
        """
        # Try different patterns to find champion data
        patterns = [
            # Look for large arrays with champion-like objects
            r'(\[\{[^\]]{100,}championId[^\]]+\}\])',
            r'(\[\{[^\]]{100,}championName[^\]]+\}\])',
            r'(\[\{[^\]]{100,}name[^\]]+gender[^\]]+\}\])',
            # Look for variable assignments
            r'(?:const|let|var)\s+\w+\s*=\s*(\[\{[^\]]{100,}gender[^\]]+\}\])',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.DOTALL | re.IGNORECASE)

            for match in matches:
                # Try to extract valid JSON from the match
                # Clean up and try to parse
                try:
                    # Sometimes the match includes extra characters, clean it
                    json_str = match

                    # Try to find the actual JSON array bounds
                    start = json_str.find('[')
                    if start == -1:
                        continue

                    # Find matching closing bracket
                    bracket_count = 0
                    end = -1
                    for i in range(start, len(json_str)):
                        if json_str[i] == '[':
                            bracket_count += 1
                        elif json_str[i] == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end = i + 1
                                break

                    if end == -1:
                        continue

                    json_str = json_str[start:end]

                    # Try to parse
                    data = json.loads(json_str)

                    if isinstance(data, list) and len(data) > 100:  # Should have 160+ champions
                        # Validate it looks like champion data
                        if all(isinstance(item, dict) for item in data):
                            sample = data[0]
                            # Check for champion-like fields
                            if any(key in sample for key in ['championName', 'name', 'championId']) and \
                               any(key in sample for key in ['gender', 'Gender']):
                                self._log(f"Found {len(data)} champions in JavaScript!")
                                return data

                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue

        return None

    def parse_champion_data(self, raw_data: dict[str, Any]) -> Champion | None:
        """Parse raw champion data into Champion object."""
        try:
            # Handle different possible field names
            name = (raw_data.get("championName") or
                   raw_data.get("name") or
                   raw_data.get("championId") or "")

            if not name:
                return None

            gender = raw_data.get("gender", "")

            # Positions
            positions = raw_data.get("positions", raw_data.get("position", []))
            if isinstance(positions, str):
                positions = [positions]

            # Species
            species = raw_data.get("species", [])
            if isinstance(species, str):
                species = [species]

            resource = raw_data.get("resource", "")

            # Range type
            range_type = raw_data.get("rangeType", raw_data.get("range_type", raw_data.get("range", [])))
            if isinstance(range_type, str):
                range_type = [range_type]

            # Regions
            regions = raw_data.get("regions", raw_data.get("region", []))
            if isinstance(regions, str):
                regions = [regions]

            # Release year - might be in different formats
            release_year = raw_data.get("releaseYear", raw_data.get("release_year", 0))
            if isinstance(release_year, str):
                # Might be a date string like "2022-01-15"
                release_year = int(release_year.split("-")[0])
            else:
                release_year = int(release_year) if release_year else 0

            return Champion(
                name=name,
                gender=gender,
                positions=positions if isinstance(positions, list) else [],
                species=species if isinstance(species, list) else [],
                resource=resource,
                range_types=range_type if isinstance(range_type, list) else [],
                regions=regions if isinstance(regions, list) else [],
                release_year=release_year,
            )

        except Exception as e:
            self._log(f"Failed to parse champion: {e}")
            return None

    def scrape_champions(self) -> list[Champion]:
        """
        Scrape all current champions from loldle.net.

        Returns:
            List of Champion objects with current data
        """
        self._log("Starting loldle.net scrape for CURRENT data...")

        # Fetch main page
        html = self.fetch_page_html()

        # Extract JavaScript URLs
        js_urls = self.extract_js_from_html(html)
        self._log(f"Found {len(js_urls)} JavaScript files")

        # Try each JS file to find champion data
        for js_url in js_urls:
            # Skip external libraries
            if any(lib in js_url.lower() for lib in ['jquery', 'bootstrap', 'google', 'analytics']):
                continue

            self._log(f"Checking: {js_url}")
            js_content = self.fetch_js_file(js_url)

            if not js_content:
                continue

            # Try to extract champion data
            champion_data = self.extract_champion_data_from_js(js_content)

            if champion_data:
                # Parse into Champion objects
                champions = []
                for raw_champ in champion_data:
                    champ = self.parse_champion_data(raw_champ)
                    if champ:
                        champions.append(champ)

                if champions:
                    self._log(f"Successfully scraped {len(champions)} champions from loldle.net!")
                    return champions

        raise Exception(
            "Could not extract champion data from loldle.net. "
            "The website structure may have changed. "
            "Falling back to community sources is recommended."
        )


def scrape_current_loldle_data(verbose: bool = True) -> list[Champion]:
    """
    Scrape current champion data directly from loldle.net.

    Args:
        verbose: Whether to print progress

    Returns:
        List of Champion objects with 2025 data
    """
    scraper = LoldleWebScraper(verbose=verbose)
    return scraper.scrape_champions()
