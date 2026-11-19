"""ETL pipeline orchestrator.

The pipeline performs the classic **ELTV** steps:

1. **Extract** – read each raw CSV into a pandas ``DataFrame``.
2. **Transform** – clean strings, enforce dtypes, parse dates and add derived
   columns (see ``src.etl.transform``).
3. **Validate** – reuse the existing ``DataValidator`` logic to ensure the data
   still conforms after transformation.
4. **Load** – bulk‑load the cleaned frames into PostgreSQL using ``load_to_db``.
5. **Audit** – write an entry to the ``etl_run_log`` table with counts and status.

The function returns a dictionary that can be rendered as a markdown report via
``src.etl.report``.
"""

import datetime
import pathlib
import uuid
from typing import Dict

import pandas as pd

from src.etl.extract import extract_csv
from src.etl.transform import (
    transform_customers,
    transform_products,
    transform_orders,
    transform_order_items,
    transform_payments,
    transform_events,
)
from src.validation import DataValidator
from src.etl.load import load_to_db
from sqlalchemy import text
from src.database.connection import get_engine
from src.database.schema_manager import create_schema
from src.etl.report import render_report
from src.etl.metrics import compute_metrics

DATA_ROOT = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw"

TABLES = {
    "customers": ("customers.csv", transform_customers),
    "products": ("products.csv", transform_products),
    "orders": ("orders.csv", transform_orders),
    "order_items": ("order_items.csv", transform_order_items),
    "payments": ("payments.csv", transform_payments),
    "events": ("events.csv", transform_events),
}


def run_etl() -> Dict:
    """Execute the full ETL pipeline.

    Returns a dict containing run metadata, per‑table row counts and validation
    results.  The caller can persist this dict (e.g., as JSON) or render a human
    readable markdown report.
    """
    engine = get_engine()
    # Ensure schema exists – safe to call every run.
    create_schema(engine)

    run_id = str(uuid.uuid4())
    run_timestamp = datetime.datetime.utcnow().isoformat()
    overall_status = "SUCCESS"
    error_message = None

    per_table_counts = {}
    df_store: Dict[str, pd.DataFrame] = {}

    # ------------------- Extract & Transform -------------------
    for table, (filename, transform_fn) in TABLES.items():
        csv_path = DATA_ROOT / filename
        df_raw = extract_csv(csv_path)
        # order_items needs the products DF for profit calculation; pass if needed.
        if table == "order_items":
            df_trans = transform_fn(df_raw, df_store.get("products"))
        else:
            df_trans = transform_fn(df_raw)
        df_store[table] = df_trans
        per_table_counts[table] = len(df_trans)

    # ------------------- Validation -------------------
    validator = DataValidator(datasets=df_store)
    report = validator.run_all_validations()
    validator.save_report(report)
    if report["overall_status"] != "PASSED":
        overall_status = "FAILED"
        error_message = "Validation failures detected – see validation_report.json"

    # ------------------- Load -------------------
    if overall_status == "SUCCESS":
        try:
            for table, df in df_store.items():
                load_to_db(table, df)
        except Exception as exc:  # pragma: no cover – unexpected DB errors
            overall_status = "FAILED"
            error_message = f"Load error: {exc}"

    # ------------------- Audit -------------------
    audit_sql = """
        INSERT INTO etl_run_log (
            run_id, pipeline_name, dataset_name, rows_processed, rows_success, rows_failed, status, error_message
        ) VALUES (
            :run_id, :pipeline_name, :dataset_name, :rows_processed, :rows_success, :rows_failed, :status, :error_message
        )
    """
    with engine.begin() as conn:
        conn.execute(
            text(audit_sql),
            {
                "run_id": run_id,
                "pipeline_name": "realtime_etl",
                "dataset_name": "ecommerce_raw",
                "rows_processed": sum(per_table_counts.values()),
                "rows_success": sum(per_table_counts.values()) if overall_status == "SUCCESS" else 0,
                "rows_failed": 0 if overall_status == "SUCCESS" else sum(per_table_counts.values()),
                "status": overall_status,
                "error_message": error_message,
            },
        )

    # ------------------- Metrics & Report -------------------
    metrics = compute_metrics(df_store)
    markdown_report = render_report(run_id, run_timestamp, overall_status, metrics, report)
    # Save the markdown report for the user.
    reports_dir = pathlib.Path(__file__).resolve().parents[2] / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"etl_run_{run_timestamp.replace(':', '-')}.md"
    report_path.write_text(markdown_report, encoding="utf-8")
    print(f"📝 ETL run report saved to {report_path}")

    return {
        "run_id": run_id,
        "timestamp": run_timestamp,
        "status": overall_status,
        "error_message": error_message,
        "row_counts": per_table_counts,
        "validation_report": report,
    }


if __name__ == "__main__":
    run_etl()
