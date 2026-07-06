# tests/services/test_repl_shell.py
# Tests for interactive REPL shell.
# Connects to: src/sql_analytics/services/repl_shell.py
# Created: 2026-07-06

import pytest
from unittest.mock import patch
from sql_analytics.services.repl_shell import REPLShell

def test_repl_shell_commands(temp_db_mgr, capsys):
    """Test that special commands like .help, .list, and .exit behave correctly in the shell."""
    temp_db_mgr.initialize_database()
    temp_db_mgr.populate_mock_data(num_customers=5, num_products=3, num_orders=5, seed=42)
    
    shell = REPLShell(temp_db_mgr)
    
    # Mock inputs: list tables, show help, set format, run query, then exit
    inputs = [".help", ".list", ".format csv", ".queries", ".run 1", ".exit"]
    
    with patch("builtins.input", side_effect=inputs):
        shell.run()
        
    captured = capsys.readouterr()
    
    # Assert startup banner exists
    assert "E-commerce SQL Analytics Interactive Shell" in captured.out
    
    # Assert commands output exists
    assert "Available Shell Commands:" in captured.out  # from .help
    assert "Database Tables:" in captured.out           # from .list
    assert "customers" in captured.out                  # from .list
    assert "[+] Output format changed to: 'csv'" in captured.out # from .format csv
    assert "Pre-registered Analytical Queries:" in captured.out # from .queries
    assert "Running Query 1:" in captured.out           # from .run 1
    assert "customer_id" in captured.out                # from .run 1 (CSV output header)
    assert "Goodbye!" in captured.out                  # from .exit
