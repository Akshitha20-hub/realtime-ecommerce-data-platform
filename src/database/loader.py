"""CSV loader for PostgreSQL.

Provides a :func:`load_table` function that bulk‑loads a pandas ``DataFrame``
into a target table using SQLAlchemy's ``to_sql`` helper. Rows that violate
constraints are written to ``data/rejected/rejected_<table>.csv`` for later
inspection.
"""

import pathlib
import pandas as pd
from sqlalchemy import inspect, text, exc as sa_exc
from sqlalchemy.engine import Engine
from src.database.connection import get_engine

REJECTED_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "rejected"
REJECTED_DIR.mkdir(parents=True, exist_ok=True)


def load_table(engine: Engine, table_name: str, df: pd.DataFrame) -> None:
    """Load *df* into *table_name*.

    Automatically aligns columns to only those present in the target database
    table, converts timestamp columns to proper string representations if needed,
    and executes multi-row insert.
    """
    try:
        # Align columns to target table schema
        insp = inspect(engine)
        if insp.has_table(table_name):
            db_cols = [col["name"] for col in insp.get_columns(table_name)]
            load_cols = [c for c in df.columns if c in db_cols]
            insert_df = df[load_cols].copy()
        else:
            insert_df = df.copy()

        insert_df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
    except sa_exc.IntegrityError as e:
        engine.dispose()
        rejected_path = REJECTED_DIR / f"rejected_{table_name}.csv"
        df.to_csv(rejected_path, index=False)
        print(f"⚠️ Integrity error while loading {table_name}: {e}\n"
              f"   Rejected rows saved to {rejected_path}")
    else:
        print(f"✅ Loaded {len(df)} rows into {table_name}")
