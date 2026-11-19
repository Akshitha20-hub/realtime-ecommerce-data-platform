"""
Centralized logging module for the Real-Time E-Commerce Data Platform.
Provides standardized formatting, console streaming, and persistent log file rotation.
"""

import logging
from pathlib import Path
import sys
from typing import Optional

# Base log directory
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(
    name: str = "EcommercePlatform",
    log_file: Optional[str] = "pipeline.log",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Creates or retrieves a logger configured with consistent formatters
    for both stdout and persistent log files.

    Args:
        name: Hierarchy name for the logger.
        log_file: Filename located under logs/ directory. If None, file logging is omitted.
        level: Minimum log level (e.g. logging.DEBUG, logging.INFO).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers on multiple calls
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Stream Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler
        if log_file:
            log_path = LOGS_DIR / log_file
            file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
