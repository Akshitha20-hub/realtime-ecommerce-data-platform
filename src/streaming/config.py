"""
Streaming Configuration
=======================
Defines Kafka broker parameters, topics, and buffer configurations.
"""

import os
from typing import Dict, Any

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "ecommerce-producer")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "ecommerce-analytics-group")

# Kafka Topics
TOPIC_EVENTS = os.getenv("KAFKA_TOPIC_EVENTS", "ecommerce.clickstream.events")
TOPIC_ORDERS = os.getenv("KAFKA_TOPIC_ORDERS", "ecommerce.orders.stream")
TOPIC_PAYMENTS = os.getenv("KAFKA_TOPIC_PAYMENTS", "ecommerce.payments.stream")

ALL_TOPICS = [TOPIC_EVENTS, TOPIC_ORDERS, TOPIC_PAYMENTS]

# Simulation settings
DEFAULT_BATCH_SIZE = 100
DEFAULT_EVENT_DELAY_SEC = 0.05  # 20 events per second simulation rate
