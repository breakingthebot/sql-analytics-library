# src/sql_analytics/services/db_manager.py
# SQLite Database manager service for the SQL Analytics query library.
# Connects to: config/settings.py, models/schema.py, utils/data_generator.py
# Created: 2026-07-06

import logging
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from tabulate import tabulate

from sql_analytics.config.settings import get_db_path
from sql_analytics.models.schema import (
    ENABLE_FOREIGN_KEYS,
    DROP_TABLES_SQL,
    CREATE_TABLES_SQL
)
from sql_analytics.utils.data_generator import generate_mock_data

# Register SQLite adapters for Python 3.12+ datetime compatibility
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode()))
sqlite3.register_converter("TIMESTAMP", lambda val: datetime.datetime.fromisoformat(val.decode()))

# Set up logger
logger = logging.getLogger("sql_analytics.services.db_manager")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class DBManager:
    """
    Manages SQLite database connections, initialization, populating data, and executing queries.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the DBManager with a specific database path.

        Parameters:
            db_path (Optional[Path]): Path to the SQLite database. If None, resolves from settings.
        """
        self.db_path = db_path or get_db_path()
        logger.debug("DBManager initialized with database path: %s", self.db_path)

    def get_connection(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database with foreign keys enabled.

        Returns:
            sqlite3.Connection: SQLite connection object.
        """
        try:
            # Ensure parent directories exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            # Enable foreign keys
            conn.execute(ENABLE_FOREIGN_KEYS)
            # Return rows as dictionaries for easier analytical access
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error("Failed to connect to SQLite database at %s: %s", self.db_path, e)
            raise

    def initialize_database(self) -> None:
        """
        Drop all existing tables and re-create the schema.
        """
        logger.info("Initializing database schema at %s", self.db_path)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Drop existing tables
                for sql in DROP_TABLES_SQL:
                    cursor.execute(sql)
                logger.debug("Dropped old tables if they existed.")
                
                # Create new tables
                for sql in CREATE_TABLES_SQL:
                    cursor.execute(sql)
                logger.info("Database schema successfully created.")
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to initialize database: %s", e)
                raise

    def populate_mock_data(
        self,
        num_customers: int = 100,
        num_products: int = 30,
        num_orders: int = 300,
        days_back: int = 730,
        seed: int = 42
    ) -> None:
        """
        Generate and insert mock data into the database.

        Parameters:
            num_customers (int): Number of customers.
            num_products (int): Number of products.
            num_orders (int): Number of orders.
            days_back (int): Number of days of historical records.
            seed (int): Random seed for reproducibility.
        """
        logger.info("Generating mock data (customers=%d, products=%d, orders=%d, seed=%d)",
                    num_customers, num_products, num_orders, seed)
        data = generate_mock_data(
            num_customers=num_customers,
            num_products=num_products,
            num_orders=num_orders,
            days_back=days_back,
            seed=seed
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Insert Customers
                cursor.executemany(
                    """
                    INSERT INTO customers (customer_id, first_name, last_name, email, state, country, segment, created_at)
                    VALUES (:customer_id, :first_name, :last_name, :email, :state, :country, :segment, :created_at)
                    """,
                    data["customers"]
                )
                logger.debug("Inserted %d customers.", len(data["customers"]))

                # Insert Products
                cursor.executemany(
                    """
                    INSERT INTO products (product_id, name, sku, category, price, cost, stock_quantity, created_at)
                    VALUES (:product_id, :name, :sku, :category, :price, :cost, :stock_quantity, :created_at)
                    """,
                    data["products"]
                )
                logger.debug("Inserted %d products.", len(data["products"]))

                # Insert Orders
                cursor.executemany(
                    """
                    INSERT INTO orders (order_id, customer_id, order_date, status, shipping_fee)
                    VALUES (:order_id, :customer_id, :order_date, :status, :shipping_fee)
                    """,
                    data["orders"]
                )
                logger.debug("Inserted %d orders.", len(data["orders"]))

                # Insert Order Items
                cursor.executemany(
                    """
                    INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, discount)
                    VALUES (:order_item_id, :order_id, :product_id, :quantity, :unit_price, :discount)
                    """,
                    data["order_items"]
                )
                logger.debug("Inserted %d order items.", len(data["order_items"]))

                # Insert Reviews
                cursor.executemany(
                    """
                    INSERT INTO reviews (review_id, customer_id, product_id, rating, comment, created_at)
                    VALUES (:review_id, :customer_id, :product_id, :rating, :comment, :created_at)
                    """,
                    data["reviews"]
                )
                logger.debug("Inserted %d reviews.", len(data["reviews"]))

                # Insert Inventory Logs
                cursor.executemany(
                    """
                    INSERT INTO inventory_logs (product_id, change_quantity, reason, logged_at)
                    VALUES (:product_id, :change_quantity, :reason, :logged_at)
                    """,
                    data["inventory_logs"]
                )
                logger.debug("Inserted %d inventory logs.", len(data["inventory_logs"]))

                conn.commit()
                logger.info("Successfully populated database with e-commerce dataset.")
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to populate mock data: %s", e)
                raise

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """
        Execute an analytical SQL query and return rows as dictionaries.

        Parameters:
            query (str): The raw SQL query to run.
            params (Tuple[Any, ...]): Any parameters to bind to the query.

        Returns:
            List[Dict[str, Any]]: List of dictionary representations of the row results.
        """
        logger.debug("Executing query: %s with params: %s", query.strip()[:60] + "...", params)
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except sqlite3.Error as e:
                logger.error("Query execution failed: %s\nQuery: %s", e, query)
                raise

def format_results_list(results: List[Dict[str, Any]], fmt: str = "table") -> str:
    """
    Format a list of dictionaries into a table, csv, json, or markdown string.

    Parameters:
        results (List[Dict[str, Any]]): List of row dictionaries.
        fmt (str): The format type ('table', 'csv', 'json', 'markdown').

    Returns:
        str: The formatted string content.
    """
    import csv
    import json
    import io

    if not results:
        return "No results returned."

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        return output.getvalue()

    elif fmt == "json":
        return json.dumps(results, indent=2, default=str)

    elif fmt == "markdown":
        headers = list(results[0].keys())
        rows = [list(r.values()) for r in results]
        return tabulate(rows, headers=headers, tablefmt="github")

    else:  # default 'table' or 'grid'
        headers = list(results[0].keys())
        rows = [list(r.values()) for r in results]
        return tabulate(rows, headers=headers, tablefmt="grid")


class DBManager:
    """
    Manages SQLite database connections, initialization, populating data, and executing queries.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the DBManager with a specific database path.

        Parameters:
            db_path (Optional[Path]): Path to the SQLite database. If None, resolves from settings.
        """
        self.db_path = db_path or get_db_path()
        logger.debug("DBManager initialized with database path: %s", self.db_path)

    def get_connection(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database with foreign keys enabled.

        Returns:
            sqlite3.Connection: SQLite connection object.
        """
        try:
            # Ensure parent directories exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            # Enable foreign keys
            conn.execute(ENABLE_FOREIGN_KEYS)
            # Return rows as dictionaries for easier analytical access
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error("Failed to connect to SQLite database at %s: %s", self.db_path, e)
            raise

    def initialize_database(self) -> None:
        """
        Drop all existing tables and re-create the schema.
        """
        logger.info("Initializing database schema at %s", self.db_path)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Drop existing tables
                for sql in DROP_TABLES_SQL:
                    cursor.execute(sql)
                logger.debug("Dropped old tables if they existed.")
                
                # Create new tables
                for sql in CREATE_TABLES_SQL:
                    cursor.execute(sql)
                logger.info("Database schema successfully created.")
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to initialize database: %s", e)
                raise

    def populate_mock_data(
        self,
        num_customers: int = 100,
        num_products: int = 30,
        num_orders: int = 300,
        days_back: int = 730,
        seed: int = 42
    ) -> None:
        """
        Generate and insert mock data into the database.

        Parameters:
            num_customers (int): Number of customers.
            num_products (int): Number of products.
            num_orders (int): Number of orders.
            days_back (int): Number of days of historical records.
            seed (int): Random seed for reproducibility.
        """
        logger.info("Generating mock data (customers=%d, products=%d, orders=%d, seed=%d)",
                    num_customers, num_products, num_orders, seed)
        data = generate_mock_data(
            num_customers=num_customers,
            num_products=num_products,
            num_orders=num_orders,
            days_back=days_back,
            seed=seed
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Insert Customers
                cursor.executemany(
                    """
                    INSERT INTO customers (customer_id, first_name, last_name, email, state, country, segment, created_at)
                    VALUES (:customer_id, :first_name, :last_name, :email, :state, :country, :segment, :created_at)
                    """,
                    data["customers"]
                )
                logger.debug("Inserted %d customers.", len(data["customers"]))

                # Insert Products
                cursor.executemany(
                    """
                    INSERT INTO products (product_id, name, sku, category, price, cost, stock_quantity, created_at)
                    VALUES (:product_id, :name, :sku, :category, :price, :cost, :stock_quantity, :created_at)
                    """,
                    data["products"]
                )
                logger.debug("Inserted %d products.", len(data["products"]))

                # Insert Orders
                cursor.executemany(
                    """
                    INSERT INTO orders (order_id, customer_id, order_date, status, shipping_fee)
                    VALUES (:order_id, :customer_id, :order_date, :status, :shipping_fee)
                    """,
                    data["orders"]
                )
                logger.debug("Inserted %d orders.", len(data["orders"]))

                # Insert Order Items
                cursor.executemany(
                    """
                    INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, discount)
                    VALUES (:order_item_id, :order_id, :product_id, :quantity, :unit_price, :discount)
                    """,
                    data["order_items"]
                )
                logger.debug("Inserted %d order items.", len(data["order_items"]))

                # Insert Reviews
                cursor.executemany(
                    """
                    INSERT INTO reviews (review_id, customer_id, product_id, rating, comment, created_at)
                    VALUES (:review_id, :customer_id, :product_id, :rating, :comment, :created_at)
                    """,
                    data["reviews"]
                )
                logger.debug("Inserted %d reviews.", len(data["reviews"]))

                # Insert Inventory Logs
                cursor.executemany(
                    """
                    INSERT INTO inventory_logs (product_id, change_quantity, reason, logged_at)
                    VALUES (:product_id, :change_quantity, :reason, :logged_at)
                    """,
                    data["inventory_logs"]
                )
                logger.debug("Inserted %d inventory logs.", len(data["inventory_logs"]))

                conn.commit()
                logger.info("Successfully populated database with e-commerce dataset.")
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to populate mock data: %s", e)
                raise

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """
        Execute an analytical SQL query and return rows as dictionaries.

        Parameters:
            query (str): The raw SQL query to run.
            params (Tuple[Any, ...]): Any parameters to bind to the query.

        Returns:
            List[Dict[str, Any]]: List of dictionary representations of the row results.
        """
        logger.debug("Executing query: %s with params: %s", query.strip()[:60] + "...", params)
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except sqlite3.Error as e:
                logger.error("Query execution failed: %s\nQuery: %s", e, query)
                raise

    def execute_query_formatted(self, query: str, params: Tuple[Any, ...] = (), fmt: str = "table") -> str:
        """
        Execute an analytical SQL query and format the result based on format type.

        Parameters:
            query (str): The raw SQL query to run.
            params (Tuple[Any, ...]): Parameters to bind to the query.
            fmt (str): The format type ('table', 'csv', 'json', 'markdown').

        Returns:
            str: The formatted query results.
        """
        results = self.execute_query(query, params)
        return format_results_list(results, fmt=fmt)

    def benchmark_queries(self, iterations: int = 5) -> List[Dict[str, Any]]:
        """
        Benchmark all registered queries, running each multiple times to measure latency.

        Parameters:
            iterations (int): The number of times to run each query.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing benchmark statistics.
        """
        import time
        from sql_analytics.queries import QUERIES

        logger.info("Starting performance benchmark (iterations=%d for each of %d queries)",
                    iterations, len(QUERIES))
        
        benchmark_results = []
        for query_def in QUERIES:
            query_id = query_def["id"]
            title = query_def["title"]
            sql = query_def["sql"]

            latencies_ms = []
            for _ in range(iterations):
                start = time.perf_counter()
                try:
                    self.execute_query(sql)
                    end = time.perf_counter()
                    latencies_ms.append((end - start) * 1000.0)
                except sqlite3.Error as e:
                    logger.error("Query %d failed during benchmark: %s", query_id, e)
                    latencies_ms = [0.0]
                    break

            if latencies_ms:
                min_ms = min(latencies_ms)
                max_ms = max(latencies_ms)
                avg_ms = sum(latencies_ms) / len(latencies_ms)
            else:
                min_ms = max_ms = avg_ms = 0.0

            benchmark_results.append({
                "query_id": query_id,
                "title": title,
                "runs": iterations if latencies_ms != [0.0] else 0,
                "min_ms": round(min_ms, 3),
                "max_ms": round(max_ms, 3),
                "avg_ms": round(avg_ms, 3)
            })
            logger.debug("Query %d benchmarked: min=%.3fms, max=%.3fms, avg=%.3fms",
                         query_id, min_ms, max_ms, avg_ms)

        logger.info("Performance benchmark completed successfully.")
        return benchmark_results
