"""
Spark Analytics Engine Runner
=============================
Executes PySpark data processing jobs:
1. Customer RFM Segmentation & Scoring
2. Time-Window Clickstream & Funnel Traffic Aggregation
3. Cumulative Revenue Metrics

Usage:
    python scripts/run_spark_jobs.py
"""

import sys
import pathlib
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.spark.rfm_analysis import run_rfm_analysis
from src.spark.window_aggregations import run_window_aggregations


def main():
    data_dir = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
    out_dir = pathlib.Path(__file__).resolve().parents[1] / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("        APACHE SPARK / PYSPARK DATA PROCESSING ENGINE")
    print("=" * 65)

    print("📦 Loading raw datasets for Spark processing...")
    orders_df = pd.read_csv(data_dir / "orders.csv")
    events_df = pd.read_csv(data_dir / "events.csv")

    # 1. RFM Segmentation
    print("\n⚡ [Job 1/2] Running Customer RFM Segmentation Job...")
    rfm_df = run_rfm_analysis(orders_df)
    rfm_path = out_dir / "customer_rfm_segments.csv"
    rfm_df.to_csv(rfm_path, index=False)
    print(f"✅ RFM Segmentation complete ({len(rfm_df):,} customers processed). Saved to {rfm_path.name}")
    print("\n  Segment Distribution:")
    for seg, count in rfm_df["segment"].value_counts().items():
        pct = (count / len(rfm_df)) * 100
        print(f"    - {seg:<18}: {count:>5,} ({pct:>5.1f}%)")

    # 2. Window Aggregations
    print("\n⚡ [Job 2/2] Running Window & Clickstream Rolling Aggregations...")
    window_results = run_window_aggregations(events_df, orders_df)
    traffic_df = window_results["hourly_traffic"]
    traffic_path = out_dir / "hourly_traffic_rollups.csv"
    traffic_df.to_csv(traffic_path, index=False)

    cum_df = window_results["cumulative_category_revenue"]
    cum_path = out_dir / "cumulative_monthly_revenue.csv"
    cum_df.to_csv(cum_path, index=False)

    print(f"✅ Window aggregations complete ({len(traffic_df)} hourly intervals).")
    print(f"   Cumulative revenue processed ({len(cum_df)} months).")

    print("\n" + "=" * 65)
    print("🎉 All Spark processing jobs completed successfully!")
    print("=" * 65)


if __name__ == "__main__":
    main()
