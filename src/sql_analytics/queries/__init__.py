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
        """
    },
    {
        "id": 11,
        "title": "Category Cross-Selling Patterns (Market Basket Analysis)",
        "description": "Identifies product categories frequently purchased together in the same order, ranking category pairs descending by purchase frequency.",
        "sql": """
            SELECT 
                p1.category AS category_a,
                p2.category AS category_b,
                COUNT(DISTINCT oi1.order_id) AS co_purchase_count
            FROM order_items oi1
            JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id != oi2.product_id
            JOIN products p1 ON oi1.product_id = p1.product_id
            JOIN products p2 ON oi2.product_id = p2.product_id
            WHERE p1.category < p2.category
            GROUP BY category_a, category_b
            ORDER BY co_purchase_count DESC;
        """
    },
    {
        "id": 12,
        "title": "Customer Value Tiering and Spend Percentile Ranking",
        "description": "Calculates customer lifetime spend, AOV, value tiers, and relative spending percentile ranks using PERCENT_RANK.",
        "sql": """
            WITH customer_stats AS (
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    c.segment,
                    COUNT(DISTINCT o.order_id) AS order_count,
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_spend
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE o.status = 'Completed'
                GROUP BY c.customer_id, c.segment
            )
            SELECT 
                customer_id,
                customer_name,
                segment,
                order_count,
                ROUND(total_spend, 2) AS total_spend,
                ROUND(total_spend / order_count, 2) AS aov,
                CASE 
                    WHEN total_spend >= 1500 THEN 'Platinum Tier'
                    WHEN total_spend >= 500 THEN 'Gold Tier'
                    WHEN total_spend >= 100 THEN 'Silver Tier'
                    ELSE 'Bronze Tier'
                END AS customer_value_tier,
                ROUND(PERCENT_RANK() OVER (ORDER BY total_spend) * 100, 1) AS spend_percentile
            FROM customer_stats
            ORDER BY total_spend DESC;
        """
    },
    {
        "id": 13,
        "title": "Product Review Ratings and Sales Volume Correlation",
        "description": "Combines product reviews with sales volumes to verify if higher-rated products drive higher unit volumes and revenues.",
        "sql": """
            SELECT 
                p.product_id,
                p.name AS product_name,
                p.category,
                p.price AS current_price,
                ROUND(AVG(r.rating), 2) AS avg_rating,
                COUNT(DISTINCT r.review_id) AS total_reviews,
                SUM(oi.quantity) AS total_units_sold,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_sales
            FROM products p
            LEFT JOIN reviews r ON p.product_id = r.product_id
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'Completed'
            GROUP BY p.product_id, p.name, p.category, p.price
            ORDER BY avg_rating DESC, total_sales DESC;
        """
    },
    {
        "id": 14,
        "title": "Stock Adjustment Log Auditing and Reorder Alerts",
        "description": "Audits the net inventory adjustments (sales vs restocks vs returns) over the last 90 days, flagging low stock.",
        "sql": """
            WITH product_stock_adjustments AS (
                SELECT 
                    product_id,
                    SUM(CASE WHEN reason = 'Restock' THEN change_quantity ELSE 0 END) AS total_restocked,
                    SUM(CASE WHEN reason = 'Sale' THEN change_quantity ELSE 0 END) AS total_sold,
                    SUM(CASE WHEN reason = 'Return' THEN change_quantity ELSE 0 END) AS total_returned,
                    SUM(change_quantity) AS net_90_day_change
                FROM inventory_logs
                WHERE logged_at >= datetime((SELECT MAX(logged_at) FROM inventory_logs), '-90 days')
                GROUP BY product_id
            )
            SELECT 
                p.product_id,
                p.name AS product_name,
                p.category,
                p.stock_quantity AS current_stock,
                COALESCE(psa.total_restocked, 0) AS units_restocked_90d,
                COALESCE(psa.total_sold, 0) AS units_sold_90d,
                COALESCE(psa.total_returned, 0) AS units_returned_90d,
                COALESCE(psa.net_90_day_change, 0) AS net_change_90d,
                CASE 
                    WHEN p.stock_quantity <= 15 THEN 'CRITICAL REORDER'
                    WHEN p.stock_quantity <= 35 THEN 'WARN: LOW STOCK'
                    ELSE 'Stock Level Healthy'
                END AS inventory_health_status
            FROM products p
            LEFT JOIN product_stock_adjustments psa ON p.product_id = psa.product_id
            ORDER BY p.stock_quantity ASC;
        """
    },
    {
        "id": 15,
        "title": "First-Time vs Repeat Customer Monthly Revenue Split",
        "description": "Tracks monthly revenue split and percentage contribution from new (first purchase) vs repeat buyers.",
        "sql": """
            WITH customer_orders_sequenced AS (
                SELECT 
                    customer_id,
                    order_id,
                    order_date,
                    strftime('%Y-%m', order_date) AS order_month,
                    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_sequence
                FROM orders
                WHERE status = 'Completed'
            ),
            order_revenues AS (
                SELECT 
                    cos.order_month,
                    cos.order_id,
                    cos.order_sequence,
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS order_value
                FROM customer_orders_sequenced cos
                JOIN order_items oi ON cos.order_id = oi.order_id
                GROUP BY cos.order_month, cos.order_id, cos.order_sequence
            ),
            monthly_splits AS (
                SELECT 
                    order_month,
                    ROUND(SUM(CASE WHEN order_sequence = 1 THEN order_value ELSE 0.0 END), 2) AS new_customer_revenue,
                    ROUND(SUM(CASE WHEN order_sequence > 1 THEN order_value ELSE 0.0 END), 2) AS repeat_customer_revenue,
                    ROUND(SUM(order_value), 2) AS total_revenue
                FROM order_revenues
                GROUP BY order_month
            )
            SELECT 
                order_month,
                new_customer_revenue,
                repeat_customer_revenue,
                total_revenue,
                ROUND((new_customer_revenue * 100.0) / total_revenue, 2) AS new_revenue_pct,
                ROUND((repeat_customer_revenue * 100.0) / total_revenue, 2) AS repeat_revenue_pct
            FROM monthly_splits
            ORDER BY order_month ASC;
        """
    },
    {
        "id": 16,
        "title": "Customer Review Response Speed and Rating Trend",
        "description": "Calculates the average days elapsed between customer order and review creation, grouped by segment and rating.",
        "sql": """
            SELECT 
                c.segment,
                r.rating,
                COUNT(r.review_id) AS review_count,
                ROUND(AVG(julianday(r.created_at) - julianday(o.order_date)), 1) AS avg_days_to_review
            FROM reviews r
            JOIN orders o ON r.customer_id = o.customer_id
            JOIN customers c ON r.customer_id = c.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id AND r.product_id = oi.product_id
            WHERE o.status = 'Completed'
            GROUP BY c.segment, r.rating
            ORDER BY c.segment ASC, r.rating DESC;
        """
    },
    {
        "id": 17,
        "title": "Product Lifecycle Sales Duration and Shelf-Life Velocity",
        "description": "Measures the lifespan in days between when a product was added to the catalog and its last sale date, along with daily sales velocity.",
        "sql": """
            WITH product_sales_lifecycle AS (
                SELECT 
                    oi.product_id,
                    MIN(o.order_date) AS first_sale,
                    MAX(o.order_date) AS last_sale,
                    SUM(oi.quantity) AS total_units_sold
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status = 'Completed'
                GROUP BY oi.product_id
            )
            SELECT 
                p.product_id,
                p.name AS product_name,
                p.category,
                strftime('%Y-%m-%d', p.created_at) AS date_added,
                ROUND(julianday(psl.last_sale) - julianday(p.created_at), 1) AS shelf_life_days,
                psl.total_units_sold,
                ROUND(psl.total_units_sold / (julianday(psl.last_sale) - julianday(p.created_at) + 1.0), 2) AS units_sold_per_day
            FROM products p
            JOIN product_sales_lifecycle psl ON p.product_id = psl.product_id
            ORDER BY units_sold_per_day DESC;
        """
    },
    {
        "id": 18,
        "title": "Category Monthly Cumulative Sales Progression",
        "description": "Calculates monthly revenue per category and calculates a running cumulative revenue progression using window functions.",
        "sql": """
            WITH category_monthly_sales AS (
                SELECT 
                    p.category,
                    strftime('%Y-%m', o.order_date) AS sales_month,
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS monthly_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status = 'Completed'
                GROUP BY p.category, sales_month
            )
            SELECT 
                category,
                sales_month,
                ROUND(monthly_revenue, 2) AS monthly_revenue,
                ROUND(SUM(monthly_revenue) OVER (
                    PARTITION BY category 
                    ORDER BY sales_month 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ), 2) AS cumulative_category_revenue
            FROM category_monthly_sales
            ORDER BY category ASC, sales_month ASC;
        """
    },
    {
        "id": 19,
        "title": "Customer Repeat Purchase Intervals and Loyalty Velocity",
        "description": "Calculates the average interval in days elapsed between orders 1-to-2 and 2-to-3 per customer, grouped by segment.",
        "sql": """
            WITH sequenced_orders AS (
                SELECT 
                    customer_id,
                    order_date,
                    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS seq
                FROM orders
                WHERE status = 'Completed'
            ),
            order_gaps AS (
                SELECT 
                    so1.customer_id,
                    julianday(so2.order_date) - julianday(so1.order_date) AS days_to_next_order,
                    so1.seq AS start_sequence
                FROM sequenced_orders so1
                JOIN sequenced_orders so2 ON so1.customer_id = so2.customer_id AND so2.seq = so1.seq + 1
            )
            SELECT 
                c.segment,
                COUNT(DISTINCT og.customer_id) AS customers_analyzed,
                ROUND(AVG(CASE WHEN og.start_sequence = 1 THEN og.days_to_next_order ELSE NULL END), 1) AS avg_days_order_1_to_2,
                ROUND(AVG(CASE WHEN og.start_sequence = 2 THEN og.days_to_next_order ELSE NULL END), 1) AS avg_days_order_2_to_3
            FROM order_gaps og
            JOIN customers c ON og.customer_id = c.customer_id
            GROUP BY c.segment
            ORDER BY c.segment ASC;
        """
    },
    {
        "id": 20,
        "title": "Product Category Penetration and Customer Cross-Shopping Ratio",
        "description": "Computes how many distinct categories each customer has bought from to calculate the category penetration ratio per segment.",
        "sql": """
            WITH customer_category_purchases AS (
                SELECT 
                    c.customer_id,
                    c.segment,
                    COUNT(DISTINCT p.category) AS distinct_categories_bought
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                LEFT JOIN products p ON oi.product_id = p.product_id
                GROUP BY c.customer_id, c.segment
            ),
            total_categories_count AS (
                SELECT COUNT(DISTINCT category) AS total_categories FROM products
            )
            SELECT 
                ccp.segment,
                COUNT(ccp.customer_id) AS customer_count,
                ROUND(AVG(ccp.distinct_categories_bought), 2) AS avg_distinct_categories_bought,
                (SELECT total_categories FROM total_categories_count) AS total_system_categories,
                ROUND(AVG(ccp.distinct_categories_bought) * 100.0 / (SELECT total_categories FROM total_categories_count), 1) AS category_penetration_ratio_pct
            FROM customer_category_purchases ccp
            GROUP BY ccp.segment
            ORDER BY category_penetration_ratio_pct DESC;
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
