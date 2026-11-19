"""
Execution script to generate synthetic e-commerce datasets and run quality validation.

Usage:
    python scripts/generate_data.py
    python scripts/generate_data.py --orders 12000 --seed 42
"""

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import (
    DATA_RAW_DIR,
    DATA_REJECTED_DIR,
    NUM_CUSTOMERS,
    NUM_EVENTS,
    NUM_ORDERS,
    NUM_PRODUCTS,
    RANDOM_SEED,
    REPORTS_DIR
)
from src.data_generator import EcommerceDataGenerator
from src.logger import get_logger
from src.validation import DataValidator

logger = get_logger("EcommercePlatform.GenerateScript", "data_generation.log")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate realistic synthetic e-commerce datasets with validation."
    )
    parser.add_argument(
        "--orders",
        type=int,
        default=NUM_ORDERS,
        help=f"Number of orders to generate (minimum 10,000 required, default: {NUM_ORDERS})"
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=NUM_CUSTOMERS,
        help=f"Number of customers to generate (default: {NUM_CUSTOMERS})"
    )
    parser.add_argument(
        "--products",
        type=int,
        default=NUM_PRODUCTS,
        help=f"Number of products to generate (default: {NUM_PRODUCTS})"
    )
    parser.add_argument(
        "--events",
        type=int,
        default=NUM_EVENTS,
        help=f"Number of clickstream events to generate (default: {NUM_EVENTS})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help=f"Reproducibility random seed (default: {RANDOM_SEED})"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DATA_RAW_DIR),
        help=f"Destination directory for raw CSVs (default: {DATA_RAW_DIR})"
    )

    args = parser.parse_args()

    # Enforce minimum order requirement
    if args.orders < 10000:
        print(f"Error: Minimum required order count is 10,000. Specified: {args.orders}")
        return 1

    logger.info("=" * 70)
    logger.info("PHASE 1: SYNTHETIC DATA GENERATION & VALIDATION PIPELINE")
    logger.info(f"Target Parameters: Seed={args.seed}, Orders={args.orders:,}, "
                f"Customers={args.customers:,}, Products={args.products:,}, Events={args.events:,}")
    logger.info("=" * 70)

    output_dir = Path(args.output_dir)

    try:
        # Step 1: Initialize Generator
        generator = EcommerceDataGenerator(seed=args.seed)

        # Step 2: Generate Datasets
        datasets = generator.generate_all(
            num_customers=args.customers,
            num_products=args.products,
            num_orders=args.orders,
            num_events=args.events
        )

        # Step 3: Persist to CSV in data/raw/
        logger.info(f"Saving datasets to CSV files in: {output_dir}")
        generator.save_to_csv(datasets=datasets, output_dir=output_dir)

        # Step 4: Validate Data Quality & Referential Integrity
        logger.info("Triggering comprehensive data validation checks...")
        validator = DataValidator(datasets=datasets)
        report = validator.run_all_validations()

        # Step 5: Isolate Rejected Records (if any)
        rejected_counts = validator.isolate_rejected_records(output_dir=DATA_REJECTED_DIR)
        total_rejected = sum(rejected_counts.values())

        # Step 6: Save Validation Report
        report_path = validator.save_report(report=report, output_file=REPORTS_DIR / "validation_report.json")
        logger.info(f"Detailed validation report written to {report_path}")

        # Step 7: Print Console Summary
        validator.print_summary(report)

        if report["overall_status"] == "PASSED" and total_rejected == 0:
            logger.info("Phase 1 data generation and validation finished successfully with 0 errors!")
            return 0
        else:
            logger.error("Phase 1 completed with validation errors. Review logs/validation.log.")
            return 1

    except Exception as exc:
        logger.exception(f"Unhandled error during data generation pipeline: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
