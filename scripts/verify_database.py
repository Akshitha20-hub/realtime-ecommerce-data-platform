'''Verify the PostgreSQL warehouse.

Usage:
    python scripts/verify_database.py
'''

import sys
import pathlib

# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from src.database.connection import get_engine


def _row_count(conn, table: str) -> int:
    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
    return result.scalar()


def main():
    engine = get_engine()
    tables = ["customers", "products", "orders", "order_items", "payments", "events"]
    print("🔎 Warehouse Verification Report:")
    print("---------------------------------")
    with engine.connect() as conn:
        for tbl in tables:
            try:
                cnt = _row_count(conn, tbl)
                print(f"  ✅ {tbl:<15}: {cnt:>7,} rows")
            except Exception as e:
                print(f"  ❌ Error reading {tbl}: {e}")
                sys.exit(1)
    print("---------------------------------")
    print("✅ All warehouse tables reachable and verified.")


if __name__ == "__main__":
    main()
