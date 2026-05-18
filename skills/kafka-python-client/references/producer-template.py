"""Synchronous Kafka producer with JSON Schema and header-based schema ID.

Template consumed by the kafka-python-client skill. Adapt the `build_event()`
function to the user's domain.

Key principles enforced here (see references/common-mistakes.md):
- One Producer instance per process, created in main(), passed as a parameter.
- Schema registration is explicit (`auto.register.schemas=False`).
- Schema ID is passed as a Kafka record header on every message.
- Idempotent producer (enable.idempotence=true), graceful shutdown via flush().
- Serializer constructors take schema_str and schema_registry_client as kwargs.
- Per-entity key (key_field) preserves partition ordering.
"""

from __future__ import annotations

import json
import logging
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from random import choice, uniform
from typing import Any

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import MessageField, SerializationContext

from common import (
    get_kafka_config,
    get_schema_registry_config,
    load_config,
    verify_kafka_setup,
    verify_schema_registry,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger("producer")

_shutdown = False


def _handle_signal(signum: int, _frame: Any) -> None:
    global _shutdown
    logger.info("Received signal %d, shutting down", signum)
    _shutdown = True


def delivery_callback(err: Any, msg: Any) -> None:
    """Per-message delivery report."""
    if err is not None:
        logger.error("Delivery failed for key=%s: %s", msg.key(), err)
    else:
        logger.debug(
            "Delivered to %s [%d] @ offset %d", msg.topic(), msg.partition(), msg.offset()
        )


def register_schema(
    sr_client: SchemaRegistryClient,
    subject: str,
    schema_str: str,
) -> int:
    """Register the schema explicitly. Lets errors propagate."""
    from confluent_kafka.schema_registry import Schema

    schema = Schema(schema_str, schema_type="JSON")
    schema_id = sr_client.register_schema(subject_name=subject, schema=schema)
    logger.info("Registered schema for subject %s with id %d", subject, schema_id)
    return schema_id


def create_json_serializer(
    schema_str: str, sr_client: SchemaRegistryClient
) -> JSONSerializer:
    """Build the JSONSerializer with explicit (non-auto) registration.

    Constructor args are passed as keywords because the positional order
    differs between JSONSerializer and AvroSerializer/ProtobufSerializer.
    """
    return JSONSerializer(
        schema_str=schema_str,
        schema_registry_client=sr_client,
        conf={"auto.register.schemas": False, "use.latest.version": True},
    )


def build_event(customers: list[str]) -> dict[str, Any]:
    """Synthesise a sample payment-completed event.

    Adapt this to the user's schema. The skill should rewrite this function
    when generating per-project — the structure here matches the demo's
    seeded schema (`orders.payment.completed-value`).
    """
    return {
        "payment_id": str(uuid.uuid4()),
        "order_id": f"ord-{uuid.uuid4().hex[:8]}",
        "customer_id": choice(customers),
        "amount": round(uniform(5.0, 250.0), 2),
        "currency": "GBP",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {"gateway": "stripe", "channel": "web"},
    }


def produce(
    producer: Producer,
    serializer: JSONSerializer,
    topic: str,
    event: dict[str, Any],
    schema_id: int,
    key_field: str = "order_id",
) -> None:
    """Produce a single event. Producer instance is passed in, not created here."""
    key = event[key_field].encode("utf-8") if key_field else None
    value = serializer(event, SerializationContext(topic, MessageField.VALUE))
    producer.produce(
        topic=topic,
        key=key,
        value=value,
        headers=[("confluent.value.schemaId", str(schema_id).encode("utf-8"))],
        on_delivery=delivery_callback,
    )
    producer.poll(0)


def main() -> int:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    config = load_config()
    verify_kafka_setup(config)
    verify_schema_registry(config)

    producer_conf = {
        **get_kafka_config(config),
        "enable.idempotence": True,
        "acks": "all",
        "linger.ms": 20,
        "compression.type": "lz4",
    }
    producer = Producer(producer_conf)

    sr_client = SchemaRegistryClient(get_schema_registry_config(config))
    schema_path = Path(__file__).parent / "schemas" / "value.schema.json"
    schema_str = schema_path.read_text()
    subject = f"{config['TOPIC']}-value"
    schema_id = register_schema(sr_client, subject, schema_str)
    serializer = create_json_serializer(schema_str, sr_client)

    customers = [f"cust-{i:04d}" for i in range(50)]
    logger.info("Producing to %s @ %s", config["TOPIC"], config["BOOTSTRAP_SERVER"])

    try:
        while not _shutdown:
            event = build_event(customers)
            try:
                produce(producer, serializer, config["TOPIC"], event, schema_id)
            except BufferError:
                logger.warning("Producer queue full, calling poll(1)")
                producer.poll(1)
            time.sleep(1.0)
    finally:
        logger.info("Flushing producer (timeout 10s)")
        outstanding = producer.flush(10)
        if outstanding > 0:
            logger.error("Producer flush left %d undelivered messages", outstanding)
            return 1
        logger.info("Producer shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
