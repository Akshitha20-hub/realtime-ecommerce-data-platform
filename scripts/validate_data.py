"""
Standalone Data Validation Script.
Loads generated CSV datasets from data/raw/, executes the quality test suite,
isolates any rejected records, and generates a validation report.

Usage:
    python scripts/validate_data.py
    python scripts/validate_data.py --data-dir data/raw --report-dir data/raw/reports
"""

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import DATA_RAW_DIR, DATA_REJECTED_DIR, REPORTS_DIR
from src.logger import get_logger
from src.validation import DataValidator

logger = get_logger("EcommercePlatform.ValidateScript", "validation.log")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate e-commerce CSV datasets.")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(DATA_RAW_DIR),
        help=f"Path to raw data directory (default: {DATA_RAW_DIR})"
    )
    parser.add_argument(
        "--report-dir",
        type=str,
        default=str(REPORTS_DIR),
        help=f"Path to output validation report directory (default: {REPORTS_DIR})"
    )
    parser.add_argument(
        "--rejected-dir",
        type=str,
        default=str(DATA_REJECTED_DIR),
        help=f"Path to output rejected records directory (default: {DATA_REJECTED_DIR})"
    )

    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    report_dir = Path(args.report_dir)
    rejected_dir = Path(args.rejected_dir)

    logger.info("=" * 65)
    logger.info("Executing E-Commerce Dataset Quality Validation")
    logger.info(f"Target Directory: {data_dir}")
    logger.info("=" * 65)

    try:
        validator = DataValidator()
        validator.load_from_csv(data_dir=data_dir)

        # Run validations
        report = validator.run_all_validations()

        # Isolate rejected records if any
        rejected_counts = validator.isolate_rejected_records(output_dir=rejected_dir)
        total_rejected = sum(rejected_counts.values())

        # Save JSON report
        report_file = report_dir / "validation_report.json"
        validator.save_report(report=report, output_file=report_file)

        # Print human-readable summary
        validator.print_summary(report)

        if report["overall_status"] == "PASSED" and total_rejected == 0:
            logger.info("Validation PASSED with zero defects. Data is production-ready!")
            return 0
        else:
            logger.error(f"Validation FAILED or found {total_rejected} rejected records.")
            return 1

    except Exception as exc:
        logger.exception(f"Fatal error during validation: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
