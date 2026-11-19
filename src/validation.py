"""
Data Validation and Quality Assurance Module.
Validates synthetic e-commerce datasets against schema rules, primary key uniqueness,
foreign key referential integrity, range and sanity constraints, business logic,
and chronological consistency. Supports partitioning and isolating rejected records.
"""

from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import DATA_RAW_DIR, DATA_REJECTED_DIR, REPORTS_DIR
from src.logger import get_logger

logger = get_logger("EcommercePlatform.Validator", "validation.log")


class DataValidator:
    """
    Validates synthetic datasets against structural, relational, and business rules.
    Isolates rejected records and produces comprehensive validation reports.
    """

    def __init__(self, datasets: Optional[Dict[str, pd.DataFrame]] = None) -> None:
        """Initializes validator with optional dictionary of DataFrames."""
        self.datasets: Dict[str, pd.DataFrame] = datasets or {}
        self.validation_results: List[Dict[str, Any]] = []
        self.rejected_records: Dict[str, pd.DataFrame] = {}

    def load_from_csv(self, data_dir: Path = DATA_RAW_DIR) -> Dict[str, pd.DataFrame]:
        """Loads all 6 required CSV files from the specified data directory."""
        tables = ["customers", "products", "orders", "order_items", "payments", "events"]
        loaded = {}
        for table in tables:
            path = data_dir / f"{table}.csv"
            if not path.exists():
                raise FileNotFoundError(f"Missing required dataset: {path}")
            logger.info(f"Loading {table} from {path}...")
            loaded[table] = pd.read_csv(path)
        self.datasets = loaded
        return loaded

    def _record_check(
        self,
        check_name: str,
        category: str,
        table: str,
        passed: bool,
        details: str,
        failed_count: int = 0
    ) -> None:
        """Appends a check result to the evaluation log."""
        result = {
            "check_name": check_name,
            "category": category,
            "table": table,
            "status": "PASSED" if passed else "FAILED",
            "failed_count": int(failed_count),
            "details": details
        }
        self.validation_results.append(result)
        if passed:
            logger.debug(f"[PASS] {check_name} on {table}")
        else:
            logger.error(f"[FAIL] {check_name} on {table}: {details} (Failures: {failed_count})")

    # -------------------------------------------------------------------------
    # 1. Primary Key Uniqueness & Nullability Checks
    # -------------------------------------------------------------------------
    def check_primary_keys(self) -> None:
        """Verifies primary key existence, non-nullability, and uniqueness."""
        pk_map = {
            "customers": "customer_id",
            "products": "product_id",
            "orders": "order_id",
            "order_items": "order_item_id",
            "payments": "payment_id",
            "events": "event_id"
        }

        for table, pk in pk_map.items():
            if table not in self.datasets:
                continue
            df = self.datasets[table]

            # Null check
            null_count = df[pk].isnull().sum()
            self._record_check(
                check_name=f"pk_not_null_{pk}",
                category="Primary Key",
                table=table,
                passed=(null_count == 0),
                details=f"Primary key {pk} has {null_count} nulls.",
                failed_count=null_count
            )

            # Duplicate check
            dup_count = df[pk].duplicated().sum()
            self._record_check(
                check_name=f"pk_unique_{pk}",
                category="Primary Key",
                table=table,
                passed=(dup_count == 0),
                details=f"Primary key {pk} has {dup_count} duplicate IDs.",
                failed_count=dup_count
            )

    # -------------------------------------------------------------------------
    # 2. Mandatory Fields Nullability Checks
    # -------------------------------------------------------------------------
    def check_mandatory_fields(self) -> None:
        """Ensures all mandatory business attributes are populated."""
        mandatory_map = {
            "customers": ["customer_id", "first_name", "last_name", "email", "gender", "age", "city", "state", "signup_date"],
            "products": ["product_id", "product_name", "category", "subcategory", "price", "cost", "stock_quantity"],
            "orders": ["order_id", "customer_id", "order_date", "order_status", "shipping_city", "shipping_state", "payment_method", "total_amount"],
            "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount", "subtotal"],
            "payments": ["payment_id", "order_id", "payment_method", "payment_status", "payment_amount", "payment_date"],
            "events": ["event_id", "event_type", "event_timestamp", "session_id"]
        }

        for table, cols in mandatory_map.items():
            if table not in self.datasets:
                continue
            df = self.datasets[table]
            for col in cols:
                null_count = df[col].isnull().sum()
                self._record_check(
                    check_name=f"not_null_{col}",
                    category="Nullability",
                    table=table,
                    passed=(null_count == 0),
                    details=f"Field {col} in {table} has {null_count} nulls.",
                    failed_count=null_count
                )

    # -------------------------------------------------------------------------
    # 3. Referential Integrity (Foreign Keys)
    # -------------------------------------------------------------------------
    def check_referential_integrity(self) -> None:
        """Validates relational links between entities."""
        fk_relationships = [
            ("orders", "customer_id", "customers", "customer_id"),
            ("order_items", "order_id", "orders", "order_id"),
            ("order_items", "product_id", "products", "product_id"),
            ("payments", "order_id", "orders", "order_id")
        ]

        for child_tbl, child_col, parent_tbl, parent_col in fk_relationships:
            if child_tbl not in self.datasets or parent_tbl not in self.datasets:
                continue

            child_df = self.datasets[child_tbl]
            parent_df = self.datasets[parent_tbl]

            parent_ids = set(parent_df[parent_col].dropna().unique())
            child_ids = child_df[child_col].dropna()

            orphans = child_ids[~child_ids.isin(parent_ids)]
            orphan_count = len(orphans)

            self._record_check(
                check_name=f"fk_{child_tbl}_{child_col}_in_{parent_tbl}",
                category="Referential Integrity",
                table=child_tbl,
                passed=(orphan_count == 0),
                details=f"{orphan_count} orphaned records in {child_tbl}.{child_col} referencing {parent_tbl}.{parent_col}.",
                failed_count=orphan_count
            )

        # Events table foreign keys (when populated)
        if "events" in self.datasets:
            events_df = self.datasets["events"]

            # Customer ID
            if "customers" in self.datasets:
                valid_cust_ids = set(self.datasets["customers"]["customer_id"].unique())
                ev_custs = events_df["customer_id"].dropna()
                invalid_cust_count = len(ev_custs[~ev_custs.isin(valid_cust_ids)])
                self._record_check(
                    check_name="fk_events_customer_id_in_customers",
                    category="Referential Integrity",
                    table="events",
                    passed=(invalid_cust_count == 0),
                    details=f"{invalid_cust_count} invalid customer_ids in events.",
                    failed_count=invalid_cust_count
                )

            # Product ID
            if "products" in self.datasets:
                valid_prod_ids = set(self.datasets["products"]["product_id"].unique())
                ev_prods = events_df["product_id"].dropna()
                invalid_prod_count = len(ev_prods[~ev_prods.isin(valid_prod_ids)])
                self._record_check(
                    check_name="fk_events_product_id_in_products",
                    category="Referential Integrity",
                    table="events",
                    passed=(invalid_prod_count == 0),
                    details=f"{invalid_prod_count} invalid product_ids in events.",
                    failed_count=invalid_prod_count
                )

    # -------------------------------------------------------------------------
    # 4. Numeric Range, Math, and Sanity Checks
    # -------------------------------------------------------------------------
    def check_numeric_ranges(self) -> None:
        """Validates numerical ranges and mathematical consistency."""
        # Products
        if "products" in self.datasets:
            pdf = self.datasets["products"]
            invalid_price = (pdf["price"] <= 0).sum()
            self._record_check(
                check_name="products_price_positive",
                category="Numeric Sanity",
                table="products",
                passed=(invalid_price == 0),
                details=f"{invalid_price} products have price <= 0.",
                failed_count=invalid_price
            )

            invalid_cost = (pdf["cost"] <= 0).sum()
            self._record_check(
                check_name="products_cost_positive",
                category="Numeric Sanity",
                table="products",
                passed=(invalid_cost == 0),
                details=f"{invalid_cost} products have cost <= 0.",
                failed_count=invalid_cost
            )

            cost_gt_price = (pdf["cost"] > pdf["price"]).sum()
            self._record_check(
                check_name="products_cost_leq_price",
                category="Numeric Sanity",
                table="products",
                passed=(cost_gt_price == 0),
                details=f"{cost_gt_price} products have manufacturing cost > price.",
                failed_count=cost_gt_price
            )

            invalid_stock = (pdf["stock_quantity"] < 0).sum()
            self._record_check(
                check_name="products_stock_non_negative",
                category="Numeric Sanity",
                table="products",
                passed=(invalid_stock == 0),
                details=f"{invalid_stock} products have negative stock quantity.",
                failed_count=invalid_stock
            )

            invalid_rating = ((pdf["product_rating"] < 1.0) | (pdf["product_rating"] > 5.0)).sum()
            self._record_check(
                check_name="products_rating_valid_range",
                category="Numeric Sanity",
                table="products",
                passed=(invalid_rating == 0),
                details=f"{invalid_rating} products have ratings outside [1.0, 5.0].",
                failed_count=invalid_rating
            )

        # Order Items
        if "order_items" in self.datasets:
            idf = self.datasets["order_items"]
            invalid_qty = (idf["quantity"] < 1).sum()
            self._record_check(
                check_name="order_items_quantity_gte_1",
                category="Numeric Sanity",
                table="order_items",
                passed=(invalid_qty == 0),
                details=f"{invalid_qty} items have quantity < 1.",
                failed_count=invalid_qty
            )

            invalid_unit_price = (idf["unit_price"] <= 0).sum()
            self._record_check(
                check_name="order_items_unit_price_positive",
                category="Numeric Sanity",
                table="order_items",
                passed=(invalid_unit_price == 0),
                details=f"{invalid_unit_price} items have non-positive unit_price.",
                failed_count=invalid_unit_price
            )

            # Subtotal consistency: subtotal == round(quantity * unit_price - discount, 2)
            expected_subtotals = (idf["quantity"] * idf["unit_price"] - idf["discount"]).round(2)
            mismatch_subtotals = (abs(idf["subtotal"] - expected_subtotals) > 0.01).sum()
            self._record_check(
                check_name="order_items_subtotal_consistency",
                category="Mathematical Consistency",
                table="order_items",
                passed=(mismatch_subtotals == 0),
                details=f"{mismatch_subtotals} items have subtotal mismatching qty * price - discount.",
                failed_count=mismatch_subtotals
            )

        # Orders
        if "orders" in self.datasets and "order_items" in self.datasets:
            odf = self.datasets["orders"]
            idf = self.datasets["order_items"]

            invalid_order_amount = (odf["total_amount"] < 0).sum()
            self._record_check(
                check_name="orders_total_amount_non_negative",
                category="Numeric Sanity",
                table="orders",
                passed=(invalid_order_amount == 0),
                details=f"{invalid_order_amount} orders have negative total_amount.",
                failed_count=invalid_order_amount
            )

            # Sum of order items equals order total
            item_sums = idf.groupby("order_id")["subtotal"].sum().round(2).rename("calculated_total")
            merged_orders = odf.merge(item_sums, on="order_id", how="left")
            total_mismatches = (abs(merged_orders["total_amount"] - merged_orders["calculated_total"]) > 0.01).sum()
            self._record_check(
                check_name="orders_total_matches_items_subtotal",
                category="Mathematical Consistency",
                table="orders",
                passed=(total_mismatches == 0),
                details=f"{total_mismatches} orders have total_amount mismatching sum of line items.",
                failed_count=total_mismatches
            )

        # Payments
        if "payments" in self.datasets and "orders" in self.datasets:
            pay_df = self.datasets["payments"]
            ord_df = self.datasets["orders"]

            invalid_pay_amount = (pay_df["payment_amount"] < 0).sum()
            self._record_check(
                check_name="payments_amount_non_negative",
                category="Numeric Sanity",
                table="payments",
                passed=(invalid_pay_amount == 0),
                details=f"{invalid_pay_amount} payments have negative amount.",
                failed_count=invalid_pay_amount
            )

            merged_pay = pay_df.merge(ord_df[["order_id", "total_amount"]], on="order_id")
            pay_mismatches = (abs(merged_pay["payment_amount"] - merged_pay["total_amount"]) > 0.01).sum()
            self._record_check(
                check_name="payments_amount_matches_order_total",
                category="Mathematical Consistency",
                table="payments",
                passed=(pay_mismatches == 0),
                details=f"{pay_mismatches} payments have amount mismatching order total.",
                failed_count=pay_mismatches
            )

    # -------------------------------------------------------------------------
    # 5. Chronological Validity Checks
    # -------------------------------------------------------------------------
    def check_chronological_validity(self) -> None:
        """Validates date causality (signup before order, order before payment)."""
        # Order date >= Customer signup date
        if "orders" in self.datasets and "customers" in self.datasets:
            ord_df = self.datasets["orders"].copy()
            cust_df = self.datasets["customers"].copy()

            ord_df["order_dt"] = pd.to_datetime(ord_df["order_date"])
            cust_df["signup_dt"] = pd.to_datetime(cust_df["signup_date"])

            merged = ord_df.merge(cust_df[["customer_id", "signup_dt"]], on="customer_id")
            invalid_orders = (merged["order_dt"] < merged["signup_dt"]).sum()
            self._record_check(
                check_name="order_date_after_customer_signup_date",
                category="Chronological Logic",
                table="orders",
                passed=(invalid_orders == 0),
                details=f"{invalid_orders} orders placed before customer signup_date.",
                failed_count=invalid_orders
            )

        # Payment date >= Order date
        if "payments" in self.datasets and "orders" in self.datasets:
            pay_df = self.datasets["payments"].copy()
            ord_df = self.datasets["orders"].copy()

            pay_df["pay_dt"] = pd.to_datetime(pay_df["payment_date"])
            ord_df["order_dt"] = pd.to_datetime(ord_df["order_date"])

            merged = pay_df.merge(ord_df[["order_id", "order_dt"]], on="order_id")
            invalid_pays = (merged["pay_dt"] < merged["order_dt"]).sum()
            self._record_check(
                check_name="payment_date_gte_order_date",
                category="Chronological Logic",
                table="payments",
                passed=(invalid_pays == 0),
                details=f"{invalid_pays} payments occurred before order_date.",
                failed_count=invalid_pays
            )

    # -------------------------------------------------------------------------
    # 6. Business Logic & Status Consistency
    # -------------------------------------------------------------------------
    def check_business_logic(self) -> None:
        """Ensures statuses match business reality."""
        if "orders" in self.datasets and "payments" in self.datasets:
            merged = self.datasets["orders"].merge(
                self.datasets["payments"][["order_id", "payment_status"]],
                on="order_id"
            )

            # Fulfilled orders should not have failed payments
            invalid_fulfilled = (
                merged["order_status"].isin(["completed", "shipped"]) &
                (merged["payment_status"] == "failed")
            ).sum()
            self._record_check(
                check_name="fulfilled_orders_payment_not_failed",
                category="Business Logic",
                table="orders_payments",
                passed=(invalid_fulfilled == 0),
                details=f"{invalid_fulfilled} completed/shipped orders have failed payment status.",
                failed_count=invalid_fulfilled
            )

            # Cancelled orders should have refunded or failed payment status
            invalid_cancelled = (
                (merged["order_status"] == "cancelled") &
                (~merged["payment_status"].isin(["refunded", "failed"]))
            ).sum()
            self._record_check(
                check_name="cancelled_orders_refunded_or_failed",
                category="Business Logic",
                table="orders_payments",
                passed=(invalid_cancelled == 0),
                details=f"{invalid_cancelled} cancelled orders have non-refunded/non-failed payments.",
                failed_count=invalid_cancelled
            )

    # -------------------------------------------------------------------------
    # Isolation of Rejected Records
    # -------------------------------------------------------------------------
    def isolate_rejected_records(self, output_dir: Path = DATA_REJECTED_DIR) -> Dict[str, int]:
        """
        Scans datasets for any records violating basic integrity constraints
        and saves them separately to data/rejected/ for auditing.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        rejected_counts = {}

        for table, df in self.datasets.items():
            rejected_mask = pd.Series(False, index=df.index)

            # Flag nulls in mandatory fields
            if table == "orders":
                rejected_mask |= df["total_amount"] < 0
                rejected_mask |= df["customer_id"].isnull()
            elif table == "products":
                rejected_mask |= df["price"] <= 0
                rejected_mask |= df["cost"] > df["price"]
            elif table == "order_items":
                rejected_mask |= df["quantity"] < 1
                rejected_mask |= df["unit_price"] <= 0
            elif table == "payments":
                rejected_mask |= df["payment_amount"] < 0

            rejected_df = df[rejected_mask]
            count = len(rejected_df)
            rejected_counts[table] = count

            if count > 0:
                rejected_file = output_dir / f"rejected_{table}.csv"
                rejected_df.to_csv(rejected_file, index=False)
                logger.warning(f"Saved {count} rejected {table} records to {rejected_file}")

        return rejected_counts

    # -------------------------------------------------------------------------
    # Comprehensive Validation Runner & Report Serialization
    # -------------------------------------------------------------------------
    def run_all_validations(self) -> Dict[str, Any]:
        """Runs the entire validation test suite."""
        self.validation_results = []
        logger.info("=== Starting Data Quality Validation Suite ===")

        self.check_primary_keys()
        self.check_mandatory_fields()
        self.check_referential_integrity()
        self.check_numeric_ranges()
        self.check_chronological_validity()
        self.check_business_logic()

        total = len(self.validation_results)
        passed = sum(1 for c in self.validation_results if c["status"] == "PASSED")
        failed = total - passed

        summary_by_cat: Dict[str, Dict[str, int]] = {}
        for c in self.validation_results:
            cat = c["category"]
            if cat not in summary_by_cat:
                summary_by_cat[cat] = {"passed": 0, "failed": 0}
            if c["status"] == "PASSED":
                summary_by_cat[cat]["passed"] += 1
            else:
                summary_by_cat[cat]["failed"] += 1

        metrics = {
            tbl: {
                "row_count": len(df),
                "column_count": len(df.columns),
                "null_count": int(df.isnull().sum().sum())
            }
            for tbl, df in self.datasets.items()
        }

        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": "PASSED" if failed == 0 else "FAILED",
            "summary": {
                "total_checks": total,
                "passed_checks": passed,
                "failed_checks": failed,
                "pass_rate_pct": round((passed / total) * 100, 2) if total else 0.0
            },
            "by_category": summary_by_cat,
            "dataset_metrics": metrics,
            "detailed_results": self.validation_results
        }

        logger.info(
            f"Validation Completed: {passed}/{total} passed "
            f"({report['summary']['pass_rate_pct']}%). Status: {report['overall_status']}"
        )
        return report

    def save_report(
        self,
        report: Dict[str, Any],
        output_file: Optional[Path] = None
    ) -> Path:
        """Saves the validation report as a JSON file."""
        target_path = output_file or (REPORTS_DIR / "validation_report.json")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved validation report to: {target_path}")
        return target_path

    def print_summary(self, report: Dict[str, Any]) -> str:
        """Formats and prints an ASCII summary table."""
        lines = [
            "=" * 78,
            f"      DATA QUALITY & VALIDATION REPORT ({report['timestamp']})",
            "=" * 78,
            f"  OVERALL STATUS: {report['overall_status']}",
            f"  Pass Rate:      {report['summary']['pass_rate_pct']}% "
            f"({report['summary']['passed_checks']}/{report['summary']['total_checks']} checks)",
            "-" * 78,
            "  DATASET RECORD METRICS:",
        ]

        for table, m in report["dataset_metrics"].items():
            lines.append(
                f"    - {table:<15}: {m['row_count']:>7,} rows | "
                f"{m['column_count']:>2} cols | {m['null_count']:>4} nulls"
            )

        lines.extend([
            "-" * 78,
            "  RESULTS BY CATEGORY:",
        ])

        for cat, counts in report["by_category"].items():
            tag = "[OK]" if counts["failed"] == 0 else "[FAIL]"
            lines.append(
                f"    {tag:<6} {cat:<28}: {counts['passed']:>2} Passed | {counts['failed']:>2} Failed"
            )

        if report["summary"]["failed_checks"] > 0:
            lines.extend([
                "-" * 78,
                "  FAILED CHECKS DETAILS:",
            ])
            for check in report["detailed_results"]:
                if check["status"] == "FAILED":
                    lines.append(f"    * [{check['table']}] {check['check_name']}: {check['details']}")

        lines.append("=" * 78)
        summary_text = "\n".join(lines)
        print(summary_text)
        return summary_text
