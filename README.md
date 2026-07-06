# SQL Analytics Query Library

A Python library containing complex analytical SQL queries against an e-commerce database, complete with a realistic mock data generator and interactive CLI runner.

## Stack
- **Language**: Python 3.8+ (Tested on Python 3.12.9)
- **Key libraries**: `tabulate` (formatting outputs), `pytest` & `pytest-cov` (automated testing)
- **Database**: SQLite3

## Setup
Follow these steps to set up the library on your local machine:
1. Clone the repository and navigate into the root directory.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - On Windows (Command Prompt):
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
4. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Environment Variables
- `SQL_ANALYTICS_DB_PATH`: Custom path to the SQLite database file. If not provided, it defaults to `data/ecommerce.db` inside the project root directory.

Refer to `.env.example` for details (none needed for standard defaults).

## Running Locally
Here are the exact CLI commands to run the application:

1. **Initialize and Seed Database**:
   Generates a schema and populates it with realistic mock records.
   ```bash
   sql-analytics db-init --seasonal
   ```
   *Options*:
   - `--customers <count>`: Number of customers to generate (default: 100).
   - `--products <count>`: Number of products to generate (default: 30).
   - `--orders <count>`: Number of orders to generate (default: 300).
   - `--seasonal`: Skews transaction date generation using seasonal weights (simulating holiday shopping spikes and summer sales cycles).

2. **Check Database Status**:
   Print table names and row counts to verify data integrity.
   ```bash
   sql-analytics db-status
   ```

3. **List Available Queries**:
   Show all registered analytical queries.
   ```bash
   sql-analytics list
   ```

4. **Execute Analytical Query**:
   Execute a specific query by its unique ID.
   ```bash
   sql-analytics run 1
   ```
   *Options*:
   - `--verbose`: Print the raw SQL query statement before running.
   - `--format` or `-f`: Specify output format (`table` [default], `csv`, `json`, `markdown`).
     - E.g., `sql-analytics run 1 -f json`
   - `--output` or `-o`: Export results directly to a local file.
     - E.g., `sql-analytics run 1 -f csv -o reports/ltv_report.csv`

5. **Benchmark Query Performance**:
   Measure latency and generate run-time statistics for all 20 queries.
   ```bash
   sql-analytics benchmark --iterations 5
   ```
   *Options*:
   - `--iterations` or `-i`: The number of benchmark runs per query (default: 5).
   - `--format` or `-f`: Specify stats table format (`table` [default], `csv`, `json`, `markdown`).
   - `--output` or `-o`: Export benchmark metrics to a local file path.
     - E.g., `sql-analytics benchmark -f json -o benchmark_report.json`

6. **Generate Executive HTML Dashboard**:
   Extract core aggregates and compile a premium interactive web dashboard report.
   ```bash
   sql-analytics dashboard --output reports/dashboard.html
   ```
   *Options*:
   - `--output` or `-o`: Configure the target HTML file path (default: `reports/dashboard.html`).

7. **Run Automated Tests**:
   ```bash
   pytest --basetemp=tests/tmp
   ```

## Analytical Queries
The library currently includes the following 20 complex analytical queries:
1. **Top Customers by Lifetime Value (LTV)**: Ranks customers by their lifetime spending on completed orders.
2. **Product Category Profit Margins**: Analyzes margins, cost, revenue, and units sold by category.
3. **Monthly Sales and Order Trends**: Tracks month-over-month revenue growth and Average Order Value (AOV).
4. **Customer Purchase Frequency Distribution**: Tracks the distribution of orders per customer to view retention.
5. **Monthly Customer Cohort Retention Rate**: Tracks cohort activity month-over-month using complex date calculations.
6. **Average Days Between Purchases by Customer Segment**: Tracks buy-cycle intervals using the `LAG` window function.
7. **High-Velocity Inventory Stock Turnover Alert**: Alerts on products with low stock relative to 30-day sales velocity.
8. **Product Return Rates and Profit Leakage Ranks**: Calculates return rates and category ranks using `DENSE_RANK`.
9. **Rolling Customer Average Spend Trend**: Performs trend analysis using frame-bounded window averages (`ROWS BETWEEN`).
10. **Customer Revenue Pareto Analysis (80/20 Rule)**: Uses running totals (`SUM OVER`) to classify top 80% VIP revenue drivers.
11. **Category Cross-Selling Patterns (Market Basket Analysis)**: Identifies category pairs frequently bought together.
12. **Customer Value Tiering and Spend Percentile Ranking**: Calculates spend percentiles (`PERCENT_RANK`) and groups customer value tiers.
13. **Product Review Ratings and Sales Volume Correlation**: Evaluates average review ratings against purchase counts and revenue totals.
14. **Stock Adjustment Log Auditing and Reorder Alerts**: Audits 90-day restocks, sales, and returns to trigger low stock alerts.
15. **First-Time vs Repeat Customer Monthly Revenue Split**: Compares monthly revenue and percentages from new vs. repeat buyers.
16. **Customer Review Response Speed and Rating Trend**: Finds the average elapsed time between purchases and reviews.
17. **Product Lifecycle Sales Duration and Shelf-Life Velocity**: Measures duration from catalog addition to last sale and daily sales velocity.
18. **Category Monthly Cumulative Sales Progression**: Calculates running revenue aggregates partitioned by product category.
19. **Customer Repeat Purchase Intervals and Loyalty Velocity**: Evaluates order intervals for orders 1-to-2 and 2-to-3.
20. **Product Category Penetration and Customer Cross-Shopping Ratio**: Computes unique category coverage metrics per segment.

## Deployed
Not applicable (Local portfolio development package).

## Architecture Notes
The codebase is designed strictly in accordance with atomic, separation-of-concerns architecture principles:
- **`src/sql_analytics/config/settings.py`**: Manages environment variables and database file path resolution.
- **`src/sql_analytics/models/schema.py`**: Contains SQL DDL statements for database initialization and foreign keys constraints.
- **`src/sql_analytics/utils/data_generator.py`**: Generates high-fidelity mock e-commerce datasets (VIP/Corporate customer discounts, product categories with costs, and inventory logs matching sale/return timelines).
- **`src/sql_analytics/services/db_manager.py`**: Coordinates SQLite connection configuration (enabling foreign key PRAGMAs, registering Python 3.12 compatibility adapters for datetime objects, executing bulk insertions, and rendering pretty-printed query tables using `tabulate`).
- **`src/sql_analytics/queries/__init__.py`**: Houses the registry of our complex analytical SQL queries. Each query is defined with its unique ID, title, descriptive summary, and raw SQL statement.
- **`src/sql_analytics/cli.py`**: Declares subcommands routing via `argparse` and prints out visual statistics.

## Notes
- **Python 3.12+ compatibility**: In Python 3.12, the default datetime adapters and converters for SQLite3 were deprecated. To prevent runtime deprecation warnings, this library explicitly registers ISO-format string adapters and datetime converters on database connection setup.
- **SQLite Database location**: SQLite database files are excluded from Git tracking via `.gitignore` to prevent committing generated local binary databases.
