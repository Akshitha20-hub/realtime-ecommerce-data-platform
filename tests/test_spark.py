"""
Unit Tests for Apache Spark & Processing Jobs
=============================================
"""

import unittest
import pandas as pd
from src.spark.rfm_analysis import run_rfm_analysis
from src.spark.window_aggregations import run_window_aggregations


class TestSparkProcessing(unittest.TestCase):
    """Test RFM segmentation and window aggregations."""

    def test_rfm_segmentation_logic(self):
        orders = pd.DataFrame({
            "order_id": [f"ORD-{i}" for i in range(1, 11)],
            "customer_id": ["C1"] * 5 + ["C2"] * 3 + ["C3"] * 2,
            "order_date": ["2024-05-01 10:00:00"] * 5 + ["2024-04-01 10:00:00"] * 3 + ["2024-01-01 10:00:00"] * 2,
            "order_status": ["completed"] * 10,
            "total_amount": [100.0] * 10,
        })
        res = run_rfm_analysis(orders)
        self.assertEqual(len(res), 3)
        self.assertIn("segment", res.columns)
        self.assertIn("rfm_score", res.columns)

    def test_window_aggregations_logic(self):
        events = pd.DataFrame({
            "event_id": [f"EVT-{i}" for i in range(1, 6)],
            "customer_id": ["C1", "C2", "C1", "C3", "C2"],
            "product_id": ["P1", "P2", "P1", "P3", "P2"],
            "event_type": ["product_view", "add_to_cart", "checkout", "purchase", "purchase"],
            "event_timestamp": ["2024-05-01 10:15:00"] * 3 + ["2024-05-01 11:20:00"] * 2,
            "session_id": ["S1", "S1", "S1", "S2", "S2"],
        })
        orders = pd.DataFrame({
            "order_id": ["O1", "O2"],
            "order_date": ["2024-05-01 10:00:00", "2024-06-01 10:00:00"],
            "order_status": ["completed", "completed"],
            "total_amount": [150.0, 200.0],
        })
        res = run_window_aggregations(events, orders)
        traffic = res["hourly_traffic"]
        self.assertEqual(len(traffic), 2)  # Two distinct hours: 10:00 and 11:00
        self.assertIn("conversion_rate_pct", traffic.columns)


if __name__ == "__main__":
    unittest.main()
