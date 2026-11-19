# Database schema manager
"""Utilities to create the PostgreSQL schema and indexes for the e‑commerce warehouse.

The schema is stored in ``sql/schema.sql`` and indexes are stored in ``sql/indexes.sql``.
The functions read those files and execute them against a SQLAlchemy engine.
"""

import pathlib
from sqlalchemy import text
from sqlalchemy.engine import Engine

SQL_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql"
SCHEMA_PATH = SQL_DIR / "schema.sql"
INDEXES_PATH = SQL_DIR / "indexes.sql"


def create_schema(engine: Engine) -> None:
    """Create all tables defined in ``sql/schema.sql``.

    The function is idempotent because the SQL uses ``CREATE TABLE IF NOT EXISTS``.
    """
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in schema_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
    print("✅ Schema created (or already existed).")


def create_indexes(engine: Engine) -> None:
    """Create all performance indexes defined in ``sql/indexes.sql``."""
    if not INDEXES_PATH.exists():
        return
    indexes_sql = INDEXES_PATH.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in indexes_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
    print("✅ Performance indexes created (or already existed).")
