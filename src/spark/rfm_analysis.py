"""
PySpark RFM (Recency, Frequency, Monetary) Customer Segmentation Job
====================================================================
Computes:
- Recency: Days since last order
- Frequency: Total distinct completed orders
- Monetary: Total lifetime revenue spend
- RFM Score & Segment (Champions, Loyal Customers, Potential, At Risk, Lost)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from src.spark.session import get_spark_session


def run_rfm_analysis(orders_df: pd.DataFrame, reference_date: Optional[str] = None) -> pd.DataFrame:
    """
    Executes RFM segmentation. Uses PySpark DataFrame when Spark is active,
    or equivalent vectorized transformations.
    """
    spark = get_spark_session("RFMSegmentationJob")

    if spark is not None:
        try:
            from pyspark.sql import functions as F
            from pyspark.sql.window import Window

            spark_df = spark.createDataFrame(orders_df)
            completed = spark_df.filter(F.col("order_status").isin("completed", "shipped"))

            rfm = completed.groupBy("customer_id").agg(
                F.max("order_date").alias("last_order_date"),
                F.countDistinct("order_id").alias("frequency"),
                F.round(F.sum("total_amount"), 2).alias("monetary")
            )

            # Convert to Pandas for downstream reporting
            result_df = rfm.toPandas()
        except Exception:
            result_df = _compute_rfm_pandas(orders_df)
    else:
        result_df = _compute_rfm_pandas(orders_df)

    # Calculate Recency in days
    max_date = pd.to_datetime(result_df["last_order_date"]).max()
    result_df["recency_days"] = (max_date - pd.to_datetime(result_df["last_order_date"])).dt.days

    # Quartile-based RFM Scoring
    result_df["r_score"] = pd.qcut(result_df["recency_days"].rank(method="first"), q=4, labels=[4, 3, 2, 1]).astype(int)
    result_df["f_score"] = pd.qcut(result_df["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    result_df["m_score"] = pd.qcut(result_df["monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    result_df["rfm_score"] = result_df["r_score"].astype(str) + result_df["f_score"].astype(str) + result_df["m_score"].astype(str)

    def assign_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 3 and f >= 3 and m >= 3:
            return "Champions"
        elif f >= 3 and m >= 2:
            return "Loyal Customers"
        elif r >= 3 and f <= 2:
            return "Recent Potential"
        elif r <= 2 and f >= 2:
            return "At Risk"
        else:
            return "Lost Customers"

    result_df["segment"] = result_df.apply(assign_segment, axis=1)
    return result_df


def _compute_rfm_pandas(orders_df: pd.DataFrame) -> pd.DataFrame:
    completed = orders_df[orders_df["order_status"].isin(["completed", "shipped"])].copy()
    rfm = completed.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("total_amount", lambda s: round(s.sum(), 2))
    ).reset_index()
    return rfm
