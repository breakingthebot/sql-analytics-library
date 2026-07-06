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
   sql-analytics db-init
   ```
   *Options*: Customize dataset size using `--customers <count>`, `--products <count>`, `--orders <count>`.

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
   *Options*: Add `--verbose` to view the raw SQL statement before running.

5. **Run Automated Tests**:
   ```bash
   pytest --basetemp=tests/tmp
   ```

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
