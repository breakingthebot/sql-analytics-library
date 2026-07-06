# tests/conftest.py
# Shared pytest fixtures for testing the SQL Analytics library.
# Created: 2026-07-06

import pytest
from sql_analytics.services.db_manager import DBManager

@pytest.fixture
def temp_db_mgr(tmp_path):
    """Fixture to provide a DBManager pointing to a temporary sqlite database file."""
    temp_db_file = tmp_path / "test_ecommerce.db"
    return DBManager(db_path=temp_db_file)
