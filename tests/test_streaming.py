"""
Unit Tests for Streaming Producer and Consumer
==============================================
"""

import unittest
from src.streaming.producer import EventProducer
from src.streaming.consumer import EventConsumer


class TestStreamingPipeline(unittest.TestCase):
    """Test producer event schema and consumer micro-batch processing."""

    def setUp(self):
        self.producer = EventProducer()
        self.consumer = EventConsumer()

    def test_producer_event_structure(self):
        ev = self.producer.generate_single_event(session_id="SESS-TEST1")
        self.assertTrue(ev["event_id"].startswith("EVT-LIVE-"))
        self.assertEqual(ev["session_id"], "SESS-TEST1")
        self.assertIn("event_type", ev)
        self.assertIn("event_timestamp", ev)
        self.assertIn("product_id", ev)

    def test_consumer_validation_valid(self):
        ev = {
            "event_id": "EVT-1",
            "event_type": "product_view",
            "event_timestamp": "2026-11-18 12:00:00",
        }
        self.assertTrue(self.consumer.validate_event(ev))

    def test_consumer_validation_invalid(self):
        ev = {"event_id": "EVT-1"}  # Missing event_type and event_timestamp
        self.assertFalse(self.consumer.validate_event(ev))

    def test_consumer_batch_processing(self):
        consumer = EventConsumer()
        for i in range(5):
            ev = {
                "event_id": f"EVT-{i}",
                "event_type": "product_view",
                "event_timestamp": "2026-11-18 12:00:00",
            }
            consumer.process_event(ev)

        metrics = consumer.get_metrics()
        self.assertEqual(metrics["total_processed"], 5)
        self.assertEqual(metrics["buffer_size"], 5)
        self.assertEqual(metrics["distribution"]["product_view"], 5)


if __name__ == "__main__":
    unittest.main()
