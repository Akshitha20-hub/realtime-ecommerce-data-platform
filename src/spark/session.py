"""
Apache Spark Configuration & Session Manager
============================================
Initializes a PySpark session when Java / Spark runtime is available,
or provides a lightweight emulation layer on environments without Java.
"""

import os
import sys
from typing import Optional, Any


def get_spark_session(app_name: str = "EcommerceSparkEngine") -> Optional[Any]:
    """
    Initializes and returns a PySpark SparkSession if PySpark and Java are available.
    Returns None if Java is not installed, triggering graceful fallback.
    """
    try:
        from pyspark.sql import SparkSession
        spark = (
            SparkSession.builder
            .appName(app_name)
            .master("local[*]")
            .config("spark.driver.memory", "2g")
            .config("spark.sql.shuffle.partitions", "4")
            .getOrCreate()
        )
        return spark
    except Exception as exc:
        return None
