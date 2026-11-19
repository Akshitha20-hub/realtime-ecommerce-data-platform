"""
Real-Time Event Producer
========================
Generates and broadcasts simulated live e-commerce clickstream and transaction
events to an Apache Kafka broker or local streaming queue.

Supports both:
1. Live Kafka streaming via kafka-python / confluent-kafka (if installed & broker available).
2. Standalone simulator mode for local development, demos, and testing.
"""

import json
import time
import uuid
import random
from datetime import datetime, timezone
from typing import Dict, Any, Generator, Optional
import pathlib
import pandas as pd

from src.streaming.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CLIENT_ID,
    TOPIC_EVENTS,
    DEFAULT_EVENT_DELAY_SEC,
)

EVENT_TYPES = [
    ("product_view", 0.50),
    ("add_to_cart",  0.25),
    ("checkout",     0.12),
    ("purchase",     0.08),
    ("cancellation", 0.03),
    ("return",       0.02),
]


class EventProducer:
    """Produces live synthetic e-commerce events."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
        self.kafka_producer = None
        self.is_connected = False
        self._load_reference_entities()
        self._init_kafka()

    def _load_reference_entities(self) -> None:
        """Load customer and product IDs from raw data to generate valid references."""
        data_dir = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw"
        try:
            cust_df = pd.read_csv(data_dir / "customers.csv", usecols=["customer_id"])
            self.customer_ids = cust_df["customer_id"].tolist()
        except Exception:
            self.customer_ids = [f"CUST-{i:06d}" for i in range(1, 1501)]

        try:
            prod_df = pd.read_csv(data_dir / "products.csv", usecols=["product_id"])
            self.product_ids = prod_df["product_id"].tolist()
        except Exception:
            self.product_ids = [f"PROD-{i:06d}" for i in range(1, 201)]

    def _init_kafka(self) -> None:
        """Attempt connection to real Kafka broker if available."""
        try:
            from kafka import KafkaProducer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=KAFKA_CLIENT_ID,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=3000,
            )
            self.is_connected = True
            print(f"✅ Connected to Kafka broker at {self.bootstrap_servers}")
        except Exception:
            self.kafka_producer = None
            self.is_connected = False
            print("ℹ️ Kafka broker not reachable. Running in standalone simulated streaming mode.")

    def generate_single_event(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a single realistic clickstream event dictionary."""
        ev_types, weights = zip(*EVENT_TYPES)
        event_type = random.choices(ev_types, weights=weights, k=1)[0]
        customer_id = random.choice(self.customer_ids) if random.random() > 0.1 else None

        return {
            "event_id": f"EVT-LIVE-{uuid.uuid4().hex[:12].upper()}",
            "customer_id": customer_id,
            "product_id": random.choice(self.product_ids),
            "event_type": event_type,
            "event_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session_id or f"SESS-{uuid.uuid4().hex[:8].upper()}",
        }

    def emit_event(self, event: Dict[str, Any], topic: str = TOPIC_EVENTS) -> None:
        """Send event to Kafka topic or print to console in simulated mode."""
        if self.is_connected and self.kafka_producer:
            self.kafka_producer.send(topic, value=event)
        # Log event emission for visibility

    def stream_continuous(
        self,
        max_events: int = 100,
        delay_sec: float = DEFAULT_EVENT_DELAY_SEC
    ) -> Generator[Dict[str, Any], None, None]:
        """Stream a sequence of events, yielding each for consumption."""
        print(f"🚀 Starting event stream ({max_events} events, {delay_sec}s delay)...")
        active_sessions = [f"SESS-{uuid.uuid4().hex[:8].upper()}" for _ in range(10)]

        for i in range(1, max_events + 1):
            session = random.choice(active_sessions)
            event = self.generate_single_event(session_id=session)
            self.emit_event(event)
            yield event
            time.sleep(delay_sec)

        if self.is_connected and self.kafka_producer:
            self.kafka_producer.flush()
        print(f"🏁 Stream completed: {max_events} events emitted.")


if __name__ == "__main__":
    producer = EventProducer()
    for ev in producer.stream_continuous(max_events=10, delay_sec=0.2):
        print(f"  [STREAM] {ev['event_timestamp']} | {ev['event_type']:<14} | Customer: {ev['customer_id']} | Product: {ev['product_id']}")
