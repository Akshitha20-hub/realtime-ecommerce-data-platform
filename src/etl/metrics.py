# Metrics utilities for the ETL pipeline
"""
Calculate simple runtime metrics for the ETL run.
Currently we aggregate per‑table row counts and total duration.
"""

import time
from typing import Dict, Any


def compute_metrics(df_store: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dict with row counts for each table.

    Args:
        df_store: Mapping of table name → pandas DataFrame after transformation.
    Returns:
        Dictionary ``{"row_counts": {table: row_count, ...}}``.
    """
    row_counts = {table: len(df) for table, df in df_store.items()}
    return {"row_counts": row_counts}
