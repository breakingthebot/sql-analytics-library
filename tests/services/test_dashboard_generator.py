# tests/services/test_dashboard_generator.py
# Tests for HTML dashboard generator service.
# Connects to: src/sql_analytics/services/dashboard_generator.py
# Created: 2026-07-06

import pytest
from pathlib import Path
from sql_analytics.services.db_manager import DBManager
from sql_analytics.services.dashboard_generator import DashboardGenerator

def test_dashboard_generation(temp_db_mgr, tmp_path):
    """Test that the dashboard generator fetches data and outputs a valid HTML file."""
    temp_db_mgr.initialize_database()
    temp_db_mgr.populate_mock_data(num_customers=10, num_products=5, num_orders=15, seed=42)
    
    out_html = tmp_path / "dashboard.html"
    
    generator = DashboardGenerator(temp_db_mgr)
    generator.generate_html(out_html)
    
    assert out_html.exists()
    content = out_html.read_text(encoding="utf-8")
    
    # Assert key HTML structure exists
    assert "<!DOCTYPE html>" in content
    assert "E-commerce SQL Analytics Dashboard" in content
    assert "Generated:" in content
    
    # Assert JSON-embedded data exists
    assert "const categoryData =" in content
    assert "const salesTrendData =" in content
    
    # Assert cohort retention rows exist
    assert "cohort-table" in content
    assert "M0" in content
    
    # Assert LTV customer tier badges exist
    assert "tier-badge" in content
