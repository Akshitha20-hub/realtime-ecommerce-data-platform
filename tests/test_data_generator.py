"""
Unit tests for EcommerceDataGenerator.
Validates record counts, schema conformity, distributions, relational constraints,
and random seed reproducibility.
"""

from pathlib import Path
import sys
import unittest
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_generator import EcommerceDataGenerator
from src.config import PRODUCT_CATEGORIES, ORDER_STATUSES, PAYMENT_METHODS, EVENT_TYPES


class TestEcommerceDataGenerator(unittest.TestCase):
    """Test suite for synthetic data generation functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up a test generator instance with small volume for speed."""
        cls.generator = EcommerceDataGenerator(seed=42)
        cls.num_cust = 50
        cls.num_prod = 30
        cls.num_orders = 100
        cls.num_events = 200

        cls.customers_df = cls.generator.generate_customers(n=cls.num_cust)
        cls.products_df = cls.generator.generate_products(n=cls.num_prod)
        cls.orders_df, cls.order_items_df = cls.generator.generate_orders_and_items(
            customers_df=cls.customers_df,
            products_df=cls.products_df,
            n_orders=cls.num_orders
        )
        cls.payments_df = cls.generator.generate_payments(orders_df=cls.orders_df)
        cls.events_df = cls.generator.generate_events(
            customers_df=cls.customers_df,
            products_df=cls.products_df,
            orders_df=cls.orders_df,
            n_events=cls.num_events
        )

    def test_customers_schema_and_integrity(self):
        """Verify customers table dimensions, columns, and uniqueness."""
        self.assertEqual(len(self.customers_df), self.num_cust)
        expected_cols = {
            "customer_id", "first_name", "last_name", "email", "gender",
            "age", "city", "state", "signup_date", "customer_segment"
        }
        self.assertTrue(expected_cols.issubset(set(self.customers_df.columns)))
        self.assertEqual(self.customers_df["customer_id"].nunique(), self.num_cust)
        self.assertFalse(self.customers_df["email"].isnull().any())
        self.assertTrue((self.customers_df["age"] >= 18).all())

    def test_products_schema_and_ranges(self):
        """Verify products prices, costs, ratings, categories, and inventory."""
        self.assertEqual(len(self.products_df), self.num_prod)
        expected_cols = {
            "product_id", "product_name", "category", "subcategory",
            "price", "cost", "stock_quantity", "product_rating"
        }
        self.assertTrue(expected_cols.issubset(set(self.products_df.columns)))
        self.assertTrue((self.products_df["price"] > 0).all())
        self.assertTrue((self.products_df["cost"] > 0).all())
        self.assertTrue((self.products_df["cost"] <= self.products_df["price"]).all())
        self.assertTrue((self.products_df["stock_quantity"] >= 0).all())
        self.assertTrue(((self.products_df["product_rating"] >= 1.0) & (self.products_df["product_rating"] <= 5.0)).all())

        valid_categories = set(PRODUCT_CATEGORIES.keys())
        self.assertTrue(set(self.products_df["category"].unique()).issubset(valid_categories))

    def test_orders_and_items_relationships(self):
        """Verify orders line item aggregation and foreign key linkage."""
        self.assertEqual(len(self.orders_df), self.num_orders)
        self.assertGreaterEqual(len(self.order_items_df), self.num_orders)

        # Referential integrity check
        cust_ids = set(self.customers_df["customer_id"])
        self.assertTrue(set(self.orders_df["customer_id"]).issubset(cust_ids))

        ord_ids = set(self.orders_df["order_id"])
        self.assertTrue(set(self.order_items_df["order_id"]).issubset(ord_ids))

        prod_ids = set(self.products_df["product_id"])
        self.assertTrue(set(self.order_items_df["product_id"]).issubset(prod_ids))

        # Check line item math: subtotal == round(quantity * unit_price - discount, 2)
        expected_subtotals = (self.order_items_df["quantity"] * self.order_items_df["unit_price"] - self.order_items_df["discount"]).round(2)
        diff = abs(self.order_items_df["subtotal"] - expected_subtotals)
        self.assertTrue((diff <= 0.01).all())

    def test_payments_consistency(self):
        """Verify payment amounts match order totals and status logic."""
        self.assertEqual(len(self.payments_df), self.num_orders)

        merged = self.payments_df.merge(self.orders_df, on="order_id")
        amount_diff = abs(merged["payment_amount"] - merged["total_amount"])
        self.assertTrue((amount_diff <= 0.01).all())

        # Check payment methods
        valid_methods = {m[0] for m in PAYMENT_METHODS}
        self.assertTrue(set(self.payments_df["payment_method"]).issubset(valid_methods))

    def test_events_funnel_generation(self):
        """Verify event records are generated and contain proper event types."""
        self.assertGreater(len(self.events_df), 0)
        expected_cols = {
            "event_id", "customer_id", "product_id", "event_type",
            "event_timestamp", "session_id"
        }
        self.assertTrue(expected_cols.issubset(set(self.events_df.columns)))
        valid_types = set(EVENT_TYPES)
        self.assertTrue(set(self.events_df["event_type"]).issubset(valid_types))

    def test_reproducibility_with_seed(self):
        """Verify that identical seeds produce bitwise identical DataFrames."""
        gen1 = EcommerceDataGenerator(seed=777)
        cust1 = gen1.generate_customers(n=25)

        gen2 = EcommerceDataGenerator(seed=777)
        cust2 = gen2.generate_customers(n=25)

        pd.testing.assert_frame_equal(cust1, cust2)


if __name__ == "__main__":
    unittest.main()
