"""
Real-Time Event Streaming Simulator
===================================
Simulates an end-to-end event stream from user clickstream to warehouse ingestion.

Usage:
    python scripts/simulate_stream.py --events 50 --rate 10
"""

import argparse
import time
import sys
import pathlib

# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.streaming.producer import EventProducer
from src.streaming.consumer import EventConsumer


def run_simulation(num_events: int = 50, rate_per_sec: float = 10.0, batch_size: int = 20) -> None:
    delay = 1.0 / rate_per_sec if rate_per_sec > 0 else 0.1
    producer = EventProducer()
    consumer = EventConsumer()

    print("=" * 65)
    print("      REAL-TIME E-COMMERCE STREAMING PIPELINE SIMULATOR")
    print("=" * 65)
    print(f"Target Events: {num_events} | Ingestion Rate: {rate_per_sec} ev/s | Micro-batch: {batch_size}")
    print("-" * 65)

    start_time = time.time()
    for idx, event in enumerate(producer.stream_continuous(max_events=num_events, delay_sec=delay), 1):
        consumer.process_event(event)
        print(f"[{idx:>3}/{num_events}] {event['event_timestamp']} | {event['event_type']:<14} | User: {str(event['customer_id']):<12} | Prod: {event['product_id']}")

        if len(consumer.buffer) >= batch_size:
            consumer.flush_to_warehouse()

    # Flush any remaining buffer
    consumer.flush_to_warehouse()
    elapsed = max(time.time() - start_time, 0.01)

    print("-" * 65)
    print("🎯 STREAMING INGESTION SUMMARY:")
    metrics = consumer.get_metrics()
    print(f"  • Total Events Ingested: {metrics['total_processed']:,}")
    print(f"  • Elapsed Time:          {elapsed:.2f} seconds")
    print(f"  • Average Throughput:    {metrics['total_processed'] / elapsed:.1f} events/sec")
    print("  • Event Distribution:")
    for ev_type, count in metrics["distribution"].items():
        pct = (count / metrics['total_processed']) * 100
        print(f"    - {ev_type:<16}: {count:>4} ({pct:>5.1f}%)")
    print("=" * 65)
    print("✅ Streaming pipeline simulation finished successfully.")


def main():
    parser = argparse.ArgumentParser(description="Simulate real-time e-commerce streaming events.")
    parser.add_argument("--events", type=int, default=50, help="Total number of events to stream (default: 50)")
    parser.add_argument("--rate", type=float, default=15.0, help="Events per second (default: 15.0)")
    parser.add_argument("--batch", type=int, default=25, help="Micro-batch size for warehouse flush (default: 25)")
    args = parser.parse_args()

    run_simulation(num_events=args.events, rate_per_sec=args.rate, batch_size=args.batch)


if __name__ == "__main__":
    main()
