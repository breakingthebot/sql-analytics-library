# tests/config/test_settings.py
# Tests for application configuration settings.
# Connects to: src/sql_analytics/config/settings.py
# Created: 2026-07-06

import os
from pathlib import Path
from sql_analytics.config.settings import get_db_path, DEFAULT_DB_PATH

def test_get_db_path_default():
    """Verify that get_db_path returns the default path when no env var is set."""
    if "SQL_ANALYTICS_DB_PATH" in os.environ:
        del os.environ["SQL_ANALYTICS_DB_PATH"]
    assert get_db_path() == DEFAULT_DB_PATH

def test_get_db_path_override(tmp_path):
    """Verify that get_db_path respects SQL_ANALYTICS_DB_PATH environment variable."""
    temp_db = tmp_path / "temp_ecommerce.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    try:
        assert get_db_path() == temp_db
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]
