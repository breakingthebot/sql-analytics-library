# tests/services/test_db_manager.py
# Tests for database connection, initialization, and query execution.
# Connects to: src/sql_analytics/services/db_manager.py
# Created: 2026-07-06

import pytest
import sqlite3
from pathlib import Path
from sql_analytics.services.db_manager import DBManager

@pytest.fixture
def temp_db_mgr(tmp_path):
    """Fixture to provide a DBManager pointing to a temporary sqlite database file."""
    temp_db_file = tmp_path / "test_ecommerce.db"
    return DBManager(db_path=temp_db_file)

def test_db_manager_initialization(temp_db_mgr):
    """Test that schema initialization creates expected tables."""
    temp_db_mgr.initialize_database()
    
    # Assert database file was created
    assert temp_db_mgr.db_path.exists()
    
    # Query sqlite_master to verify tables exist
    with temp_db_mgr.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        
    expected_tables = ["customers", "products", "orders", "order_items", "reviews", "inventory_logs"]
    for table in expected_tables:
        assert table in tables

def test_db_manager_populate_and_query(temp_db_mgr):
    """Test populating mock data and running queries."""
    temp_db_mgr.initialize_database()
    temp_db_mgr.populate_mock_data(num_customers=10, num_products=5, num_orders=15, seed=99)
    
    # Verify row counts
    cust_res = temp_db_mgr.execute_query("SELECT COUNT(*) as count FROM customers;")
    assert cust_res[0]["count"] == 10
    
    prod_res = temp_db_mgr.execute_query("SELECT COUNT(*) as count FROM products;")
    assert prod_res[0]["count"] == 5
    
    order_res = temp_db_mgr.execute_query("SELECT COUNT(*) as count FROM orders;")
    assert order_res[0]["count"] == 15

    # Run one of the analytical queries to ensure no syntax errors
    query = """
        SELECT c.segment, COUNT(o.order_id) as total_orders
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.segment;
    """
    res = temp_db_mgr.execute_query(query)
    assert len(res) > 0
    assert "segment" in res[0]
    assert "total_orders" in res[0]

def test_db_manager_query_formatted(temp_db_mgr):
    """Test pretty printed query execution results formatting."""
    temp_db_mgr.initialize_database()
    temp_db_mgr.populate_mock_data(num_customers=5, num_products=3, num_orders=5, seed=42)
    
    table_str = temp_db_mgr.execute_query_formatted("SELECT customer_id, email FROM customers;")
    assert "customer_id" in table_str
    assert "email" in table_str
    assert "@example.com" in table_str
