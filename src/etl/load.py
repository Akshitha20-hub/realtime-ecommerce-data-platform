"""Loading utilities for the ETL pipeline.

The :func:`load_to_db` function receives a pandas ``DataFrame`` and a target
table name, then uses the generic ``loader.load_table`` implementation.  It
returns the number of rows that were attempted to be inserted (successful rows
are logged by the loader; any integrity errors are written to ``data/rejected``).
"""

import pandas as pd
from src.database.loader import load_table
from src.database.connection import get_engine


def load_to_db(table_name: str, df: pd.DataFrame) -> int:
    """Load *df* into *table_name* and return the attempted row count.

    Args:
        table_name: The destination PostgreSQL table.
        df: Data to insert.
    Returns:
        Number of rows that were fed to the loader (the caller can treat this as
        the number of rows processed; the loader itself logs any rejected rows).
    """
    engine = get_engine()
    load_table(engine, table_name, df)
    return len(df)
