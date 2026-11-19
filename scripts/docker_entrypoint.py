"""
Docker Container Entrypoint
===========================
Orchestrates container startup:
1. Waits for PostgreSQL to be healthy and accepting connections.
2. Applies SQL schema and performance indexes.
3. Automatically runs the batch ETL pipeline if the warehouse is empty.
4. Starts the Streamlit business intelligence dashboard.
"""

import os
import sys
import time
import subprocess
from sqlalchemy import text
from src.database.connection import get_engine
from src.database.schema_manager import create_schema, create_indexes
from src.etl.pipeline import run_etl


def wait_for_db(max_retries: int = 30, delay: int = 2) -> None:
    """Poll database until connection succeeds."""
    print("⏳ Waiting for PostgreSQL database to be ready...")
    engine = get_engine()
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Connected to PostgreSQL successfully!")
            return
        except Exception as exc:
            print(f"   [Attempt {attempt}/{max_retries}] Database not ready yet: {exc}")
            time.sleep(delay)
    print("❌ Timed out waiting for PostgreSQL.")
    sys.exit(1)


def initialize_warehouse() -> None:
    """Initialize schema, indexes, and load initial data if empty."""
    engine = get_engine()
    print("🚀 Initializing warehouse schema and indexes...")
    create_schema(engine)
    create_indexes(engine)

    # Check if orders table already has data
    with engine.connect() as conn:
        try:
            count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        except Exception:
            count = 0

    if count == 0:
        print("📦 Database is empty. Running initial ETL pipeline to populate warehouse...")
        result = run_etl()
        print(f"✅ ETL finished with status: {result['status']}")
    else:
        print(f"ℹ️ Warehouse already contains {count:,} orders. Skipping initial data load.")


def start_dashboard() -> None:
    """Launch the Streamlit analytics dashboard."""
    print("🌐 Starting Streamlit Dashboard on port 8501...")
    cmd = [
        "streamlit", "run", "dashboard/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ]
    subprocess.run(cmd)


def main() -> None:
    wait_for_db()
    initialize_warehouse()
    start_dashboard()


if __name__ == "__main__":
    main()
