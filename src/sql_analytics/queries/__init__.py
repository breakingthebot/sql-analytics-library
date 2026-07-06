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
    },
    {
        "id": 4,
        "title": "Customer Purchase Frequency Distribution",
        "description": "Calculates the distribution of purchase counts across customers (how many completed orders customers have placed). Help find customer retention metrics.",
        "sql": """
            WITH customer_order_counts AS (
                SELECT 
                    customer_id,
                    COUNT(order_id) AS order_count
                FROM orders
                WHERE status = 'Completed'
                GROUP BY customer_id
            )
            SELECT 
                order_count AS completed_orders_per_customer,
                COUNT(customer_id) AS customer_count,
                ROUND(COUNT(customer_id) * 100.0 / (SELECT COUNT(*) FROM customer_order_counts), 2) AS customer_percentage
            FROM customer_order_counts
            GROUP BY order_count
            ORDER BY order_count ASC;
        """
    },
    {
        "id": 5,
        "title": "Monthly Customer Cohort Retention Rate",
        "description": "Calculates customer cohorts based on first purchase month, tracking subsequent monthly retention percentages over time.",
        "sql": """
            WITH customer_first_orders AS (
                SELECT 
                    customer_id,
                    MIN(order_date) AS first_order_date,
                    strftime('%Y-%m', MIN(order_date)) AS cohort_month
                FROM orders
                WHERE status = 'Completed'
                GROUP BY customer_id
            ),
            cohort_sizes AS (
                SELECT 
                    cohort_month,
                    COUNT(customer_id) AS cohort_size
                FROM customer_first_orders
                GROUP BY cohort_month
            ),
            customer_order_months AS (
                SELECT DISTINCT 
                    o.customer_id,
                    strftime('%Y-%m', o.order_date) AS order_month
                FROM orders o
                WHERE o.status = 'Completed'
            ),
            cohort_activity AS (
                SELECT 
                    cfo.cohort_month,
                    com.order_month,
                    (strftime('%Y', com.order_month) - strftime('%Y', cfo.cohort_month)) * 12 +
                    (strftime('%m', com.order_month) - strftime('%m', cfo.cohort_month)) AS month_number,
                    COUNT(DISTINCT com.customer_id) AS active_customers
                FROM customer_first_orders cfo
                JOIN customer_order_months com ON cfo.customer_id = com.customer_id
                GROUP BY cohort_month, order_month, month_number
            )
            SELECT 
                ca.cohort_month,
                cs.cohort_size,
                ca.month_number AS months_elapsed,
                ca.active_customers,
                ROUND((ca.active_customers * 100.0) / cs.cohort_size, 2) AS retention_rate_pct
            FROM cohort_activity ca
            JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
            ORDER BY ca.cohort_month ASC, ca.month_number ASC;
        """
    },
    {
        "id": 6,
        "title": "Average Days Between Purchases by Customer Segment",
        "description": "Uses LAG to measure the interval in days between consecutive completed orders per customer, grouped by customer segment.",
        "sql": """
            WITH ordered_customer_purchases AS (
                SELECT 
                    customer_id,
                    order_date,
                    LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date
                FROM orders
                WHERE status = 'Completed'
            ),
            purchase_gaps AS (
                SELECT 
                    ocp.customer_id,
                    c.segment,
                    julianday(ocp.order_date) - julianday(ocp.prev_order_date) AS days_between
                FROM ordered_customer_purchases ocp
                JOIN customers c ON ocp.customer_id = c.customer_id
                WHERE ocp.prev_order_date IS NOT NULL
            )
            SELECT 
                segment,
                COUNT(*) AS repeat_purchases_analyzed,
                ROUND(MIN(days_between), 1) AS min_days_between,
                ROUND(MAX(days_between), 1) AS max_days_between,
                ROUND(AVG(days_between), 1) AS avg_days_between
            FROM purchase_gaps
            GROUP BY segment
            ORDER BY avg_days_between ASC;
        """
    },
    {
        "id": 7,
        "title": "High-Velocity Inventory Stock Turnover Alert",
        "description": "Finds products whose stock levels are low relative to their daily sales velocity (units sold per day in the last 30 days).",
        "sql": """
            WITH product_sales_velocity AS (
                SELECT 
                    oi.product_id,
                    SUM(oi.quantity) AS units_sold_last_30_days,
                    SUM(oi.quantity) / 30.0 AS daily_sales_velocity
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status IN ('Completed', 'Pending') 
                  AND o.order_date >= datetime((SELECT MAX(order_date) FROM orders), '-30 days')
                GROUP BY oi.product_id
            )
            SELECT 
                p.product_id,
                p.name AS product_name,
                p.category,
                p.stock_quantity AS current_stock,
                COALESCE(psv.units_sold_last_30_days, 0) AS units_sold_last_30_days,
                ROUND(COALESCE(psv.daily_sales_velocity, 0.0), 2) AS daily_velocity,
                CASE 
                    WHEN COALESCE(psv.daily_sales_velocity, 0.0) = 0.0 THEN 'No Sales (Overstock)'
                    WHEN p.stock_quantity = 0 THEN 'Out of Stock'
                    ELSE CAST(ROUND(p.stock_quantity / psv.daily_sales_velocity, 1) AS TEXT)
                END AS days_stock_remaining
            FROM products p
            LEFT JOIN product_sales_velocity psv ON p.product_id = psv.product_id
            ORDER BY 
                CASE WHEN current_stock = 0 THEN 0 ELSE 1 END,
                CASE WHEN daily_velocity > 0 THEN current_stock / daily_velocity ELSE 9999 END ASC,
                current_stock ASC;
        """
    },
    {
        "id": 8,
        "title": "Product Return Rates and Profit Leakage Ranks",
        "description": "Calculates return rates per product and ranks products within their category based on total lost revenue from returned items.",
        "sql": """
            WITH category_totals AS (
                SELECT 
                    p.category,
                    COUNT(DISTINCT oi.order_id) AS total_orders,
                    SUM(oi.quantity) AS total_units_sold,
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_potential_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                JOIN orders o ON oi.order_id = o.order_id
                GROUP BY p.category
            ),
            product_returns AS (
                SELECT 
                    p.category,
                    p.product_id,
                    p.name AS product_name,
                    SUM(CASE WHEN o.status = 'Returned' THEN oi.quantity ELSE 0 END) AS returned_units,
                    SUM(oi.quantity) AS total_units,
                    SUM(CASE WHEN o.status = 'Returned' THEN oi.quantity * oi.unit_price * (1 - oi.discount) ELSE 0.0 END) AS lost_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                JOIN orders o ON oi.order_id = o.order_id
                GROUP BY p.category, p.product_id, p.name
            )
            SELECT 
                pr.category,
                pr.product_name,
                pr.returned_units,
                pr.total_units,
                ROUND((pr.returned_units * 100.0) / pr.total_units, 2) AS return_rate_pct,
                ROUND(pr.lost_revenue, 2) AS lost_revenue,
                DENSE_RANK() OVER (PARTITION BY pr.category ORDER BY pr.lost_revenue DESC) AS return_rank_in_category
            FROM product_returns pr
            WHERE pr.returned_units > 0
            ORDER BY pr.category ASC, lost_revenue DESC;
        """
    },
    {
        "id": 9,
        "title": "Rolling Customer Average Spend Trend",
        "description": "Uses frame window functions to calculate the rolling 3-order average transaction amount and order-to-order difference per customer.",
        "sql": """
            WITH customer_order_totals AS (
                SELECT 
                    o.customer_id,
                    o.order_id,
                    o.order_date,
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) + o.shipping_fee AS order_total
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY o.customer_id, o.order_id, o.order_date, o.shipping_fee
            )
            SELECT 
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                cot.order_id,
                cot.order_date,
                ROUND(cot.order_total, 2) AS order_total,
                ROUND(AVG(cot.order_total) OVER (
                    PARTITION BY cot.customer_id 
                    ORDER BY cot.order_date 
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ), 2) AS rolling_3_order_avg,
                ROUND(cot.order_total - LAG(cot.order_total, 1) OVER (
                    PARTITION BY cot.customer_id 
                    ORDER BY cot.order_date
                ), 2) AS diff_from_prev_order
            FROM customer_order_totals cot
            JOIN customers c ON cot.customer_id = c.customer_id
            ORDER BY c.customer_id ASC, cot.order_date ASC
            LIMIT 30;
        """
    },
    {
        "id": 10,
        "title": "Customer Revenue Pareto Analysis (80/20 Rule)",
        "description": "Calculates running cumulative revenue contribution to classify customers into core contributors (VIP/Pareto 80%) vs. long-tail.",
        "sql": """
            WITH customer_revenues AS (
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS customer_revenue
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE o.status = 'Completed'
                GROUP BY c.customer_id, customer_name
            ),
            revenue_ranks AS (
                SELECT 
                    customer_id,
                    customer_name,
                    customer_revenue,
                    SUM(customer_revenue) OVER (ORDER BY customer_revenue DESC) AS running_revenue,
                    SUM(customer_revenue) OVER () AS total_revenue
                FROM customer_revenues
            )
            SELECT 
                customer_id,
                customer_name,
                ROUND(customer_revenue, 2) AS customer_revenue,
                ROUND(running_revenue, 2) AS cumulative_revenue,
                ROUND((running_revenue * 100.0) / total_revenue, 2) AS cumulative_revenue_percentage,
                CASE 
                    WHEN (running_revenue * 100.0) / total_revenue <= 80.0 THEN 'Core 80% Contributor (VIP)'
                    ELSE 'Long-tail 20% Contributor'
                END AS pareto_classification
            FROM revenue_ranks
            ORDER BY customer_revenue DESC;
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
