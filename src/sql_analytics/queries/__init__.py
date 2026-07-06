# src/sql_analytics/queries/__init__.py
# Registry of analytical SQL queries.
# Connects to: None
# Created: 2026-07-06

from typing import Dict, List, Any

QUERIES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Top Customers by Lifetime Value (LTV)",
        "description": "Calculates the total spending (excluding shipping and applying discounts) for completed orders, ranking customers descending by their lifetime value.",
        "sql": """
            SELECT 
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                c.email,
                c.segment,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS lifetime_value
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Completed'
            GROUP BY c.customer_id, customer_name, c.email, c.segment
            ORDER BY lifetime_value DESC
            LIMIT 10;
        """
    },
    {
        "id": 2,
        "title": "Product Category Profit Margins",
        "description": "Analyzes the total revenue, wholesale cost, net profit, and profit margin percentage for each product category across all completed orders.",
        "sql": """
            SELECT 
                p.category,
                SUM(oi.quantity) AS units_sold,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue,
                ROUND(SUM(oi.quantity * p.cost), 2) AS total_cost,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * p.cost), 2) AS net_profit,
                ROUND(
                    ((SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * p.cost)) / 
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount))) * 100, 
                    2
                ) AS profit_margin_pct
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'Completed'
            GROUP BY p.category
            ORDER BY net_profit DESC;
        """
    },
    {
        "id": 3,
        "title": "Monthly Sales and Order Trends",
        "description": "Aggregates revenue, order volume, and Average Order Value (AOV) by month, showcasing sales trends.",
        "sql": """
            SELECT 
                strftime('%Y-%m', o.order_date) AS sales_month,
                COUNT(DISTINCT o.order_id) AS total_orders,
                SUM(oi.quantity) AS total_items_sold,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Completed'
            GROUP BY sales_month
            ORDER BY sales_month ASC;
        """
    }
]

def get_query_by_id(query_id: int) -> Dict[str, Any]:
    """
    Retrieve a query definition by its unique ID.

    Parameters:
        query_id (int): The ID of the query.

    Returns:
        Dict[str, Any]: The query definition dictionary.

    Raises:
        ValueError: If no query exists with the given ID.
    """
    for query in QUERIES:
        if query["id"] == query_id:
            return query
    raise ValueError(f"Query with ID {query_id} does not exist.")
