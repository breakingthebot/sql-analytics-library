# src/sql_analytics/config/settings.py
# Application settings and configurations for the SQL Analytics query library.
# Connects to: None
# Created: 2026-07-06

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Default database directory
DEFAULT_DATA_DIR = BASE_DIR / "data"

# Default SQLite database path
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "ecommerce.db"

def get_db_path() -> Path:
    """
    Get the SQLite database path, resolving from environment variables if present.

    Returns:
        Path: Path to the SQLite database file.
    """
    db_env = os.getenv("SQL_ANALYTICS_DB_PATH")
    if db_env:
        return Path(db_env)
    return DEFAULT_DB_PATH
