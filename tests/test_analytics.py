"""
Unit Tests for Analytics SQL Queries and Fallback Data
======================================================
"""

import unittest
import pathlib
from src.analytics import (
    SQL_DIR,
    demo_revenue_summary,
    demo_monthly_revenue,
    demo_category_performance,
    demo_top_products,
    demo_order_status_funnel,
    demo_payment_analysis,
    demo_event_funnel,
    demo_repeat_customers,
    demo_revenue_by_state,
)


class TestAnalytics(unittest.TestCase):
    """Verify all SQL query files exist and demo generators output valid DataFrames."""

    def test_sql_files_exist(self):
        expected_sql = [
            "revenue_summary.sql",
            "monthly_revenue.sql",
            "top_products.sql",
            "category_performance.sql",
            "customer_lifetime_value.sql",
            "order_status_funnel.sql",
            "payment_analysis.sql",
            "event_funnel.sql",
            "repeat_customers.sql",
            "revenue_by_state.sql",
        ]
        for sql_file in expected_sql:
            path = SQL_DIR / sql_file
            self.assertTrue(path.exists(), f"Missing SQL analytics file: {sql_file}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("SELECT", content.upper())

    def test_demo_dataframes(self):
        self.assertGreater(demo_revenue_summary()["total_revenue"], 0)
        self.assertEqual(len(demo_monthly_revenue()), 12)
        self.assertEqual(len(demo_category_performance()), 8)
        self.assertEqual(len(demo_top_products()), 20)
        self.assertEqual(len(demo_order_status_funnel()), 5)
        self.assertEqual(len(demo_payment_analysis()), 10)
        self.assertEqual(len(demo_event_funnel()), 6)
        self.assertEqual(len(demo_repeat_customers()), 2)
        self.assertEqual(len(demo_revenue_by_state()), 10)


if __name__ == "__main__":
    unittest.main()
