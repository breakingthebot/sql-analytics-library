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

def test_cli_output_formats(capsys, tmp_path):
    """Verify that specifying different formats (csv, json, markdown) alters the output layout."""
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        # Initialize
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "5", "--products", "3", "--orders", "5"]):
            with pytest.raises(SystemExit):
                main()
        
        # Test JSON format
        with patch.object(sys, "argv", ["sql-analytics", "run", "1", "--format", "json"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert '"lifetime_value":' in captured.out
            assert '[' in captured.out
            assert ']' in captured.out
            
        # Test CSV format
        with patch.object(sys, "argv", ["sql-analytics", "run", "1", "--format", "csv"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert 'customer_id' in captured.out
            assert 'lifetime_value' in captured.out
            
        # Test Markdown format
        with patch.object(sys, "argv", ["sql-analytics", "run", "1", "--format", "markdown"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert 'customer_id' in captured.out
            assert '|' in captured.out
            
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]

def test_cli_output_file(capsys, tmp_path):
    """Verify that writing output to a file works and creates the target file."""
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        # Initialize
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "5", "--products", "3", "--orders", "5"]):
            with pytest.raises(SystemExit):
                main()
        
        out_csv = tmp_path / "exports" / "ltv_report.csv"
        
        # Run and save to out_csv
        with patch.object(sys, "argv", ["sql-analytics", "run", "1", "--format", "csv", "--output", str(out_csv)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Results successfully exported to:" in captured.out
            
        # Assert file exists and contains CSV headers
        assert out_csv.exists()
        content = out_csv.read_text(encoding="utf-8")
        assert "customer_id" in content
        assert "lifetime_value" in content
        
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]

def test_cli_benchmark(capsys, tmp_path):
    """Verify that calling the CLI 'benchmark' subcommand runs the profiler and prints tables."""
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        # Initialize
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "5", "--products", "3", "--orders", "5"]):
            with pytest.raises(SystemExit):
                main()
        
        # Test default benchmark run
        with patch.object(sys, "argv", ["sql-analytics", "benchmark", "--iterations", "1"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Running performance benchmark across all registered queries..." in captured.out
            assert "query_id" in captured.out
            assert "avg_ms" in captured.out

        # Test CSV benchmark output to file
        out_csv = tmp_path / "benchmark_report.csv"
        with patch.object(sys, "argv", ["sql-analytics", "benchmark", "--iterations", "1", "--format", "csv", "--output", str(out_csv)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            
        assert out_csv.exists()
        content = out_csv.read_text(encoding="utf-8")
        assert "query_id,title,runs,min_ms,max_ms,avg_ms" in content or "query_id,title,runs,min_ms,max_ms,avg_ms" in content.replace('"', '')

    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]

def test_cli_dashboard(capsys, tmp_path):
    """Verify that calling the CLI 'dashboard' subcommand creates the HTML report."""
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        # Initialize
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "5", "--products", "3", "--orders", "5"]):
            with pytest.raises(SystemExit):
                main()
        
        out_html = tmp_path / "reports" / "dashboard.html"
        
        # Run dashboard command
        with patch.object(sys, "argv", ["sql-analytics", "dashboard", "--output", str(out_html)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Generating executive SQL analytics dashboard..." in captured.out
            assert "Dashboard successfully generated at:" in captured.out
            
        assert out_html.exists()
        content = out_html.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]

def test_cli_db_init_seasonal(capsys, tmp_path):
    """Verify that database initialization and seeding works with the --seasonal flag."""
    temp_db = tmp_path / "cli_seasonal_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "10", "--products", "5", "--orders", "15", "--seasonal"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Database initialized and populated successfully!" in captured.out
            
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]

def test_cli_shell(capsys, tmp_path):
    """Verify that calling the CLI 'shell' subcommand launches the interactive REPL."""
    temp_db = tmp_path / "cli_test.db"
    os.environ["SQL_ANALYTICS_DB_PATH"] = str(temp_db)
    
    try:
        # Initialize
        with patch.object(sys, "argv", ["sql-analytics", "db-init", "--customers", "5", "--products", "3", "--orders", "5"]):
            with pytest.raises(SystemExit):
                main()
        
        # Run shell command with mock quit input
        with patch("builtins.input", side_effect=[".exit"]):
            with patch.object(sys, "argv", ["sql-analytics", "shell"]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                assert "E-commerce SQL Analytics Interactive Shell" in captured.out
                assert "Goodbye!" in captured.out
                
    finally:
        del os.environ["SQL_ANALYTICS_DB_PATH"]
