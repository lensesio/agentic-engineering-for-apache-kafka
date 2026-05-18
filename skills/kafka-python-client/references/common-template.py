"""Shared configuration loading and connectivity verification.

Template consumed by the kafka-python-client skill. Generated projects
import from this module; do not import this file directly into your app.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import requests
from confluent_kafka.admin import AdminClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_REQUIRED_KEYS: tuple[str, ...] = (
    "BOOTSTRAP_SERVER",
    "TOPIC",
    "SCHEMA_REGISTRY_URL",
    "CLIENT_ID",
    "GROUP_ID",
)


def load_config() -> dict[str, str]:
    """Load configuration from `.env` (if present) and environment variables.

    Falls back to environment variables for every key, so the same code path
    works in containers where `.env` is not mounted.
    """
    dotenv_path = Path(__file__).parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)

    env = os.environ.get("KAFKA_ENV", "local").lower()
    config = {
        "KAFKA_ENV": env,
        "BOOTSTRAP_SERVER": os.environ.get("BOOTSTRAP_SERVER", "localhost:9092"),
        "TOPIC": os.environ.get("TOPIC", "demo-topic"),
        "SCHEMA_REGISTRY_URL": os.environ.get(
            "SCHEMA_REGISTRY_URL", "http://localhost:8081"
        ),
        "CLIENT_ID": os.environ.get("CLIENT_ID", "python-client"),
        "GROUP_ID": os.environ.get("GROUP_ID", "python-consumer-group"),
    }

    if env == "cloud":
        config["API_KEY"] = os.environ.get("API_KEY", "")
        config["API_SECRET"] = os.environ.get("API_SECRET", "")
        config["SR_API_KEY"] = os.environ.get("SR_API_KEY", "")
        config["SR_API_SECRET"] = os.environ.get("SR_API_SECRET", "")

    missing = [k for k in _REQUIRED_KEYS if not config.get(k)]
    if missing:
        raise RuntimeError(
            f"Missing required configuration keys: {missing}. "
            "Copy .env.example to .env and fill them in."
        )
    return config


def get_kafka_config(config: dict[str, str]) -> dict[str, Any]:
    """Build the librdkafka client config dict.

    Shared by producer and consumer. Branches on KAFKA_ENV. Note that
    `message.max.bytes` is intentionally not set here — it's a client-global
    config in librdkafka and over-tuning it causes the consumer to refuse to
    start (fetch.max.bytes must be >= message.max.bytes).
    """
    base: dict[str, Any] = {
        "bootstrap.servers": config["BOOTSTRAP_SERVER"],
        "client.id": config["CLIENT_ID"],
    }
    env = config["KAFKA_ENV"]
    if env == "cloud":
        if not config.get("API_KEY") or not config.get("API_SECRET"):
            raise RuntimeError(
                "KAFKA_ENV=cloud requires API_KEY and API_SECRET in .env"
            )
        base.update(
            {
                "security.protocol": "SASL_SSL",
                "sasl.mechanisms": "PLAIN",
                "sasl.username": config["API_KEY"],
                "sasl.password": config["API_SECRET"],
            }
        )
    elif env == "local":
        base["security.protocol"] = "PLAINTEXT"
    else:
        raise RuntimeError(f"Unknown KAFKA_ENV: {env}. Use 'cloud' or 'local'.")
    return base


def get_schema_registry_config(config: dict[str, str]) -> dict[str, Any]:
    """Build the Schema Registry client config dict."""
    sr_config: dict[str, Any] = {"url": config["SCHEMA_REGISTRY_URL"]}
    if config["KAFKA_ENV"] == "cloud":
        if not config.get("SR_API_KEY") or not config.get("SR_API_SECRET"):
            raise RuntimeError(
                "KAFKA_ENV=cloud requires SR_API_KEY and SR_API_SECRET in .env"
            )
        sr_config["basic.auth.user.info"] = (
            f"{config['SR_API_KEY']}:{config['SR_API_SECRET']}"
        )
    return sr_config


def verify_kafka_setup(config: dict[str, str], timeout: float = 5.0) -> bool:
    """Verify the Kafka broker is reachable and the topic exists.

    Returns True on success, raises with a clear message on failure.
    """
    try:
        admin = AdminClient(get_kafka_config(config))
        metadata = admin.list_topics(timeout=timeout)
    except Exception as exc:
        raise RuntimeError(
            f"Kafka broker {config['BOOTSTRAP_SERVER']} unreachable: {exc}"
        ) from exc

    topic = config["TOPIC"]
    if topic not in metadata.topics:
        raise RuntimeError(
            f"Topic '{topic}' not found on {config['BOOTSTRAP_SERVER']}. "
            "Create it before running this app."
        )
    logger.info("Kafka broker reachable, topic '%s' exists", topic)
    return True


def verify_schema_registry(config: dict[str, str], timeout: float = 5.0) -> bool:
    """HTTP-check the Schema Registry endpoint."""
    url = f"{config['SCHEMA_REGISTRY_URL'].rstrip('/')}/subjects"
    auth: tuple[str, str] | None = None
    if config["KAFKA_ENV"] == "cloud":
        auth = (config["SR_API_KEY"], config["SR_API_SECRET"])
    try:
        resp = requests.get(url, auth=auth, timeout=timeout)
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Schema Registry {config['SCHEMA_REGISTRY_URL']} unreachable: {exc}"
        ) from exc
    if resp.status_code >= 400:
        raise RuntimeError(
            f"Schema Registry returned {resp.status_code} for GET /subjects"
        )
    logger.info("Schema Registry reachable at %s", config["SCHEMA_REGISTRY_URL"])
    return True
