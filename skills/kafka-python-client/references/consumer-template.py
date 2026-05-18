"""Async Kafka consumer with JSON Schema deserialization and graceful shutdown.

Template consumed by the kafka-python-client skill. Adapt the `handle_event()`
function to the user's processing needs.

Key principles enforced here (see references/common-mistakes.md):
- AIOConsumer is used unconditionally; the poll loop runs as a coroutine and never blocks the event loop.
- AsyncJSONDeserializer constructed with kwargs (schema_str=..., schema_registry_client=...).
- Signal-based shutdown: unsubscribe() then close(), both awaited.
- AsyncSchemaRegistryClient for the registry client (does not block the event loop).
- No json.loads fallback — Schema Registry is the only deserialization path.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Any

from confluent_kafka.aio import AIOConsumer
from confluent_kafka.schema_registry._async.json_schema import AsyncJSONDeserializer
from confluent_kafka.schema_registry._async.schema_registry_client import (
    AsyncSchemaRegistryClient,
)
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
logger = logging.getLogger("consumer")

_shutdown = asyncio.Event()


def _install_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown.set)


async def handle_event(event: dict[str, Any]) -> None:
    """Process one deserialized event.

    Adapt this to the user's needs. The skill should rewrite this function
    when generating per-project. Keep it idempotent so re-processing on
    consumer restart is safe.
    """
    logger.info(
        "Received payment_id=%s order_id=%s amount=%s %s",
        event.get("payment_id"),
        event.get("order_id"),
        event.get("amount"),
        event.get("currency"),
    )


async def main() -> int:
    loop = asyncio.get_running_loop()
    _install_signal_handlers(loop)

    config = load_config()
    verify_kafka_setup(config)
    verify_schema_registry(config)

    sr_client = AsyncSchemaRegistryClient(get_schema_registry_config(config))
    schema_path = Path(__file__).parent / "schemas" / "value.schema.json"
    schema_str = schema_path.read_text()

    deserializer = await AsyncJSONDeserializer(
        schema_str=schema_str,
        schema_registry_client=sr_client,
    )

    consumer_conf = {
        **get_kafka_config(config),
        "group.id": config["GROUP_ID"],
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "max.poll.interval.ms": 300000,
        "session.timeout.ms": 45000,
    }
    consumer = AIOConsumer(consumer_conf)
    await consumer.subscribe([config["TOPIC"]])
    logger.info(
        "Subscribed to %s as group %s",
        config["TOPIC"],
        config["GROUP_ID"],
    )

    try:
        while not _shutdown.is_set():
            msg = await consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error("Consumer error: %s", msg.error())
                continue
            try:
                event = await deserializer(
                    msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
                )
            except Exception as exc:
                logger.error(
                    "Deserialize failed offset=%d partition=%d: %s",
                    msg.offset(),
                    msg.partition(),
                    exc,
                )
                continue
            try:
                await handle_event(event)
                await consumer.commit(message=msg, asynchronous=False)
            except Exception as exc:
                logger.exception("handle_event failed, will retry on restart: %s", exc)
                # Do NOT commit — the message will be reprocessed on restart.
    finally:
        logger.info("Unsubscribing and closing consumer")
        try:
            await consumer.unsubscribe()
        finally:
            await consumer.close()
        logger.info("Consumer shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
