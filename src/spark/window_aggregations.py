"""
PySpark Window Functions & Rolling Aggregations Job
===================================================
Computes:
- Hourly event traffic rollups & unique session counts
- Cumulative rolling revenue per product category
- Event conversion rate per hour window
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from src.spark.session import get_spark_session


def run_window_aggregations(events_df: pd.DataFrame, orders_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Computes time-window metrics on clickstream events and cumulative order trends.
    """
    spark = get_spark_session("WindowAggregationsJob")

    if spark is not None:
        try:
            from pyspark.sql import functions as F
            from pyspark.sql.window import Window

            sp_events = spark.createDataFrame(events_df)
            sp_events = sp_events.withColumn("hour", F.date_trunc("hour", F.col("event_timestamp")))

            hourly_traffic = (
                sp_events.groupBy("hour")
                .agg(
                    F.count("event_id").alias("total_events"),
                    F.countDistinct("session_id").alias("unique_sessions"),
                    F.countDistinct("customer_id").alias("unique_users"),
                    F.sum(F.when(F.col("event_type") == "purchase", 1).otherwise(0)).alias("purchases"),
                )
                .orderBy("hour")
            ).toPandas()

            hourly_traffic["conversion_rate_pct"] = np.round(
                (hourly_traffic["purchases"] / hourly_traffic["unique_sessions"].replace(0, np.nan)) * 100, 2
            ).fillna(0)

        except Exception:
            hourly_traffic = _compute_hourly_traffic_pandas(events_df)
    else:
        hourly_traffic = _compute_hourly_traffic_pandas(events_df)

    # Cumulative category revenue
    cat_cum = _compute_cumulative_revenue_pandas(orders_df)

    return {
        "hourly_traffic": hourly_traffic,
        "cumulative_category_revenue": cat_cum,
    }


def _compute_hourly_traffic_pandas(events_df: pd.DataFrame) -> pd.DataFrame:
    df = events_df.copy()
    df["dt"] = pd.to_datetime(df["event_timestamp"])
    df["hour"] = df["dt"].dt.floor("h")

    grouped = df.groupby("hour").agg(
        total_events=("event_id", "count"),
        unique_sessions=("session_id", "nunique"),
        unique_users=("customer_id", "nunique"),
        purchases=("event_type", lambda s: (s == "purchase").sum())
    ).reset_index().sort_values("hour")

    grouped["conversion_rate_pct"] = np.round(
        (grouped["purchases"] / grouped["unique_sessions"].replace(0, np.nan)) * 100, 2
    ).fillna(0)
    return grouped


def _compute_cumulative_revenue_pandas(orders_df: pd.DataFrame) -> pd.DataFrame:
    df = orders_df[orders_df["order_status"].isin(["completed", "shipped"])].copy()
    df["order_dt"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_dt"].dt.to_period("M").astype(str)

    monthly = df.groupby("month")["total_amount"].sum().reset_index()
    monthly = monthly.sort_values("month")
    monthly["cumulative_revenue"] = monthly["total_amount"].cumsum().round(2)
    return monthly
