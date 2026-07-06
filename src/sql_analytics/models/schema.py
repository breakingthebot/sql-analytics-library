# src/sql_analytics/models/schema.py
# SQL Schema definitions for the e-commerce analytics database.
# Connects to: None
# Created: 2026-07-06

# SQL to enable foreign keys in SQLite
ENABLE_FOREIGN_KEYS = "PRAGMA foreign_keys = ON;"

# SQL queries to drop all tables in reverse dependency order
DROP_TABLES_SQL = [
    "DROP TABLE IF EXISTS inventory_logs;",
    "DROP TABLE IF EXISTS reviews;",
    "DROP TABLE IF EXISTS order_items;",
    "DROP TABLE IF EXISTS orders;",
    "DROP TABLE IF EXISTS products;",
    "DROP TABLE IF EXISTS customers;"
]

# SQL queries to create tables with appropriate datatypes and foreign keys
CREATE_TABLES_SQL = [
    """
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        state TEXT NOT NULL,
        country TEXT NOT NULL,
        segment TEXT NOT NULL CHECK(segment IN ('Retail', 'VIP', 'Corporate')),
        created_at TIMESTAMP NOT NULL
    );
    """,
    """
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        cost REAL NOT NULL CHECK(cost >= 0),
        stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
        created_at TIMESTAMP NOT NULL
    );
    """,
    """
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TIMESTAMP NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Completed', 'Pending', 'Cancelled', 'Returned')),
        shipping_fee REAL NOT NULL DEFAULT 0.0 CHECK(shipping_fee >= 0),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        unit_price REAL NOT NULL CHECK(unit_price >= 0),
        discount REAL NOT NULL DEFAULT 0.0 CHECK(discount >= 0.0 AND discount <= 1.0),
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        comment TEXT,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE inventory_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        change_quantity INTEGER NOT NULL,
        reason TEXT NOT NULL CHECK(reason IN ('Sale', 'Restock', 'Return', 'Adjustment')),
        logged_at TIMESTAMP NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
    );
    """
]
