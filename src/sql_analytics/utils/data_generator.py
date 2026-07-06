# src/sql_analytics/utils/data_generator.py
# Generates realistic mock e-commerce data with high integrity.
# Connects to: None
# Created: 2026-07-06

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

# Predefined datasets for realistic e-commerce simulation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young"
]

STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI", "WA", "AZ", "CO", "MA", "VA", "OR"]

CATEGORIES = {
    "Electronics": [
        ("Wireless Headphones", 99.99, 45.00),
        ("Smart Watch", 199.99, 90.00),
        ("Bluetooth Speaker", 49.99, 22.00),
        ("Noise Cancelling Earbuds", 149.99, 65.00),
        ("Mechanical Keyboard", 119.99, 50.00),
        ("Ergonomic Mouse", 59.99, 25.00),
        ("4K Monitor", 349.99, 180.00)
    ],
    "Apparel": [
        ("Classic Denim Jacket", 79.99, 30.00),
        ("Running Shoes", 120.00, 55.00),
        ("Cotton T-Shirt", 19.99, 6.00),
        ("Athletic Shorts", 29.99, 10.00),
        ("Wool Sweater", 89.99, 35.00),
        ("Leather Belt", 39.99, 15.00),
        ("Polarized Sunglasses", 150.00, 60.00)
    ],
    "Home & Kitchen": [
        ("Drip Coffee Maker", 49.99, 20.00),
        ("Stainless Steel Kettle", 34.99, 14.00),
        ("Chef's Knife", 69.99, 25.00),
        ("Non-Stick Frying Pan", 39.99, 16.00),
        ("Memory Foam Pillow", 45.00, 18.00),
        ("Air Purifier", 129.99, 60.00),
        ("Robot Vacuum", 249.99, 110.00)
    ],
    "Beauty": [
        ("Moisturizing Cream", 24.99, 8.00),
        ("Hydrating Serum", 32.00, 11.00),
        ("Face Wash", 15.99, 5.00),
        ("Sunscreen SPF 50", 18.99, 6.50),
        ("Matte Lipstick", 22.00, 7.00),
        ("Clay Mask", 19.99, 6.00)
    ],
    "Sports & Outdoors": [
        ("Yoga Mat", 25.00, 9.00),
        ("Stainless Water Bottle", 19.99, 7.00),
        ("Camping Tent", 149.99, 65.00),
        ("Sleeping Bag", 79.99, 32.00),
        ("Dumbbell Set", 59.99, 25.00),
        ("Resistance Bands", 14.99, 5.00),
        ("Hiking Backpack", 99.99, 42.00)
    ]
}

REVIEW_COMMENTS = {
    5: ["Absolutely love it!", "Exceeded my expectations.", "High quality, worth every penny.", "Excellent product.", "Highly recommend!"],
    4: ["Good quality, works well.", "Satisfied with this purchase.", "Very good, minor complaints.", "As described, fast shipping.", "Solid product."],
    3: ["Decent, but could be better.", "Average product.", "Okay for the price.", "Took a bit long to ship, product is fine.", "It works, but feels cheap."],
    2: ["Disappointed.", "Did not meet expectations.", "Quality is lacking.", "Underperforming product.", "Wouldn't buy again."],
    1: ["Terrible quality.", "Broke on first use.", "Complete waste of money.", "Do not buy!", "Horrible experience."]
}

def generate_mock_data(
    num_customers: int = 100,
    num_products: int = 30,
    num_orders: int = 300,
    days_back: int = 730,
    seed: int = 42
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generates structured mock data for customers, products, orders, items, reviews, and logs.

    Parameters:
        num_customers (int): The number of customers to generate.
        num_products (int): The number of products to generate (clamped to max available).
        num_orders (int): The number of orders to generate.
        days_back (int): The number of days back to generate history for.
        seed (int): Random seed for reproducibility.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Lists of dictionaries representing rows for each table.
    """
    # Set seed for reproducibility
    random.seed(seed)

    start_date = datetime.now() - timedelta(days=days_back)
    
    # 1. Generate Products
    products = []
    prod_pool = []
    for cat, items in CATEGORIES.items():
        for name, price, cost in items:
            prod_pool.append((name, cat, price, cost))
            
    # Clamp to max pool size if exceeded
    num_products = min(num_products, len(prod_pool))
    selected_prods = random.sample(prod_pool, num_products)
    
    for i, (name, cat, price, cost) in enumerate(selected_prods, start=1):
        sku = f"{cat[:3].upper()}-{i:04d}-{random.randint(100, 999)}"
        created_days_back = random.randint(int(days_back * 0.8), days_back)
        prod_created = start_date + timedelta(days=days_back - created_days_back)
        initial_stock = random.randint(50, 200)
        
        products.append({
            "product_id": i,
            "name": name,
            "sku": sku,
            "category": cat,
            "price": price,
            "cost": cost,
            "stock_quantity": initial_stock,
            "created_at": prod_created
        })

    # 2. Generate Customers
    customers = []
    used_emails = set()
    for i in range(1, num_customers + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@example.com"
        while email in used_emails:
            email = f"{first.lower()}.{last.lower()}{random.randint(100, 999)}@example.com"
        used_emails.add(email)
        
        segment = random.choices(["Retail", "VIP", "Corporate"], weights=[0.80, 0.15, 0.05], k=1)[0]
        created_days_back = random.randint(0, days_back)
        cust_created = start_date + timedelta(days=created_days_back)
        
        customers.append({
            "customer_id": i,
            "first_name": first,
            "last_name": last,
            "email": email,
            "state": random.choice(STATES),
            "country": "USA",
            "segment": segment,
            "created_at": cust_created
        })

    # 3. Generate Orders, Order Items, Reviews, and Inventory Logs
    orders = []
    order_items = []
    reviews = []
    inventory_logs = []
    
    # Track inventory state per product to create realistic logs
    current_inventory = {p["product_id"]: p["stock_quantity"] for p in products}
    
    # Initialize inventory logs with initial restocks
    for p in products:
        inventory_logs.append({
            "product_id": p["product_id"],
            "change_quantity": p["stock_quantity"],
            "reason": "Restock",
            "logged_at": p["created_at"]
        })
        
    order_item_id_counter = 1
    review_id_counter = 1
    log_id_counter = len(products) + 1
    
    # Generate orders over the time range
    # Sort customers by their creation date so we can assign order dates correctly
    for order_id in range(1, num_orders + 1):
        # Choose a random customer
        customer = random.choice(customers)
        cust_created = customer["created_at"]
        
        # Order date must be after customer creation date
        days_remaining = (datetime.now() - cust_created).days
        if days_remaining <= 0:
            order_date = cust_created
        else:
            order_date = cust_created + timedelta(days=random.randint(0, days_remaining),
                                                  hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59))
            
        # Ensure order date is not in the future relative to now
        if order_date > datetime.now():
            order_date = datetime.now()

        # Check which products existed before or at order date
        available_products = [p for p in products if p["created_at"] <= order_date]
        if not available_products:
            available_products = products  # fallback
            
        # Determine order status
        # Completed (80%), Returned (7%), Cancelled (8%), Pending (5%)
        status = random.choices(["Completed", "Returned", "Cancelled", "Pending"],
                                weights=[0.80, 0.07, 0.08, 0.05], k=1)[0]
        
        # Calculate shipping fee: VIP gets free shipping, orders > $100 get free shipping, otherwise $5.99-$12.99
        shipping_fee = 0.0
        
        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date,
            "status": status,
            "shipping_fee": shipping_fee  # Will calculate and update after items are selected
        })
        
        # Generate 1 to 4 items for this order
        num_items = random.randint(1, 4)
        order_products = random.sample(available_products, min(num_items, len(available_products)))
        
        total_order_value = 0.0
        
        for p in order_products:
            qty = random.choices([1, 2, 3, 4], weights=[0.7, 0.2, 0.07, 0.03], k=1)[0]
            unit_price = p["price"]
            
            # Segment-based discounts
            discount = 0.0
            if customer["segment"] == "VIP":
                discount = random.choice([0.0, 0.10, 0.15])
            elif customer["segment"] == "Corporate":
                discount = random.choice([0.0, 0.05, 0.10, 0.15, 0.20])
            else:
                # Retail might get occasional promo discount
                discount = random.choices([0.0, 0.05], weights=[0.9, 0.1], k=1)[0]
                
            total_order_value += (unit_price * qty) * (1 - discount)
            
            order_items.append({
                "order_item_id": order_item_id_counter,
                "order_id": order_id,
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_price": unit_price,
                "discount": discount
            })
            order_item_id_counter += 1
            
            # Inventory updates (logs and current stocks)
            # Cancelled orders do not affect inventory, Pending/Completed/Returned do.
            if status in ["Completed", "Returned", "Pending"]:
                current_inventory[p["product_id"]] -= qty
                inventory_logs.append({
                    "log_id": log_id_counter,
                    "product_id": p["product_id"],
                    "change_quantity": -qty,
                    "reason": "Sale",
                    "logged_at": order_date
                })
                log_id_counter += 1
                
                # If returned, product goes back to inventory shortly after
                if status == "Returned":
                    return_date = order_date + timedelta(days=random.randint(1, 10))
                    if return_date > datetime.now():
                        return_date = datetime.now()
                    current_inventory[p["product_id"]] += qty
                    inventory_logs.append({
                        "log_id": log_id_counter,
                        "product_id": p["product_id"],
                        "change_quantity": qty,
                        "reason": "Return",
                        "logged_at": return_date
                    })
                    log_id_counter += 1

            # Generate reviews for some completed/returned items
            if status in ["Completed", "Returned"] and random.random() < 0.25:
                # Review date is 1-14 days after order date
                review_date = order_date + timedelta(days=random.randint(1, 14))
                if review_date > datetime.now():
                    review_date = datetime.now()
                
                # Returned orders skew lower in rating
                if status == "Returned":
                    rating = random.choices([1, 2, 3, 4], weights=[0.4, 0.3, 0.2, 0.1], k=1)[0]
                else:
                    rating = random.choices([5, 4, 3, 2, 1], weights=[0.5, 0.3, 0.1, 0.07, 0.03], k=1)[0]
                    
                comment = random.choice(REVIEW_COMMENTS[rating])
                
                reviews.append({
                    "review_id": review_id_counter,
                    "customer_id": customer["customer_id"],
                    "product_id": p["product_id"],
                    "rating": rating,
                    "comment": comment,
                    "created_at": review_date
                })
                review_id_counter += 1

        # Complete shipping fee calculation
        if customer["segment"] == "VIP" or total_order_value >= 100.0:
            orders[-1]["shipping_fee"] = 0.0
        else:
            orders[-1]["shipping_fee"] = round(random.uniform(5.99, 12.99), 2)
            
    # Periodically restock inventory if it falls below 20
    # Process inventory restocks based on logs timeline
    for pid, inv in current_inventory.items():
        if inv < 20:
            restock_amt = random.randint(50, 100)
            products[pid - 1]["stock_quantity"] = inv + restock_amt
            inventory_logs.append({
                "log_id": log_id_counter,
                "product_id": pid,
                "change_quantity": restock_amt,
                "reason": "Restock",
                "logged_at": datetime.now() - timedelta(hours=random.randint(1, 12))
            })
            log_id_counter += 1
        else:
            products[pid - 1]["stock_quantity"] = inv

    # Set generated data
    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "reviews": reviews,
        "inventory_logs": inventory_logs
    }
