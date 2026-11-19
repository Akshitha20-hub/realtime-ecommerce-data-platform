"""
Unit tests for DataValidator.
Validates that the validation suite passes clean datasets and correctly catches
anomalies such as duplicate primary keys, orphaned foreign keys, negative prices,
and chronological violations.
"""

from pathlib import Path
import sys
import unittest
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_generator import EcommerceDataGenerator
from src.validation import DataValidator


class TestDataValidator(unittest.TestCase):
    """Test suite for data validation rules and anomaly detection."""

    @classmethod
    def setUpClass(cls):
        """Generate a baseline clean synthetic dataset for testing."""
        generator = EcommerceDataGenerator(seed=123)
        cls.clean_datasets = generator.generate_all(
            num_customers=40,
            num_products=25,
            num_orders=60,
            num_events=120
        )

    def test_clean_data_passes_all_validations(self):
        """Verify that a properly generated dataset achieves 100% validation pass rate."""
        validator = DataValidator(datasets=self.clean_datasets)
        report = validator.run_all_validations()

        self.assertEqual(report["overall_status"], "PASSED")
        self.assertEqual(report["summary"]["failed_checks"], 0)
        self.assertEqual(report["summary"]["pass_rate_pct"], 100.0)

    def test_detects_duplicate_primary_keys(self):
        """Verify validator flags duplicate IDs."""
        corrupted = {k: v.copy() for k, v in self.clean_datasets.items()}
        # Duplicate the first customer record
        corrupted["customers"] = pd.concat([corrupted["customers"], corrupted["customers"].iloc[[0]]], ignore_index=True)

        validator = DataValidator(datasets=corrupted)
        validator.check_primary_keys()

        dup_check = next(c for c in validator.validation_results if c["check_name"] == "pk_unique_customer_id")
        self.assertEqual(dup_check["status"], "FAILED")
        self.assertEqual(dup_check["failed_count"], 1)

    def test_detects_orphaned_foreign_keys(self):
        """Verify validator flags foreign key referential integrity violations."""
        corrupted = {k: v.copy() for k, v in self.clean_datasets.items()}
        # Inject an invalid customer_id into orders
        corrupted["orders"].loc[0, "customer_id"] = "CUST-NON-EXISTENT-999"

        validator = DataValidator(datasets=corrupted)
        validator.check_referential_integrity()

        fk_check = next(c for c in validator.validation_results if c["check_name"] == "fk_orders_customer_id_in_customers")
        self.assertEqual(fk_check["status"], "FAILED")
        self.assertGreater(fk_check["failed_count"], 0)

    def test_detects_negative_prices_and_quantities(self):
        """Verify validator catches non-positive prices and quantities."""
        corrupted = {k: v.copy() for k, v in self.clean_datasets.items()}
        corrupted["products"].loc[0, "price"] = -49.99
        corrupted["order_items"].loc[0, "quantity"] = 0

        validator = DataValidator(datasets=corrupted)
        validator.check_numeric_ranges()

        price_check = next(c for c in validator.validation_results if c["check_name"] == "products_price_positive")
        self.assertEqual(price_check["status"], "FAILED")

        qty_check = next(c for c in validator.validation_results if c["check_name"] == "order_items_quantity_gte_1")
        self.assertEqual(qty_check["status"], "FAILED")

    def test_detects_chronological_inversions(self):
        """Verify validator catches impossible order date (e.g. order before signup date)."""
        corrupted = {k: v.copy() for k, v in self.clean_datasets.items()}
        # Move order timestamp back to year 2020 (customer signed up in 2024)
        corrupted["orders"].loc[0, "order_date"] = "2020-01-01 10:00:00"

        validator = DataValidator(datasets=corrupted)
        validator.check_chronological_validity()

        chrono_check = next(c for c in validator.validation_results if c["check_name"] == "order_date_after_customer_signup_date")
        self.assertEqual(chrono_check["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
