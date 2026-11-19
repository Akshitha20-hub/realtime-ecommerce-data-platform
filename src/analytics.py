"""
Analytics helper.

Provides :func:`run_query` which executes one of the SQL files in
``sql/analytics/`` against the warehouse and returns a pandas DataFrame.
Since Docker / PostgreSQL might not be running in every environment, the module
also provides :func:`generate_sample_data` which returns realistic *synthetic*
data so the dashboard always has something to display.
"""

import pathlib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

SQL_DIR = pathlib.Path(__file__).resolve().parents[1] / "sql" / "analytics"


# ---------------------------------------------------------------------------
# Live database helper (requires PostgreSQL to be running)
# ---------------------------------------------------------------------------
def run_query(sql_filename: str) -> pd.DataFrame:
    """Execute *sql_filename* from ``sql/analytics/`` and return a DataFrame.

    Raises ``RuntimeError`` if the DB is not reachable.
    """
    try:
        from src.database.connection import get_engine
        engine = get_engine()
        sql = (SQL_DIR / sql_filename).read_text(encoding="utf-8")
        with engine.connect() as conn:
            return pd.read_sql(sql, conn)
    except Exception as exc:
        raise RuntimeError(f"DB query failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Offline / demo data generators
# ---------------------------------------------------------------------------
def _month_labels(n: int = 12) -> list[str]:
    base = datetime(2024, 1, 1)
    return [(base + timedelta(days=30 * i)).strftime("%b %Y") for i in range(n)]


def demo_revenue_summary() -> dict:
    return {
        "total_revenue": 4_823_650.75,
        "total_orders":  8_412,
        "avg_order_value": 573.42,
    }


def demo_monthly_revenue() -> pd.DataFrame:
    months = _month_labels(12)
    np.random.seed(42)
    revenue = np.random.randint(280_000, 520_000, size=12).astype(float)
    orders  = np.random.randint(550, 950, size=12)
    return pd.DataFrame({
        "month":           months,
        "monthly_revenue": revenue,
        "total_orders":    orders,
    })


def demo_category_performance() -> pd.DataFrame:
    categories = [
        "Electronics", "Clothing", "Beauty & Personal Care",
        "Home & Kitchen", "Sports", "Books", "Toys", "Health",
    ]
    np.random.seed(0)
    revenue  = np.random.randint(200_000, 900_000, size=len(categories))
    units    = np.random.randint(1_000, 8_000,     size=len(categories))
    ratings  = np.round(np.random.uniform(3.5, 5.0, size=len(categories)), 2)
    return pd.DataFrame({
        "category":      categories,
        "total_revenue": revenue,
        "total_units_sold": units,
        "avg_rating":    ratings,
    }).sort_values("total_revenue", ascending=False)


def demo_top_products() -> pd.DataFrame:
    products = [
        "Elite Sunscreen SPF 50", "Eco Smartphone Pro", "Compact Bluetooth Speaker",
        "Yoga Mat Ultra", "Organic Face Cream", "Running Shoes X", "DSLR Camera 4K",
        "Stainless Water Bottle", "Gaming Headset", "Smart Watch Series 5",
        "Portable Charger 20K", "LED Desk Lamp", "Cotton T-Shirt Pack", "Puzzle 1000pc",
        "Resistance Bands Set", "Protein Powder Vanilla", "Noise-Cancel Earbuds",
        "Cookware Set 10pc", "Sketch Pad A3", "Tennis Racket Pro",
    ]
    np.random.seed(7)
    revenue = sorted(np.random.randint(15_000, 90_000, size=len(products)), reverse=True)
    units   = np.random.randint(100, 800, size=len(products))
    return pd.DataFrame({
        "product_name":  products,
        "total_revenue": revenue,
        "total_units_sold": units,
    })


def demo_order_status_funnel() -> pd.DataFrame:
    return pd.DataFrame({
        "order_status": ["completed", "shipped", "pending", "cancelled", "returned"],
        "order_count":  [5_200, 2_100, 1_800, 900, 412],
        "pct_of_total": [49.5, 20.0, 17.1, 8.6, 3.9],
    })


def demo_payment_analysis() -> pd.DataFrame:
    methods  = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet"] * 2
    statuses = (["completed"] * 5) + (["failed"] * 5)
    np.random.seed(3)
    counts  = np.random.randint(500, 3_000, size=10)
    amounts = np.random.randint(100_000, 900_000, size=10).astype(float)
    return pd.DataFrame({
        "payment_method": methods,
        "payment_status": statuses,
        "payment_count":  counts,
        "total_amount":   amounts,
    })


def demo_event_funnel() -> pd.DataFrame:
    return pd.DataFrame({
        "event_type":       ["product_view", "add_to_cart", "checkout", "purchase", "return", "cancellation"],
        "event_count":      [40_375, 18_500, 12_200, 8_412, 1_050, 900],
        "unique_customers": [1_480,   1_200,     980,   840,   310,  290],
    })


def demo_repeat_customers() -> pd.DataFrame:
    return pd.DataFrame({
        "repeat_flag":    ["Repeat", "One-Time"],
        "customer_count": [1_040, 440],
    })


def demo_revenue_by_state() -> pd.DataFrame:
    states  = ["CA", "TX", "NY", "FL", "IL", "WA", "MA", "GA", "CO", "AZ"]
    np.random.seed(5)
    revenue = sorted(np.random.randint(80_000, 600_000, size=len(states)), reverse=True)
    orders  = np.random.randint(200, 1_200, size=len(states))
    return pd.DataFrame({
        "state":         states,
        "total_revenue": revenue,
        "total_orders":  orders,
    })
