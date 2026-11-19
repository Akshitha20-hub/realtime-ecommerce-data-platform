'''Create the PostgreSQL schema.

Usage:
    python scripts/create_schema.py
'''

import sys
import pathlib

# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.database.connection import get_engine
from src.database.schema_manager import create_schema, create_indexes


def main() -> None:
    engine = get_engine()
    try:
        create_schema(engine)
        create_indexes(engine)
    except Exception as exc:
        print(f"❌ Failed to create schema: {exc}")
        sys.exit(1)
    else:
        print("✅ Schema creation completed.")


if __name__ == "__main__":
    main()
