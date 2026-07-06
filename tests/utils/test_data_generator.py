# tests/utils/test_data_generator.py
# Tests for mock data generation utility.
# Connects to: src/sql_analytics/utils/data_generator.py
# Created: 2026-07-06

from datetime import datetime
from sql_analytics.utils.data_generator import generate_mock_data

def test_generate_mock_data_sizes():
    """Verify that generated data scales to requested limits."""
    data = generate_mock_data(num_customers=20, num_products=5, num_orders=30, seed=123)
    
    assert "customers" in data
    assert "products" in data
    assert "orders" in data
    assert "order_items" in data
    assert "reviews" in data
    assert "inventory_logs" in data
    
    # Assert counts
    assert len(data["customers"]) == 20
    assert len(data["products"]) == 5
    assert len(data["orders"]) == 30

def test_generate_mock_data_integrity():
    """Verify that relational keys and dates have logical consistency."""
    data = generate_mock_data(num_customers=10, num_products=10, num_orders=20, seed=42)
    
    cust_ids = {c["customer_id"] for c in data["customers"]}
    prod_ids = {p["product_id"] for p in data["products"]}
    order_ids = {o["order_id"] for o in data["orders"]}
    
    # Check that all order customer_ids link to valid customers
    for order in data["orders"]:
        assert order["customer_id"] in cust_ids
        assert isinstance(order["order_date"], datetime)
        
    # Check order items
    for item in data["order_items"]:
        assert item["order_id"] in order_ids
        assert item["product_id"] in prod_ids
        assert item["quantity"] > 0
        assert item["unit_price"] > 0
        assert 0.0 <= item["discount"] <= 1.0
        
    # Check inventory logs match products
    for log in data["inventory_logs"]:
        assert log["product_id"] in prod_ids
        assert log["reason"] in ["Restock", "Sale", "Return", "Adjustment"]
        assert isinstance(log["logged_at"], datetime)

def test_generate_mock_data_seasonal():
    """Verify that seasonal trends data generation runs without errors and produces valid dates."""
    data = generate_mock_data(num_customers=10, num_products=5, num_orders=20, seed=42, seasonal_trends=True)
    
    assert "orders" in data
    assert len(data["orders"]) == 20
    
    for order in data["orders"]:
        assert isinstance(order["order_date"], datetime)
        assert order["order_date"] <= datetime.now()
