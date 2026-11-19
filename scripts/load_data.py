'''Load CSV files into PostgreSQL.

Usage:
    python scripts/load_data.py
'''

import sys
import pathlib

# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
from src.database.connection import get_engine
from src.database.loader import load_table

DATA_ROOT = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
TABLES = [
    ("customers", "customers.csv"),
    ("products", "products.csv"),
    ("orders", "orders.csv"),
    ("order_items", "order_items.csv"),
    ("payments", "payments.csv"),
    ("events", "events.csv"),
]


def main() -> None:
    engine = get_engine()
    for table_name, filename in TABLES:
        csv_path = DATA_ROOT / filename
        print(f"🔽 Loading {csv_path.name} → {table_name}")
        df = pd.read_csv(csv_path)
        load_table(engine, table_name, df)


if __name__ == "__main__":
    main()
