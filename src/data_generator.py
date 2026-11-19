"""
Synthetic E-Commerce Data Generator.
Produces realistic, relational, reproducible datasets for customers, products,
orders, order items, payments, and events with authentic seasonality, category price
distributions, customer behavior patterns, and strict schema adherence.
"""

from datetime import datetime, timedelta
import logging
from pathlib import Path
import random
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import (
    CUSTOMER_SEGMENTS,
    DATA_RAW_DIR,
    HOURLY_WEIGHTS,
    MONTHLY_SEASONALITY_WEIGHTS,
    NUM_CUSTOMERS,
    NUM_EVENTS,
    NUM_ORDERS,
    NUM_PRODUCTS,
    ORDER_STATUSES,
    PAYMENT_METHODS,
    PRODUCT_CATEGORIES,
    RANDOM_SEED,
    US_LOCATIONS
)
from src.logger import get_logger

logger = get_logger("EcommercePlatform.DataGenerator", "data_generation.log")


class EcommerceDataGenerator:
    """
    Orchestrates the generation of realistic e-commerce synthetic data with referential
    integrity, seasonal patterns, and business rule enforcement.
    """

    MALE_FIRST_NAMES: List[str] = [
        "James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph",
        "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
        "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
        "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob",
        "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
        "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Frank", "Patrick"
    ]

    FEMALE_FIRST_NAMES: List[str] = [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica",
        "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Betty", "Sandra", "Ashley",
        "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa", "Deborah",
        "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen", "Amy", "Angela",
        "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen", "Samantha",
        "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Maria", "Heather"
    ]

    LAST_NAMES: List[str] = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
        "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey"
    ]

    EMAIL_DOMAINS: List[str] = [
        "gmail.com", "yahoo.com", "outlook.com", "icloud.com", "proton.me", "fastmail.com"
    ]

    PRODUCT_ADJECTIVES: List[str] = [
        "Pro", "Ultra", "Essential", "Premium", "Classic", "Eco-Friendly",
        "Ergonomic", "Smart", "Compact", "Advanced", "Elite", "Signature"
    ]

    def __init__(self, seed: int = RANDOM_SEED) -> None:
        """Initializes generator with a fixed random seed."""
        self.seed = seed
        self._set_seed(seed)
        logger.info(f"Initialized EcommerceDataGenerator with seed={seed}")

    def _set_seed(self, seed: int) -> None:
        """Sets internal random seeds across Python random and NumPy."""
        random.seed(seed)
        np.random.seed(seed)

    # -------------------------------------------------------------------------
    # 1. Customers Generator
    # -------------------------------------------------------------------------
    def generate_customers(self, n: int = NUM_CUSTOMERS) -> pd.DataFrame:
        """
        Generates realistic customer profiles matching schema:
        customer_id, first_name, last_name, email, gender, age, city, state, signup_date, customer_segment
        """
        logger.info(f"Generating {n:,} customer records...")
        customers = []

        # Registration window: 2024-01-01 to 2024-12-31 (guarantees signup_date < order_date)
        signup_start = datetime(2024, 1, 1, 0, 0, 0)
        segment_names, segment_weights = zip(*CUSTOMER_SEGMENTS)

        for i in range(1, n + 1):
            customer_id = f"CUST-{i:06d}"

            # Gender selection
            gender_roll = random.random()
            if gender_roll < 0.49:
                gender = "M"
                first_name = random.choice(self.MALE_FIRST_NAMES)
            elif gender_roll < 0.98:
                gender = "F"
                first_name = random.choice(self.FEMALE_FIRST_NAMES)
            else:
                gender = "Other"
                first_name = random.choice(self.MALE_FIRST_NAMES + self.FEMALE_FIRST_NAMES)

            last_name = random.choice(self.LAST_NAMES)
            email_domain = random.choice(self.EMAIL_DOMAINS)
            email = f"{first_name.lower()}.{last_name.lower()}{i % 999}@{email_domain}"

            # Realistic age distribution (18-72, centered in late 20s - 40s)
            age = int(np.clip(np.random.normal(36, 12), 18, 72))

            loc = random.choice(US_LOCATIONS)
            segment = np.random.choice(segment_names, p=segment_weights)

            signup_offset = timedelta(
                days=random.randint(0, 364),
                seconds=random.randint(0, 86399)
            )
            signup_date = (signup_start + signup_offset).strftime("%Y-%m-%d %H:%M:%S")

            customers.append({
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "gender": gender,
                "age": age,
                "city": loc["city"],
                "state": loc["state"],
                "signup_date": signup_date,
                "customer_segment": segment
            })

        df = pd.DataFrame(customers)
        logger.info(f"Generated {len(df):,} customer records successfully.")
        return df

    # -------------------------------------------------------------------------
    # 2. Products Generator
    # -------------------------------------------------------------------------
    def generate_products(self, n: int = NUM_PRODUCTS) -> pd.DataFrame:
        """
        Generates realistic product catalog matching schema:
        product_id, product_name, category, subcategory, price, cost, stock_quantity, product_rating
        """
        logger.info(f"Generating {n:,} product records...")
        products = []
        categories = list(PRODUCT_CATEGORIES.keys())

        for i in range(1, n + 1):
            product_id = f"PROD-{i:06d}"
            category = random.choice(categories)
            cat_meta = PRODUCT_CATEGORIES[category]

            subcategory = random.choice(cat_meta["subcategories"])
            adj = random.choice(self.PRODUCT_ADJECTIVES)
            product_name = f"{adj} {subcategory.rstrip('s')} {i % 100 + 1}"

            min_p, max_p = cat_meta["price_range"]
            raw_price = np.random.uniform(min_p, max_p)
            price = round(raw_price - (raw_price % 1) + 0.99, 2)
            if price < min_p:
                price = round(min_p, 2)

            min_c, max_c = cat_meta["cost_ratio_range"]
            cost = round(price * random.uniform(min_c, max_c), 2)
            stock_quantity = random.randint(20, 1000)

            # Rating distribution: average 4.2 with std 0.5, clamped [3.0, 5.0]
            product_rating = round(float(np.clip(np.random.normal(4.2, 0.45), 3.0, 5.0)), 1)

            products.append({
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "subcategory": subcategory,
                "price": price,
                "cost": cost,
                "stock_quantity": stock_quantity,
                "product_rating": product_rating
            })

        df = pd.DataFrame(products)
        logger.info(f"Generated {len(df):,} product records successfully.")
        return df

    # -------------------------------------------------------------------------
    # 3. Orders and Order Items Generator
    # -------------------------------------------------------------------------
    def generate_orders_and_items(
        self,
        customers_df: pd.DataFrame,
        products_df: pd.DataFrame,
        n_orders: int = NUM_ORDERS
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generates orders and order line items with seasonal patterns and mathematical consistency.
        Orders schema:
            order_id, customer_id, order_date, order_status, shipping_city, shipping_state,
            payment_method, total_amount
        Order items schema:
            order_item_id, order_id, product_id, quantity, unit_price, discount, subtotal
        """
        logger.info(f"Generating {n_orders:,} orders and line items...")

        customer_ids = customers_df["customer_id"].values
        customer_lookup = customers_df.set_index("customer_id").to_dict("index")
        product_records = products_df[["product_id", "price"]].to_dict("records")
        num_products = len(product_records)

        months = list(range(1, 13))
        month_weights = [MONTHLY_SEASONALITY_WEIGHTS[m] for m in months]
        month_probs = np.array(month_weights) / sum(month_weights)

        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }

        status_names, status_weights = zip(*ORDER_STATUSES)
        method_names, method_weights = zip(*PAYMENT_METHODS)
        hourly_probs = np.array(HOURLY_WEIGHTS) / sum(HOURLY_WEIGHTS)

        orders = []
        order_items = []
        item_counter = 1

        for ord_idx in range(1, n_orders + 1):
            order_id = f"ORD-{ord_idx:07d}"
            customer_id = np.random.choice(customer_ids)
            customer = customer_lookup[customer_id]

            # Seasonal date generation
            chosen_month = int(np.random.choice(months, p=month_probs))
            chosen_day = random.randint(1, days_in_month[chosen_month])
            chosen_hour = int(np.random.choice(range(24), p=hourly_probs))
            chosen_min = random.randint(0, 59)
            chosen_sec = random.randint(0, 59)

            order_dt = datetime(2025, chosen_month, chosen_day, chosen_hour, chosen_min, chosen_sec)
            order_date_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")

            order_status = np.random.choice(status_names, p=status_weights)
            payment_method = np.random.choice(method_names, p=method_weights)

            # Line items per order: 1 (35%), 2 (35%), 3 (18%), 4 (8%), 5 (4%)
            # Guarantees >2.1 average items per order, exceeding 22,000+ total line items
            num_items = int(np.random.choice([1, 2, 3, 4, 5], p=[0.35, 0.35, 0.18, 0.08, 0.04]))
            chosen_prod_indices = np.random.choice(num_products, size=num_items, replace=False)

            order_total = 0.0
            for prod_idx in chosen_prod_indices:
                prod = product_records[prod_idx]
                qty = int(np.random.choice([1, 2, 3, 4], p=[0.75, 0.18, 0.05, 0.02]))
                unit_price = float(prod["price"])
                raw_item_total = qty * unit_price

                # 25% chance of item promotional discount (5% to 20% off)
                if random.random() < 0.25:
                    discount = round(raw_item_total * random.choice([0.05, 0.10, 0.15, 0.20]), 2)
                else:
                    discount = 0.00

                subtotal = round(raw_item_total - discount, 2)
                order_total += subtotal

                order_items.append({
                    "order_item_id": f"ITEM-{item_counter:08d}",
                    "order_id": order_id,
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "discount": discount,
                    "subtotal": subtotal
                })
                item_counter += 1

            order_total = round(order_total, 2)

            orders.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "order_date": order_date_str,
                "order_status": order_status,
                "shipping_city": customer["city"],
                "shipping_state": customer["state"],
                "payment_method": payment_method,
                "total_amount": order_total
            })

        orders_df = pd.DataFrame(orders)
        order_items_df = pd.DataFrame(order_items)

        logger.info(f"Generated {len(orders_df):,} orders and {len(order_items_df):,} order items.")
        return orders_df, order_items_df

    # -------------------------------------------------------------------------
    # 4. Payments Generator
    # -------------------------------------------------------------------------
    def generate_payments(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates payment records matching schema:
        payment_id, order_id, payment_method, payment_status, payment_amount, payment_date
        """
        logger.info(f"Generating payments for {len(orders_df):,} orders...")
        payments = []
        payment_counter = 1

        for _, order in orders_df.iterrows():
            payment_id = f"PAY-{payment_counter:07d}"
            order_id = order["order_id"]
            order_status = order["order_status"]
            payment_method = order["payment_method"]
            payment_amount = order["total_amount"]
            order_dt = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")

            # Payment timestamp is within 5 - 120 seconds of order
            pay_dt = order_dt + timedelta(seconds=random.randint(5, 120))
            payment_date_str = pay_dt.strftime("%Y-%m-%d %H:%M:%S")

            # Status correlation
            if order_status in ["completed", "shipped"]:
                payment_status = "successful"
            elif order_status == "processing":
                payment_status = "successful" if random.random() < 0.90 else "pending"
            elif order_status == "cancelled":
                payment_status = "refunded" if random.random() < 0.75 else "failed"
            elif order_status == "returned":
                payment_status = "refunded"
            else:
                payment_status = "successful"

            payments.append({
                "payment_id": payment_id,
                "order_id": order_id,
                "payment_method": payment_method,
                "payment_status": payment_status,
                "payment_amount": payment_amount,
                "payment_date": payment_date_str
            })
            payment_counter += 1

        payments_df = pd.DataFrame(payments)
        logger.info(f"Generated {len(payments_df):,} payment transactions.")
        return payments_df

    # -------------------------------------------------------------------------
    # 5. Events Generator
    # -------------------------------------------------------------------------
    def generate_events(
        self,
        customers_df: pd.DataFrame,
        products_df: pd.DataFrame,
        orders_df: pd.DataFrame,
        n_events: int = NUM_EVENTS
    ) -> pd.DataFrame:
        """
        Generates clickstream events matching schema:
        event_id, customer_id, product_id, event_type, event_timestamp, session_id
        Event types: product_view, add_to_cart, checkout, purchase, product_search
        """
        logger.info(f"Generating ~{n_events:,} customer activity events...")

        customer_ids = customers_df["customer_id"].values
        product_ids = products_df["product_id"].values

        events = []
        event_counter = 1

        # Funnel A: Converted purchase sessions aligned with orders
        sample_orders = orders_df.sample(frac=0.75, random_state=self.seed)
        for _, order in sample_orders.iterrows():
            cust_id = order["customer_id"]
            prod_id = np.random.choice(product_ids)
            order_dt = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
            session_id = f"SESS-{random.randint(1000000, 9999999)}"

            # 1. product_search
            t1 = order_dt - timedelta(minutes=random.randint(12, 25))
            events.append({
                "event_id": f"EVT-{event_counter:08d}",
                "customer_id": cust_id,
                "product_id": None,
                "event_type": "product_search",
                "event_timestamp": t1.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id
            })
            event_counter += 1

            # 2. product_view
            t2 = t1 + timedelta(minutes=random.randint(2, 5))
            events.append({
                "event_id": f"EVT-{event_counter:08d}",
                "customer_id": cust_id,
                "product_id": prod_id,
                "event_type": "product_view",
                "event_timestamp": t2.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id
            })
            event_counter += 1

            # 3. add_to_cart
            t3 = t2 + timedelta(minutes=random.randint(1, 4))
            events.append({
                "event_id": f"EVT-{event_counter:08d}",
                "customer_id": cust_id,
                "product_id": prod_id,
                "event_type": "add_to_cart",
                "event_timestamp": t3.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id
            })
            event_counter += 1

            # 4. checkout
            t4 = t3 + timedelta(minutes=random.randint(1, 3))
            events.append({
                "event_id": f"EVT-{event_counter:08d}",
                "customer_id": cust_id,
                "product_id": prod_id,
                "event_type": "checkout",
                "event_timestamp": t4.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id
            })
            event_counter += 1

            # 5. purchase (aligned with order date)
            events.append({
                "event_id": f"EVT-{event_counter:08d}",
                "customer_id": cust_id,
                "product_id": prod_id,
                "event_type": "purchase",
                "event_timestamp": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id
            })
            event_counter += 1

        # Funnel B: Exploratory & Abandoned sessions
        remaining = max(1000, n_events - len(events))
        logger.info(f"Generating {remaining:,} exploratory/abandoned sessions...")

        sim_start = datetime(2025, 1, 1, 0, 0, 0)
        sim_duration = 365 * 86400

        browse_event_types = ["product_search", "product_view", "add_to_cart", "checkout"]
        browse_weights = [0.40, 0.40, 0.15, 0.05]

        for _ in range(remaining):
            cust_id = np.random.choice(customer_ids) if random.random() < 0.80 else None
            ev_type = np.random.choice(browse_event_types, p=browse_weights)
            prod_id = np.random.choice(product_ids) if ev_type != "product_search" else None
            session_id = f"SESS-{random.randint(1000000, 9999999)}"

            random_sec = random.randint(0, sim_duration - 1)
            ev_dt = (sim_start + timedelta(seconds=random_sec)).strftime("%Y-%m-%d %H:%M:%S")

            events.append({
                "event_id": f"EVT-{event_counter:08d}",
                "customer_id": cust_id,
                "product_id": prod_id,
                "event_type": ev_type,
                "event_timestamp": ev_dt,
                "session_id": session_id
            })
            event_counter += 1

        events_df = pd.DataFrame(events)
        events_df.sort_values(by="event_timestamp", inplace=True)
        events_df.reset_index(drop=True, inplace=True)
        logger.info(f"Generated {len(events_df):,} events successfully.")
        return events_df

    # -------------------------------------------------------------------------
    # 6. Pipeline Orchestration & CSV Export
    # -------------------------------------------------------------------------
    def generate_all(
        self,
        num_customers: int = NUM_CUSTOMERS,
        num_products: int = NUM_PRODUCTS,
        num_orders: int = NUM_ORDERS,
        num_events: int = NUM_EVENTS
    ) -> Dict[str, pd.DataFrame]:
        """Runs the entire generation pipeline and returns a dictionary of DataFrames."""
        logger.info("=== Commencing Complete Dataset Generation Pipeline ===")
        customers_df = self.generate_customers(n=num_customers)
        products_df = self.generate_products(n=num_products)
        orders_df, order_items_df = self.generate_orders_and_items(
            customers_df=customers_df,
            products_df=products_df,
            n_orders=num_orders
        )
        payments_df = self.generate_payments(orders_df=orders_df)
        events_df = self.generate_events(
            customers_df=customers_df,
            products_df=products_df,
            orders_df=orders_df,
            n_events=num_events
        )

        dataset = {
            "customers": customers_df,
            "products": products_df,
            "orders": orders_df,
            "order_items": order_items_df,
            "payments": payments_df,
            "events": events_df
        }
        logger.info("=== All Datasets Generated Successfully ===")
        return dataset

    def save_to_csv(
        self,
        datasets: Dict[str, pd.DataFrame],
        output_dir: Path = DATA_RAW_DIR
    ) -> Dict[str, Path]:
        """Saves generated DataFrames to separate CSV files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_paths: Dict[str, Path] = {}

        for name, df in datasets.items():
            filepath = output_dir / f"{name}.csv"
            df.to_csv(filepath, index=False, encoding="utf-8")
            saved_paths[name] = filepath
            logger.info(f"Saved {name}.csv: {len(df):,} records ({filepath.stat().st_size / 1024:.1f} KB)")

        return saved_paths
