"""Transformation utilities for the ETL pipeline.

The functions clean column values, enforce correct dtypes, parse dates, and add a few derived columns:
- ``order_year`` and ``order_month`` for the ``orders`` table.
- ``profit`` on ``order_items`` ( (unit_price - cost) * quantity - discount ).

All transformations are deliberately simple and deterministic so a beginner can follow.
"""

import pandas as pd
from datetime import datetime


def _clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    # Strip whitespace from all object columns
    obj_cols = df.select_dtypes(include="object").columns
    df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())
    return df


def _parse_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = _clean_strings(df)
    df = _parse_dates(df, ["signup_date"])
    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    df = _clean_strings(df)
    # Ensure numeric columns are proper float/int types
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], downcast="integer", errors="coerce")
    df["product_rating"] = pd.to_numeric(df["product_rating"], errors="coerce")
    return df


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = _clean_strings(df)
    df = _parse_dates(df, ["order_date"])
    # Derive year/month for later analytics
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    return df


def transform_order_items(df: pd.DataFrame, products_df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = _clean_strings(df)
    numeric_cols = ["quantity", "unit_price", "discount"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Optional profit calculation (requires product cost). If ``products_df`` is supplied, merge to get cost.
    if products_df is not None and "product_id" in df.columns:
        merged = df.merge(products_df[["product_id", "cost"]], on="product_id", how="left")
        merged["profit"] = (merged["unit_price"] - merged["cost"]) * merged["quantity"] - merged["discount"]
        df = merged
    else:
        df["profit"] = (df["unit_price"] - 0) * df["quantity"] - df["discount"]
    return df


def transform_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = _clean_strings(df)
    df = _parse_dates(df, ["payment_date"])
    df["payment_amount"] = pd.to_numeric(df["payment_amount"], errors="coerce")
    return df


def transform_events(df: pd.DataFrame) -> pd.DataFrame:
    df = _clean_strings(df)
    df = _parse_dates(df, ["event_timestamp"])
    return df
