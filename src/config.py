"""
Configuration module for the Real-Time E-Commerce Data Engineering Platform.
Defines project paths, simulation parameters, categorical pools, distributions,
and schemas for all core entities.
"""

from pathlib import Path
from typing import Dict, List, Tuple

# -----------------------------------------------------------------------------
# Base Directories
# -----------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
DATA_RAW_DIR: Path = DATA_DIR / "raw"
DATA_PROCESSED_DIR: Path = DATA_DIR / "processed"
DATA_REJECTED_DIR: Path = DATA_DIR / "rejected"
LOGS_DIR: Path = BASE_DIR / "logs"
REPORTS_DIR: Path = DATA_RAW_DIR / "reports"

# Ensure essential directories exist
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_REJECTED_DIR, LOGS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Random Generation & Simulation Parameters
# -----------------------------------------------------------------------------
RANDOM_SEED: int = 42

# Target record counts (Exceeds project minimums: 1000 cust, 100 prod, 10000 orders, 20000 items, 10000 events)
NUM_CUSTOMERS: int = 1500
NUM_PRODUCTS: int = 200
NUM_ORDERS: int = 10500
NUM_EVENTS: int = 28000

# Simulation Date Range (1 full year)
SIMULATION_START_DATE: str = "2025-01-01 00:00:00"
SIMULATION_END_DATE: str = "2025-12-31 23:59:59"

# -----------------------------------------------------------------------------
# Product Catalog Metadata
# -----------------------------------------------------------------------------
PRODUCT_CATEGORIES: Dict[str, Dict[str, object]] = {
    "Electronics": {
        "price_range": (39.99, 1499.99),
        "cost_ratio_range": (0.60, 0.78),
        "subcategories": [
            "Smartphones", "Laptops", "Wireless Earbuds", "Smartwatches",
            "Gaming Monitors", "Bluetooth Speakers", "Mechanical Keyboards"
        ]
    },
    "Apparel": {
        "price_range": (14.99, 189.99),
        "cost_ratio_range": (0.30, 0.50),
        "subcategories": [
            "Denim Jackets", "Cotton T-Shirts", "Athletic Joggers",
            "Running Shoes", "Hoodies", "Summer Dresses", "Accessories"
        ]
    },
    "Home & Kitchen": {
        "price_range": (19.99, 399.99),
        "cost_ratio_range": (0.40, 0.60),
        "subcategories": [
            "Stainless Steel Cookware", "Espresso Machines", "Air Fryers",
            "Blenders", "Memory Foam Pillows", "Vacuum Cleaners"
        ]
    },
    "Beauty & Personal Care": {
        "price_range": (9.99, 129.99),
        "cost_ratio_range": (0.25, 0.45),
        "subcategories": [
            "Hydrating Serums", "Organic Moisturizers", "Hair Styling Sets",
            "Sunscreen SPF 50", "Fragrances", "Facial Cleansers"
        ]
    },
    "Sports & Outdoors": {
        "price_range": (24.99, 499.99),
        "cost_ratio_range": (0.45, 0.65),
        "subcategories": [
            "Yoga Mats", "Camping Tents", "Fitness Dumbbells",
            "Hiking Backpacks", "Cycling Helmets", "Hydration Packs"
        ]
    },
    "Books": {
        "price_range": (7.99, 49.99),
        "cost_ratio_range": (0.35, 0.55),
        "subcategories": [
            "Data Engineering", "Machine Learning", "System Design",
            "Business Strategy", "Science Fiction", "Biographies"
        ]
    }
}

# -----------------------------------------------------------------------------
# Categorical Distributions & Weights
# -----------------------------------------------------------------------------
CUSTOMER_SEGMENTS: List[Tuple[str, float]] = [
    ("Consumer", 0.65),
    ("Corporate", 0.15),
    ("Small Business", 0.15),
    ("VIP", 0.05)
]

ORDER_STATUSES: List[Tuple[str, float]] = [
    ("completed", 0.72),
    ("shipped", 0.12),
    ("processing", 0.05),
    ("cancelled", 0.06),
    ("returned", 0.05)
]

PAYMENT_METHODS: List[Tuple[str, float]] = [
    ("credit_card", 0.45),
    ("paypal", 0.22),
    ("apple_pay", 0.15),
    ("debit_card", 0.10),
    ("buy_now_pay_later", 0.08)
]

EVENT_TYPES: List[str] = [
    "product_view",
    "add_to_cart",
    "checkout",
    "purchase",
    "product_search"
]

# Seasonal Demand Pattern (Monthly weights normalized for 2025)
MONTHLY_SEASONALITY_WEIGHTS: Dict[int, float] = {
    1: 0.85,   # Jan: Post-holiday dip
    2: 0.80,   # Feb
    3: 0.95,   # Mar: Spring refresh
    4: 0.92,   # Apr
    5: 1.00,   # May
    6: 1.05,   # Jun
    7: 1.25,   # Jul: Summer Mid-Year Sale
    8: 1.05,   # Aug: Back to school
    9: 1.00,   # Sep
    10: 1.15,  # Oct: Early holiday ramp
    11: 1.70,  # Nov: Black Friday / Cyber Monday surge
    12: 1.85   # Dec: Holiday gifting peak
}

# Time of day shopping weights (24-hour diurnal curve)
HOURLY_WEIGHTS: List[float] = [
    0.015, 0.010, 0.008, 0.006, 0.005, 0.008,  # 00:00 - 05:00 (overnight lull)
    0.018, 0.035, 0.055, 0.070, 0.080, 0.085,  # 06:00 - 11:00 (morning rise)
    0.090, 0.085, 0.075, 0.068, 0.065, 0.072,  # 12:00 - 17:00 (afternoon steady)
    0.085, 0.095, 0.090, 0.075, 0.050, 0.028   # 18:00 - 23:00 (evening peak)
]

# Geographic Pool (US locations)
US_LOCATIONS: List[Dict[str, str]] = [
    {"city": "New York", "state": "NY"},
    {"city": "Los Angeles", "state": "CA"},
    {"city": "Chicago", "state": "IL"},
    {"city": "Houston", "state": "TX"},
    {"city": "Phoenix", "state": "AZ"},
    {"city": "Philadelphia", "state": "PA"},
    {"city": "San Antonio", "state": "TX"},
    {"city": "San Diego", "state": "CA"},
    {"city": "Dallas", "state": "TX"},
    {"city": "San Jose", "state": "CA"},
    {"city": "Austin", "state": "TX"},
    {"city": "Seattle", "state": "WA"},
    {"city": "Denver", "state": "CO"},
    {"city": "Boston", "state": "MA"},
    {"city": "Atlanta", "state": "GA"},
    {"city": "Miami", "state": "FL"},
    {"city": "Portland", "state": "OR"},
    {"city": "Minneapolis", "state": "MN"},
    {"city": "Charlotte", "state": "NC"},
    {"city": "Salt Lake City", "state": "UT"}
]
