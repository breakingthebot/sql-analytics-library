# src/sql_analytics/services/dashboard_generator.py
# HTML Dashboard generator service for e-commerce SQL analytics.
# Connects to: services/db_manager.py
# Created: 2026-07-06

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from sql_analytics.services.db_manager import DBManager

# HTML dashboard template incorporating premium dark glassmorphism design, Inter typography, Chart.js, and a cohort heatmap.
DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="SQL Analytics Executive Dashboard - E-commerce intelligence.">
    <title>E-commerce SQL Analytics Dashboard</title>
    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --primary: #8b5cf6;
            --secondary: #14b8a6;
            --warning: #f59e0b;
            --danger: #ef4444;
            --success: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.5;
            background-image: radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(20, 184, 166, 0.08) 0%, transparent 40%);
            background-attachment: fixed;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Header section */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }

        .header-title h1 {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            background: linear-gradient(135deg, #fff 30%, var(--text-muted) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-title p {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }

        .header-meta {
            text-align: right;
        }

        .badge {
            background-color: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.3);
            color: #c084fc;
            padding: 0.4rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 0.5rem;
        }

        .timestamp {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        /* KPI cards grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .kpi-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: rgba(139, 92, 246, 0.3);
        }

        .kpi-icon {
            width: 54px;
            height: 54px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            margin-right: 1.25rem;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .kpi-revenue .kpi-icon { color: var(--secondary); background: rgba(20, 184, 166, 0.1); border-color: rgba(20, 184, 166, 0.2); }
        .kpi-orders .kpi-icon { color: var(--primary); background: rgba(139, 92, 246, 0.1); border-color: rgba(139, 92, 246, 0.2); }
        .kpi-customers .kpi-icon { color: var(--warning); background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
        .kpi-aov .kpi-icon { color: var(--success); background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); }

        .kpi-content p {
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            margin-top: 0.25rem;
            letter-spacing: -0.02em;
        }

        /* General dashboard section cards */
        .section-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(12px);
            margin-bottom: 2rem;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .section-title i {
            margin-right: 0.5rem;
            color: var(--primary);
        }

        /* Charts panel layout */
        .charts-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        @media (max-width: 1024px) {
            .charts-row {
                grid-template-columns: 1fr;
            }
        }

        .chart-container {
            position: relative;
            height: 320px;
            width: 100%;
        }

        /* Custom Cohort Heatmap table styles */
        .table-responsive {
            width: 100%;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--card-border);
        }

        .cohort-table {
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            font-size: 0.85rem;
        }

        .cohort-table th, .cohort-table td {
            padding: 0.75rem;
            border: 1px solid var(--card-border);
        }

        .cohort-table th {
            background-color: rgba(15, 23, 42, 0.6);
            color: var(--text-muted);
            font-weight: 600;
        }

        .cohort-label {
            text-align: left;
            font-weight: 600;
            background-color: rgba(15, 23, 42, 0.3);
            color: var(--text-main);
            padding-left: 1rem !important;
        }

        .cohort-size {
            background-color: rgba(15, 23, 42, 0.2);
            color: var(--text-muted);
        }

        .heatmap-cell {
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .heatmap-cell:hover {
            filter: brightness(1.2);
            transform: scale(1.05);
            outline: 1px solid rgba(255, 255, 255, 0.4);
            z-index: 10;
            position: relative;
        }

        /* Two columns details row */
        .details-grid {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 900px) {
            .details-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Standard data tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            text-align: left;
        }

        .data-table th, .data-table td {
            padding: 0.85rem 1rem;
            border-bottom: 1px solid var(--card-border);
        }

        .data-table th {
            background-color: rgba(15, 23, 42, 0.4);
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }

        .data-table tr:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }

        .tier-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
        }

        .tier-platinum { background: rgba(20, 184, 166, 0.15); color: #2dd4bf; border: 1px solid rgba(20, 184, 166, 0.3); }
        .tier-gold { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .tier-silver { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
        .tier-bronze { background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }

        .stock-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.7rem;
            text-transform: uppercase;
            display: inline-block;
        }
        .stock-critical { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .stock-warn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .stock-healthy { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

    </style>
</head>
<body>
    <div class="container">
        <!-- Dashboard Header -->
        <header>
            <div class="header-title">
                <h1>E-commerce SQL Analytics</h1>
                <p>Advanced business intelligence and operational diagnostics extracted via raw queries.</p>
            </div>
            <div class="header-meta">
                <span class="badge"><i class="fa-solid fa-bolt"></i> Live Dataset</span>
                <div class="timestamp">Generated: <span id="gen-time">$generated_time</span></div>
            </div>
        </header>

        <!-- KPI Cards Grid -->
        <div class="kpi-grid">
            <!-- Total Revenue -->
            <div class="kpi-card kpi-revenue">
                <div class="kpi-icon"><i class="fa-solid fa-dollar-sign"></i></div>
                <div class="kpi-content">
                    <p>Total Net Revenue</p>
                    <div class="kpi-value">$$total_revenue</div>
                </div>
            </div>
            <!-- Completed Orders -->
            <div class="kpi-card kpi-orders">
                <div class="kpi-icon"><i class="fa-solid fa-cart-shopping"></i></div>
                <div class="kpi-content">
                    <p>Completed Orders</p>
                    <div class="kpi-value">$completed_orders</div>
                </div>
            </div>
            <!-- Total Customers -->
            <div class="kpi-card kpi-customers">
                <div class="kpi-icon"><i class="fa-solid fa-users"></i></div>
                <div class="kpi-content">
                    <p>Total Customers</p>
                    <div class="kpi-value">$total_customers</div>
                </div>
            </div>
            <!-- Average Order Value (AOV) -->
            <div class="kpi-card kpi-aov">
                <div class="kpi-icon"><i class="fa-solid fa-chart-line"></i></div>
                <div class="kpi-content">
                    <p>Avg Order Value</p>
                    <div class="kpi-value">$$avg_order_value</div>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="charts-row">
            <!-- Category Profit Margins Bar Chart -->
            <div class="section-card">
                <div class="section-title">
                    <span><i class="fa-solid fa-tags"></i> Category Performance & Profit Margins</span>
                </div>
                <div class="chart-container">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>

            <!-- Monthly Revenue and AOV Line Chart -->
            <div class="section-card">
                <div class="section-title">
                    <span><i class="fa-solid fa-calendar-days"></i> Monthly Sales & AOV Growth Trends</span>
                </div>
                <div class="chart-container">
                    <canvas id="salesTrendChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Cohort Retention Heatmap Section -->
        <div class="section-card">
            <div class="section-title">
                <span><i class="fa-solid fa-people-group"></i> Customer Cohort Retention Rate Matrix (%)</span>
            </div>
            <div class="table-responsive">
                <table class="cohort-table">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding-left: 1rem;">Cohort Month</th>
                            <th>Size</th>
                            <th>M0</th>
                            <th>M1</th>
                            <th>M2</th>
                            <th>M3</th>
                            <th>M4</th>
                            <th>M5</th>
                            <th>M6</th>
                            <th>M7</th>
                            <th>M8</th>
                            <th>M9</th>
                            <th>M10</th>
                            <th>M11</th>
                            <th>M12</th>
                        </tr>
                    </thead>
                    <tbody>
                        $cohort_rows
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Details Row (Top Customers & Stock Warnings) -->
        <div class="details-grid">
            <!-- Top Customers -->
            <div class="section-card">
                <div class="section-title">
                    <span><i class="fa-solid fa-trophy"></i> Top 10 Spending Customers (LTV Tiering)</span>
                </div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Segment</th>
                                <th>Orders</th>
                                <th>Total Spend</th>
                                <th>AOV</th>
                                <th>Value Tier</th>
                            </tr>
                        </thead>
                        <tbody>
                            $customer_rows
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Inventory Warnings -->
            <div class="section-card">
                <div class="section-title">
                    <span><i class="fa-solid fa-triangle-exclamation"></i> Low Stock & Reorder Audits</span>
                </div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Stock</th>
                                <th>Net 90d</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            $reorder_rows
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Inject data and set up charts -->
    <script>
        // Data injected from Python
        const categoryData = $category_json;
        const salesTrendData = $sales_trend_json;

        // 1. Setup Category Performance Chart
        const ctxCategory = document.getElementById('categoryChart').getContext('2d');
        new Chart(ctxCategory, {
            type: 'bar',
            data: {
                labels: categoryData.map(item => item.category),
                datasets: [
                    {
                        label: 'Revenue ($)',
                        data: categoryData.map(item => item.total_revenue),
                        backgroundColor: 'rgba(20, 184, 166, 0.6)',
                        borderColor: 'rgba(20, 184, 166, 1)',
                        borderWidth: 1.5,
                        borderRadius: 6
                    },
                    {
                        label: 'Net Profit ($)',
                        data: categoryData.map(item => item.net_profit),
                        backgroundColor: 'rgba(139, 92, 246, 0.6)',
                        borderColor: 'rgba(139, 92, 246, 1)',
                        borderWidth: 1.5,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { family: 'Inter' } }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });

        // 2. Setup Sales Trend Chart
        const ctxSales = document.getElementById('salesTrendChart').getContext('2d');
        new Chart(ctxSales, {
            type: 'line',
            data: {
                labels: salesTrendData.map(item => item.sales_month),
                datasets: [
                    {
                        type: 'bar',
                        label: 'Total Revenue ($)',
                        data: salesTrendData.map(item => item.total_revenue),
                        backgroundColor: 'rgba(139, 92, 246, 0.25)',
                        borderColor: 'rgba(139, 92, 246, 0.8)',
                        borderWidth: 2,
                        borderRadius: 4,
                        yAxisID: 'y'
                    },
                    {
                        type: 'line',
                        label: 'Avg Order Value ($)',
                        data: salesTrendData.map(item => item.avg_order_value),
                        borderColor: '#14b8a6',
                        backgroundColor: 'rgba(20, 184, 166, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#14b8a6',
                        tension: 0.3,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { family: 'Inter' } }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y1: {
                        position: 'right',
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

class DashboardGenerator:
    """
    Handles extracting aggregate SQL metrics and compiling an interactive HTML/CSS portfolio dashboard.
    """

    def __init__(self, db_manager: DBManager):
        """
        Initialize the dashboard generator.

        Parameters:
            db_manager (DBManager): Database manager service.
        """
        self.db = db_manager

    def generate_html(self, output_path: Path) -> None:
        """
        Query the database, fetch aggregate trends, and write a styled dashboard page.

        Parameters:
            output_path (Path): Path to write the dashboard HTML file.
        """
        # 1. Fetch KPI metrics (Completed orders only)
        kpi_query = """
            SELECT 
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Completed';
        """
        kpis = self.db.execute_query(kpi_query)[0]
        completed_orders = kpis["total_orders"] or 0
        total_revenue = kpis["total_revenue"] or 0.0
        avg_order_value = round(total_revenue / completed_orders, 2) if completed_orders > 0 else 0.0

        cust_count = self.db.execute_query("SELECT COUNT(*) AS count FROM customers;")[0]["count"]

        # 2. Fetch Category Profit Margins (Query 2 logic)
        cat_query = """
            SELECT 
                p.category,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * p.cost), 2) AS net_profit
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'Completed'
            GROUP BY p.category
            ORDER BY total_revenue DESC;
        """
        categories_data = self.db.execute_query(cat_query)

        # 3. Fetch Monthly Sales and Order Trends (Query 3 logic)
        trend_query = """
            SELECT 
                strftime('%Y-%m', o.order_date) AS sales_month,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Completed'
            GROUP BY sales_month
            ORDER BY sales_month ASC;
        """
        sales_trend_data = self.db.execute_query(trend_query)

        # 4. Fetch Customer Value Tiering (Query 12 logic - Top 10)
        cust_tier_query = """
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
                END AS customer_value_tier
            FROM customer_stats
            ORDER BY total_spend DESC
            LIMIT 10;
        """
        top_customers = self.db.execute_query(cust_tier_query)

        customer_rows_html = ""
        for cust in top_customers:
            tier_class = cust["customer_value_tier"].lower().split()[0]
            customer_rows_html += f"""
                <tr>
                    <td>{cust['customer_name']}</td>
                    <td>{cust['segment']}</td>
                    <td>{cust['order_count']}</td>
                    <td>${cust['total_spend']:,}</td>
                    <td>${cust['aov']:,}</td>
                    <td><span class="tier-badge tier-{tier_class}">{cust['customer_value_tier']}</span></td>
                </tr>
            """

        # 5. Fetch Reorder Warnings (Query 14 logic)
        reorder_query = """
            WITH product_stock_adjustments AS (
                SELECT 
                    product_id,
                    SUM(change_quantity) AS net_90_day_change
                FROM inventory_logs
                WHERE logged_at >= datetime((SELECT MAX(logged_at) FROM inventory_logs), '-90 days')
                GROUP BY product_id
            )
            SELECT 
                p.name AS product_name,
                p.stock_quantity AS current_stock,
                COALESCE(psa.net_90_day_change, 0) AS net_change_90d,
                CASE 
                    WHEN p.stock_quantity <= 15 THEN 'CRITICAL REORDER'
                    WHEN p.stock_quantity <= 35 THEN 'WARN: LOW STOCK'
                    ELSE 'Stock Level Healthy'
                END AS inventory_health_status
            FROM products p
            LEFT JOIN product_stock_adjustments psa ON p.product_id = psa.product_id
            ORDER BY p.stock_quantity ASC
            LIMIT 8;
        """
        reorders = self.db.execute_query(reorder_query)

        reorder_rows_html = ""
        for item in reorders:
            status = item["inventory_health_status"]
            badge_class = "stock-critical" if "CRITICAL" in status else ("stock-warn" if "WARN" in status else "stock-healthy")
            reorder_rows_html += f"""
                <tr>
                    <td>{item['product_name']}</td>
                    <td>{item['current_stock']}</td>
                    <td>{item['net_change_90d']}</td>
                    <td><span class="stock-badge {badge_class}">{status}</span></td>
                </tr>
            """

        # 6. Fetch Monthly Customer Cohort Retention (Query 5 logic)
        cohort_query = """
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
                    (strftime('%Y', com.order_month) - strftime('%Y', cfo.cohort_month)) * 12 +
                    (strftime('%m', com.order_month) - strftime('%m', cfo.cohort_month)) AS month_number,
                    COUNT(DISTINCT com.customer_id) AS active_customers
                FROM customer_first_orders cfo
                JOIN customer_order_months com ON cfo.customer_id = com.customer_id
                GROUP BY cohort_month, month_number
            )
            SELECT 
                ca.cohort_month,
                cs.cohort_size,
                ca.month_number,
                ca.active_customers,
                ROUND((ca.active_customers * 100.0) / cs.cohort_size, 2) AS retention_rate_pct
            FROM cohort_activity ca
            JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
            ORDER BY ca.cohort_month ASC, ca.month_number ASC;
        """
        cohort_raw = self.db.execute_query(cohort_query)

        # Build pivot structure for cohort retention heatmap
        cohorts: Dict[str, Dict[str, Any]] = {}
        for row in cohort_raw:
            month = row["cohort_month"]
            if month not in cohorts:
                cohorts[month] = {
                    "size": row["cohort_size"],
                    "months": {}
                }
            cohorts[month]["months"][row["month_number"]] = row["retention_rate_pct"]

        cohort_rows_html = ""
        for cohort_month, cdata in sorted(cohorts.items()):
            size = cdata["size"]
            row_html = f'<tr><td class="cohort-label">{cohort_month}</td><td class="cohort-size">{size}</td>'
            
            for m in range(13): # M0 to M12
                val = cdata["months"].get(m)
                if val is not None:
                    # HSL color formatting: higher retention rate = darker teal
                    opacity = max(0.05, min(1.0, val / 100.0))
                    # Purple theme background color gradient matching CSS vars
                    bg_color = f"rgba(139, 92, 246, {opacity:.2f})"
                    row_html += f'<td class="heatmap-cell" style="background-color: {bg_color}; color: #fff;">{val}%</td>'
                else:
                    row_html += '<td>-</td>'
            row_html += '</tr>'
            cohort_rows_html += row_html

        # 7. Substitute placeholders in template
        html_content = DASHBOARD_TEMPLATE
        html_content = html_content.replace("$generated_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html_content = html_content.replace("$total_revenue", f"{total_revenue:,.2f}")
        html_content = html_content.replace("$completed_orders", f"{completed_orders:,}")
        html_content = html_content.replace("$total_customers", f"{cust_count:,}")
        html_content = html_content.replace("$avg_order_value", f"{avg_order_value:,.2f}")
        html_content = html_content.replace("$customer_rows", customer_rows_html)
        html_content = html_content.replace("$reorder_rows", reorder_rows_html)
        html_content = html_content.replace("$cohort_rows", cohort_rows_html)
        html_content = html_content.replace("$category_json", json.dumps(categories_data))
        html_content = html_content.replace("$sales_trend_json", json.dumps(sales_trend_data))

        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")
