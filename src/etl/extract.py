"""Extraction utilities for the ETL pipeline.

The :func:`extract_csv` helper reads a CSV file into a pandas ``DataFrame`` and
records basic metadata (file size, extraction time) for logging.
"""

import pathlib
import pandas as pd
from datetime import datetime


def extract_csv(csv_path: pathlib.Path) -> pd.DataFrame:
    """Read *csv_path* into a DataFrame.

    Raises ``FileNotFoundError`` if the path does not exist.
    """
    start = datetime.utcnow()
    df = pd.read_csv(csv_path)
    elapsed = (datetime.utcnow() - start).total_seconds()
    print(
        f"🔽 Extracted {csv_path.name} ({len(df)} rows) in {elapsed:.2f}s, "
        f"size={csv_path.stat().st_size/1024:.1f}KB"
    )
    return df
