# tests/models/test_schema.py
# Tests for schema definition integrity.
# Connects to: src/sql_analytics/models/schema.py
# Created: 2026-07-06

from sql_analytics.models.schema import CREATE_TABLES_SQL, DROP_TABLES_SQL

def test_schema_sql_present():
    """Verify that schema DDL queries list is populated and structured correctly."""
    assert len(CREATE_TABLES_SQL) > 0
    assert len(DROP_TABLES_SQL) > 0
    
    # Check that key tables are included in creation SQL
    creation_strings = "".join(CREATE_TABLES_SQL).lower()
    assert "create table customers" in creation_strings
    assert "create table products" in creation_strings
    assert "create table orders" in creation_strings
    assert "create table order_items" in creation_strings
    assert "create table reviews" in creation_strings
    assert "create table inventory_logs" in creation_strings
