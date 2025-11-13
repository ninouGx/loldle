"""Data loading and management."""

from loldle.data.loader import (
    DataLoadError,
    filter_characters_by_prefix,
    get_character_by_name,
    load_champion_names,
    load_champions_from_csv,
    save_champions_to_csv,
)
from loldle.data.sources import (
    DataSourceError,
    GitHubDataSource,
    fetch_champions_from_best_source,
)

__all__ = [
    # Loaders
    "DataLoadError",
    "load_champions_from_csv",
    "load_champion_names",
    "save_champions_to_csv",
    "get_character_by_name",
    "filter_characters_by_prefix",
    # Sources
    "DataSourceError",
    "GitHubDataSource",
    "fetch_champions_from_best_source",
]
