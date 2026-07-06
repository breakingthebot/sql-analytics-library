# tests/test_cli.py
# Tests for CLI entry point and subcommands.
# Connects to: src/sql_analytics/cli.py
# Created: 2026-07-06

import pytest
import sys
import os
from unittest.mock import patch
from sql_analytics.cli import main
from sql_analytics import __version__

def test_cli_version(capsys):
    """Verify that calling the CLI with --version outputs version and exits."""
    with patch.object(sys, "argv", ["sql-analytics", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert f"sql-analytics v{__version__}" in captured.out or f"sql-analytics v{__version__}" in captured.err

def test_cli_list(capsys, tmp_path):
    """Verify that listing queries runs successfully."""
    # Use temporary DB path to avoid touching production data
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        with patch.object(sys, "argv", ["sql-analytics", "list"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Available Analytical Queries" in captured.out
            assert "Top Customers by Lifetime Value (LTV)" in captured.out
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]

def test_cli_db_init_and_run(capsys, tmp_path):
    """Verify that database initialization and running queries through CLI works."""
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        # 1. Test db-init command
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "10", "--products", "5", "--orders", "15"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Database initialized and populated successfully!" in captured.out
            
        # 2. Test db-status command
        with patch.object(sys, "argv", ["sql-analytics", "db-status"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Database Table Statistics" in captured.out
            assert "customers" in captured.out
            
        # 3. Test run command
        with patch.object(sys, "argv", ["sql-analytics", "run", "1"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Running Query 1: Top Customers by Lifetime Value (LTV)" in captured.out
            assert "lifetime_value" in captured.out
            
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]
