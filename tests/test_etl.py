"""
Unit and Integration Tests for Batch ETL Pipeline
==================================================
Tests extraction, transformation logic, metric computations, and reporting.
"""

import unittest
import pandas as pd
from src.etl.transform import (
    transform_customers,
    transform_products,
    transform_orders,
    transform_order_items,
    transform_payments,
    transform_events,
)
from src.etl.metrics import compute_metrics
from src.etl.report import render_report


class TestETLTransformations(unittest.TestCase):
    """Test data transformation cleaning and feature engineering."""

    def test_transform_customers(self):
        raw = pd.DataFrame({
            "customer_id": [" CUST-001 "],
            "signup_date": ["2024-05-10 14:30:00"],
            "city": ["  New York  "],
        })
        res = transform_customers(raw)
        self.assertEqual(res["customer_id"].iloc[0], "CUST-001")
        self.assertEqual(res["city"].iloc[0], "New York")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(res["signup_date"]))

    def test_transform_orders_derived_columns(self):
        raw = pd.DataFrame({
            "order_id": ["ORD-1"],
            "order_date": ["2024-03-15 10:00:00"],
            "total_amount": [120.50],
        })
        res = transform_orders(raw)
        self.assertIn("order_year", res.columns)
        self.assertIn("order_month", res.columns)
        self.assertEqual(res["order_year"].iloc[0], 2024)
        self.assertEqual(res["order_month"].iloc[0], 3)

    def test_transform_order_items_profit(self):
        items = pd.DataFrame({
            "order_item_id": ["ITM-1"],
            "product_id": ["PROD-1"],
            "quantity": [2],
            "unit_price": [50.0],
            "discount": [10.0],
        })
        prods = pd.DataFrame({
            "product_id": ["PROD-1"],
            "cost": [20.0],
        })
        res = transform_order_items(items, prods)
        self.assertIn("profit", res.columns)
        # profit = (50 - 20) * 2 - 10 = 50.0
        self.assertAlmostEqual(res["profit"].iloc[0], 50.0)

    def test_compute_metrics(self):
        store = {
            "customers": pd.DataFrame({"a": [1, 2, 3]}),
            "orders": pd.DataFrame({"b": [1, 2]}),
        }
        m = compute_metrics(store)
        self.assertEqual(m["row_counts"]["customers"], 3)
        self.assertEqual(m["row_counts"]["orders"], 2)

    def test_render_report(self):
        metrics = {"row_counts": {"orders": 100}}
        val_rep = {
            "overall_status": "PASSED",
            "summary": {"total_checks": 10, "passed_checks": 10, "failed_checks": 0, "pass_rate_pct": 100.0},
            "detailed_results": []
        }
        rep = render_report("test-run-123", "2026-11-18T12:00:00", "SUCCESS", metrics, val_rep)
        self.assertIn("test-run-123", rep)
        self.assertIn("SUCCESS", rep)
        self.assertIn("100.0%", rep)


if __name__ == "__main__":
    unittest.main()
