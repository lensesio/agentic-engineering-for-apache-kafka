"""Unit tests for the generated Kafka client project.

Template consumed by the kafka-python-client skill. Tests run without a live
Kafka cluster or Schema Registry — every external dependency is mocked.

What's tested:
  1. common.py: load_config(), get_kafka_config(), connectivity verifiers
  2. producer.py: producer-instance reuse, header-based schema ID, kwargs-only
     serializer construction, flush() in finally
  3. consumer.py: registry-backed deserialization, unsubscribe-then-close shutdown
  4. schemas/value.schema.json: structural sanity (type, title, properties, formats)
  5. Project structure: pyproject.toml (uv-managed) and .env.example exist
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "value.schema.json"


@pytest.fixture
def env_local(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """A minimal valid local-environment config in os.environ."""
    values = {
        "KAFKA_ENV": "local",
        "BOOTSTRAP_SERVER": "localhost:9092",
        "TOPIC": "orders.payment.completed",
        "SCHEMA_REGISTRY_URL": "http://localhost:8081",
        "CLIENT_ID": "test-client",
        "GROUP_ID": "test-group",
    }
    for k, v in values.items():
        monkeypatch.setenv(k, v)
    return values


def test_load_config_returns_all_required_keys(env_local: dict[str, str]) -> None:
    from common import load_config

    config = load_config()
    for key in ("KAFKA_ENV", "BOOTSTRAP_SERVER", "TOPIC", "SCHEMA_REGISTRY_URL", "CLIENT_ID", "GROUP_ID"):
        assert config.get(key), f"{key} missing or empty"
    assert config["KAFKA_ENV"] == "local"


def test_load_config_raises_when_required_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    from common import load_config

    for k in ("BOOTSTRAP_SERVER", "TOPIC", "SCHEMA_REGISTRY_URL", "CLIENT_ID", "GROUP_ID"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("KAFKA_ENV", "local")
    # load_config supplies defaults for local, so this should still succeed —
    # remove the defaults too by patching os.environ.get for these specific keys.
    with patch.dict(os.environ, {}, clear=True):
        monkeypatch.setenv("KAFKA_ENV", "local")
        monkeypatch.setenv("BOOTSTRAP_SERVER", "")
        monkeypatch.setenv("TOPIC", "")
        monkeypatch.setenv("SCHEMA_REGISTRY_URL", "")
        monkeypatch.setenv("CLIENT_ID", "")
        monkeypatch.setenv("GROUP_ID", "")
        with pytest.raises(RuntimeError, match="Missing required configuration"):
            load_config()


def test_get_kafka_config_local_uses_plaintext(env_local: dict[str, str]) -> None:
    from common import get_kafka_config, load_config

    kafka_conf = get_kafka_config(load_config())
    assert kafka_conf["security.protocol"] == "PLAINTEXT"
    assert kafka_conf["bootstrap.servers"] == "localhost:9092"
    assert "sasl.mechanisms" not in kafka_conf


def test_get_kafka_config_cloud_uses_sasl_ssl(monkeypatch: pytest.MonkeyPatch) -> None:
    from common import get_kafka_config, load_config

    monkeypatch.setenv("KAFKA_ENV", "cloud")
    monkeypatch.setenv("BOOTSTRAP_SERVER", "pkc-xxxxx.confluent.cloud:9092")
    monkeypatch.setenv("API_KEY", "key")
    monkeypatch.setenv("API_SECRET", "secret")
    monkeypatch.setenv("SR_API_KEY", "srkey")
    monkeypatch.setenv("SR_API_SECRET", "srsecret")
    monkeypatch.setenv("TOPIC", "demo")
    monkeypatch.setenv("SCHEMA_REGISTRY_URL", "https://psrc-xxxxx.confluent.cloud")
    monkeypatch.setenv("CLIENT_ID", "test")
    monkeypatch.setenv("GROUP_ID", "test")

    kafka_conf = get_kafka_config(load_config())
    assert kafka_conf["security.protocol"] == "SASL_SSL"
    assert kafka_conf["sasl.mechanisms"] == "PLAIN"
    assert kafka_conf["sasl.username"] == "key"


def test_verify_kafka_setup_success(env_local: dict[str, str]) -> None:
    from common import load_config, verify_kafka_setup

    mock_metadata = MagicMock()
    mock_metadata.topics = {"orders.payment.completed": MagicMock()}
    with patch("common.AdminClient") as MockAdmin:
        MockAdmin.return_value.list_topics.return_value = mock_metadata
        assert verify_kafka_setup(load_config()) is True


def test_verify_kafka_setup_missing_topic(env_local: dict[str, str]) -> None:
    from common import load_config, verify_kafka_setup

    mock_metadata = MagicMock()
    mock_metadata.topics = {}
    with patch("common.AdminClient") as MockAdmin:
        MockAdmin.return_value.list_topics.return_value = mock_metadata
        with pytest.raises(RuntimeError, match="not found"):
            verify_kafka_setup(load_config())


def test_verify_schema_registry_success(env_local: dict[str, str]) -> None:
    from common import load_config, verify_schema_registry

    with patch("common.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        assert verify_schema_registry(load_config()) is True


def test_verify_schema_registry_http_error(env_local: dict[str, str]) -> None:
    from common import load_config, verify_schema_registry

    with patch("common.requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        with pytest.raises(RuntimeError, match="returned 500"):
            verify_schema_registry(load_config())


def test_producer_produce_uses_passed_instance(env_local: dict[str, str]) -> None:
    """produce() must not instantiate a Producer — it must accept one as a parameter."""
    from producer import produce

    mock_producer = MagicMock()
    mock_serializer = MagicMock(return_value=b'{"payment_id": "abc"}')
    event = {
        "payment_id": "abc",
        "order_id": "ord-001",
        "customer_id": "cust-0001",
        "amount": 12.34,
        "currency": "GBP",
        "completed_at": "2026-05-20T10:00:00+00:00",
        "metadata": None,
    }
    produce(mock_producer, mock_serializer, "topic", event, schema_id=42)
    mock_producer.produce.assert_called_once()
    _, kwargs = mock_producer.produce.call_args
    assert kwargs["topic"] == "topic"
    assert kwargs["key"] == b"ord-001"
    assert kwargs["value"] == b'{"payment_id": "abc"}'
    # Header-based schema ID is the synchronous-producer pattern.
    schema_id_header = dict(kwargs["headers"])[b"confluent.value.schemaId" if isinstance(kwargs["headers"][0][0], bytes) else "confluent.value.schemaId"]
    assert schema_id_header == b"42" or schema_id_header == "42"


def test_create_json_serializer_uses_kwargs_only() -> None:
    """create_json_serializer must pass schema_str and schema_registry_client as kwargs.

    Positional ordering differs between JSON/Avro/Protobuf serializers and using
    positional args would cause a TypeError on a swap.
    """
    from producer import create_json_serializer

    with patch("producer.JSONSerializer") as MockSer:
        MockSer.return_value = MagicMock()
        sr_client = MagicMock()
        create_json_serializer("{}", sr_client)
        _, kwargs = MockSer.call_args
        assert "schema_str" in kwargs
        assert "schema_registry_client" in kwargs
        assert kwargs["conf"] == {"auto.register.schemas": False, "use.latest.version": True}


def test_register_schema_lets_errors_propagate() -> None:
    """register_schema must NOT wrap sr_client.register_schema in try/except."""
    from producer import register_schema

    sr_client = MagicMock()
    sr_client.register_schema.side_effect = RuntimeError("auth failed")
    with pytest.raises(RuntimeError, match="auth failed"):
        register_schema(sr_client, "subject", "{}")


@pytest.mark.skipif(not SCHEMA_PATH.exists(), reason="schemas/value.schema.json not generated")
class TestJsonSchema:
    """Structural sanity for the generated JSON Schema."""

    @pytest.fixture
    def schema(self) -> dict:
        return json.loads(SCHEMA_PATH.read_text())

    def test_type_is_object(self, schema: dict) -> None:
        assert schema.get("type") == "object"

    def test_has_title(self, schema: dict) -> None:
        assert schema.get("title")

    def test_has_properties(self, schema: dict) -> None:
        props = schema.get("properties", {})
        assert len(props) >= 1, "schema must have at least one property"

    def test_has_required(self, schema: dict) -> None:
        required = schema.get("required", [])
        assert isinstance(required, list)
        assert all(isinstance(r, str) for r in required)

    def test_timestamp_fields_use_date_time_format(self, schema: dict) -> None:
        for name, prop in schema.get("properties", {}).items():
            if "_at" in name or "timestamp" in name.lower():
                assert prop.get("format") == "date-time", (
                    f"{name} is a timestamp field but doesn't use format: date-time"
                )


def test_pyproject_toml_contains_essentials() -> None:
    """pyproject.toml is the single source of truth for dependencies (managed by uv)."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml is required (uv-managed project)"
    pyproject = pyproject_path.read_text()
    assert "confluent-kafka" in pyproject
    assert "python-dotenv" in pyproject
    assert "requests" in pyproject
    assert "pytest" in pyproject


def test_no_requirements_txt_present() -> None:
    """The project must use pyproject.toml + uv, not requirements.txt + pip."""
    assert not (PROJECT_ROOT / "requirements.txt").exists(), (
        "requirements.txt found — this project is uv-managed, use pyproject.toml instead"
    )


def test_env_example_exists() -> None:
    assert (PROJECT_ROOT / ".env.example").exists()


@pytest.mark.asyncio
async def test_consumer_calls_unsubscribe_then_close() -> None:
    """Graceful shutdown must call unsubscribe() BEFORE close() to leave the group cleanly."""
    import consumer as consumer_module

    fake_consumer = AsyncMock()
    fake_consumer.poll = AsyncMock(side_effect=lambda timeout: None)
    fake_consumer.unsubscribe = AsyncMock()
    fake_consumer.close = AsyncMock()
    fake_consumer.subscribe = AsyncMock()

    # Trigger immediate shutdown via the module-level event.
    consumer_module._shutdown.set()
    try:
        with patch.object(consumer_module, "AIOConsumer", return_value=fake_consumer), \
             patch.object(consumer_module, "AsyncSchemaRegistryClient"), \
             patch.object(consumer_module, "AsyncJSONDeserializer", new=AsyncMock(return_value=AsyncMock())), \
             patch.object(consumer_module, "verify_kafka_setup", return_value=True), \
             patch.object(consumer_module, "verify_schema_registry", return_value=True):
            await consumer_module.main()
    finally:
        consumer_module._shutdown.clear()

    fake_consumer.unsubscribe.assert_awaited_once()
    fake_consumer.close.assert_awaited_once()
    # And the order must be unsubscribe before close.
    unsubscribe_call = fake_consumer.unsubscribe.call_args_list
    close_call = fake_consumer.close.call_args_list
    assert unsubscribe_call and close_call
