"""
Real-Time Event Consumer
========================
Consumes live e-commerce clickstream events, performs micro-batching, validates
event schemas in flight, and writes processed records directly into the PostgreSQL
warehouse.

Also calculates real-time rolling metrics (event counts, top events, throughput).
"""

import json
import time
import pathlib
from collections import Counter
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import text

from src.streaming.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    TOPIC_EVENTS,
    DEFAULT_BATCH_SIZE,
)
from src.database.connection import get_engine
from src.database.loader import load_table


class EventConsumer:
    """Consumes, validates, and ingests live event streams."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
        self.kafka_consumer = None
        self.is_connected = False
        self.processed_count = 0
        self.event_type_counts = Counter()
        self.buffer: List[Dict[str, Any]] = []
        self._init_kafka()

    def _init_kafka(self) -> None:
        """Attempt connection to real Kafka consumer."""
        try:
            from kafka import KafkaConsumer
            self.kafka_consumer = KafkaConsumer(
                TOPIC_EVENTS,
                bootstrap_servers=self.bootstrap_servers,
                group_id=KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                consumer_timeout_ms=5000,
            )
            self.is_connected = True
            print(f"✅ Connected Kafka consumer to topic '{TOPIC_EVENTS}'")
        except Exception:
            self.kafka_consumer = None
            self.is_connected = False
            print("ℹ️ Kafka broker not reachable. Consumer ready for local streaming batches.")

    def validate_event(self, event: Dict[str, Any]) -> bool:
        """Validate live event schema and integrity."""
        required = ["event_id", "event_type", "event_timestamp"]
        for field in required:
            if not event.get(field):
                return False
        return True

    def process_event(self, event: Dict[str, Any]) -> None:
        """Process a single incoming event record."""
        if not self.validate_event(event):
            return

        self.buffer.append(event)
        self.processed_count += 1
        self.event_type_counts[event["event_type"]] += 1

    def flush_to_warehouse(self) -> int:
        """Flush the in-memory micro-batch to PostgreSQL."""
        if not self.buffer:
            return 0

        batch_df = pd.DataFrame(self.buffer)
        count = len(batch_df)

        try:
            engine = get_engine()
            load_table(engine, "events", batch_df)
            print(f"💾 Flushed micro-batch of {count} events to PostgreSQL warehouse.")
        except Exception as exc:
            # Fallback to local append log
            out_dir = pathlib.Path(__file__).resolve().parents[2] / "data" / "processed"
            out_dir.mkdir(parents=True, exist_ok=True)
            log_path = out_dir / "streamed_events.jsonl"
            with open(log_path, "a", encoding="utf-8") as f:
                for ev in self.buffer:
                    f.write(json.dumps(ev) + "\n")
            print(f"⚠️ PostgreSQL not reachable ({exc}). Appended {count} events to {log_path.name}")

        self.buffer.clear()
        return count

    def get_metrics(self) -> Dict[str, Any]:
        """Return real-time stream aggregation metrics."""
        return {
            "total_processed": self.processed_count,
            "buffer_size": len(self.buffer),
            "distribution": dict(self.event_type_counts),
        }
