# Java TestContainers Template for ShadowTraffic

This is the annotated reference template for the generated test class. Adapt it based on whether Schema Registry is required and what the topic's schema looks like.

## Full template — with Schema Registry (Avro / JSON Schema / Protobuf topics)

```java
package <package>;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import static org.assertj.core.api.Assertions.assertThat;

@Testcontainers
class <ClassName> {

    // Shared Docker network — all containers communicate over this.
    // ShadowTraffic reaches Kafka at kafka:9092 and Schema Registry at
    // http://schema-registry:8081, matching the adapted config.
    static final Network network = Network.newNetwork();

    @Container
    static final KafkaContainer kafka =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.7.0"))
            .withNetwork(network)
            .withNetworkAliases("kafka");

    // Include this block only when the topic uses Avro, JSON Schema, or Protobuf.
    @Container
    static final GenericContainer<?> schemaRegistry =
        new GenericContainer<>(DockerImageName.parse("confluentinc/cp-schema-registry:7.7.0"))
            .withNetwork(network)
            .withNetworkAliases("schema-registry")
            .dependsOn(kafka)
            .withEnv("SCHEMA_REGISTRY_HOST_NAME", "schema-registry")
            .withEnv("SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS", "kafka:9092")
            .withExposedPorts(8081)
            // Wait until Schema Registry is accepting requests before ShadowTraffic starts.
            .waitingFor(Wait.forHttp("/subjects").forStatusCode(200));

    @Container
    static final GenericContainer<?> shadowTraffic =
        new GenericContainer<>(DockerImageName.parse("shadowtraffic/shadowtraffic:latest"))
            .withNetwork(network)
            // ShadowTraffic must not start until Kafka (and Schema Registry) are ready.
            .dependsOn(kafka, schemaRegistry)
            // License is read from environment variables — never hardcoded.
            // Export these in your shell or CI environment before running the test.
            .withEnv("LICENSE_ID",           Objects.requireNonNull(System.getenv("LICENSE_ID"),           "LICENSE_ID env var is required"))
            .withEnv("LICENSE_EMAIL",        Objects.requireNonNull(System.getenv("LICENSE_EMAIL"),        "LICENSE_EMAIL env var is required"))
            .withEnv("LICENSE_ORGANIZATION", Objects.requireNonNull(System.getenv("LICENSE_ORGANIZATION"), "LICENSE_ORGANIZATION env var is required"))
            .withEnv("LICENSE_EDITION",      Objects.requireNonNull(System.getenv("LICENSE_EDITION"),      "LICENSE_EDITION env var is required"))
            .withEnv("LICENSE_EXPIRATION",   Objects.requireNonNull(System.getenv("LICENSE_EXPIRATION"),   "LICENSE_EXPIRATION env var is required"))
            .withEnv("LICENSE_SIGNATURE",    Objects.requireNonNull(System.getenv("LICENSE_SIGNATURE"),    "LICENSE_SIGNATURE env var is required"))
            // Config is loaded from src/test/resources/shadowtraffic-config.json at build time.
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("shadowtraffic-config.json"),
                "/home/config.json"
            )
            .withCommand("--config", "/home/config.json");

    @Test
    void shouldReceiveEventsFromShadowTraffic() {
        int expectedEvents = 100; // must match maxEvents in shadowtraffic-config.json

        // Use kafka.getBootstrapServers() for the consumer — this is the host-mapped
        // address TestContainers exposes externally, not the internal kafka:9092.
        try (KafkaConsumer<String, Object> consumer = new KafkaConsumer<>(Map.of(
            ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapServers(),
            ConsumerConfig.GROUP_ID_CONFIG,          "shadowtraffic-test-group",
            ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest",
            // Replace with the correct deserializer for your topic's format:
            // - String/JSON:  "org.apache.kafka.common.serialization.StringDeserializer"
            // - Avro:         "io.confluent.kafka.serializers.KafkaAvroDeserializer"
            // - JSON Schema:  "io.confluent.kafka.serializers.json.KafkaJsonSchemaDeserializer"
            ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,   "org.apache.kafka.common.serialization.StringDeserializer",
            ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer"
        ))) {
            consumer.subscribe(List.of("<topic-name>"));

            List<ConsumerRecord<String, Object>> received = new ArrayList<>();
            long deadline = System.currentTimeMillis() + Duration.ofSeconds(30).toMillis();

            while (received.size() < expectedEvents && System.currentTimeMillis() < deadline) {
                consumer.poll(Duration.ofMillis(500)).forEach(received::add);
            }

            assertThat(received)
                .as("ShadowTraffic should have produced %d events", expectedEvents)
                .hasSize(expectedEvents);

            // Spot-check: verify the first event has the expected shape.
            // Replace "fieldName" with an actual field from your schema.
            // For JSON string values: assertThat(record.value()).contains("fieldName");
            // For Avro GenericRecord: assertThat(record.value().get("fieldName")).isNotNull();
            ConsumerRecord<String, Object> sample = received.get(0);
            assertThat(sample.value()).isNotNull();
        }
    }
}
```

## Minimal template — plain JSON / no Schema Registry

```java
package <package>;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import static org.assertj.core.api.Assertions.assertThat;

@Testcontainers
class <ClassName> {

    static final Network network = Network.newNetwork();

    @Container
    static final KafkaContainer kafka =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.7.0"))
            .withNetwork(network)
            .withNetworkAliases("kafka");

    @Container
    static final GenericContainer<?> shadowTraffic =
        new GenericContainer<>(DockerImageName.parse("shadowtraffic/shadowtraffic:latest"))
            .withNetwork(network)
            .dependsOn(kafka)
            .withEnv("LICENSE_ID",           Objects.requireNonNull(System.getenv("LICENSE_ID"),           "LICENSE_ID env var is required"))
            .withEnv("LICENSE_EMAIL",        Objects.requireNonNull(System.getenv("LICENSE_EMAIL"),        "LICENSE_EMAIL env var is required"))
            .withEnv("LICENSE_ORGANIZATION", Objects.requireNonNull(System.getenv("LICENSE_ORGANIZATION"), "LICENSE_ORGANIZATION env var is required"))
            .withEnv("LICENSE_EDITION",      Objects.requireNonNull(System.getenv("LICENSE_EDITION"),      "LICENSE_EDITION env var is required"))
            .withEnv("LICENSE_EXPIRATION",   Objects.requireNonNull(System.getenv("LICENSE_EXPIRATION"),   "LICENSE_EXPIRATION env var is required"))
            .withEnv("LICENSE_SIGNATURE",    Objects.requireNonNull(System.getenv("LICENSE_SIGNATURE"),    "LICENSE_SIGNATURE env var is required"))
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("shadowtraffic-config.json"),
                "/home/config.json"
            )
            .withCommand("--config", "/home/config.json");

    @Test
    void shouldReceiveEventsFromShadowTraffic() {
        int expectedEvents = 100;

        try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(Map.of(
            ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapServers(),
            ConsumerConfig.GROUP_ID_CONFIG,          "shadowtraffic-test-group",
            ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest",
            ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,   "org.apache.kafka.common.serialization.StringDeserializer",
            ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer"
        ))) {
            consumer.subscribe(List.of("<topic-name>"));

            List<ConsumerRecord<String, String>> received = new ArrayList<>();
            long deadline = System.currentTimeMillis() + Duration.ofSeconds(30).toMillis();

            while (received.size() < expectedEvents && System.currentTimeMillis() < deadline) {
                consumer.poll(Duration.ofMillis(500)).forEach(received::add);
            }

            assertThat(received)
                .as("ShadowTraffic should have produced %d events", expectedEvents)
                .hasSize(expectedEvents);

            assertThat(received.get(0).value()).isNotNull();
        }
    }
}
```

## Class naming convention

Derive the class name from the topic name. Replace dots and hyphens with title-case word boundaries:

| Topic name | Class name |
|---|---|
| `orders.created` | `OrdersCreatedShadowTrafficTest` |
| `orders.payment.completed` | `OrdersPaymentCompletedShadowTrafficTest` |
| `audit-events` | `AuditEventsShadowTrafficTest` |
| `user_profiles` | `UserProfilesShadowTrafficTest` |

## Deserializer selection

Match the consumer deserializer to the topic's schema format:

| Schema format | VALUE_DESERIALIZER_CLASS_CONFIG |
|---|---|
| Plain / no schema | `org.apache.kafka.common.serialization.StringDeserializer` |
| JSON Schema | `io.confluent.kafka.serializers.json.KafkaJsonSchemaDeserializer` |
| Avro | `io.confluent.kafka.serializers.KafkaAvroDeserializer` |
| Protobuf | `io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializer` |

For Schema Registry-backed formats, also add to the consumer config:
```java
"schema.registry.url", "http://" + schemaRegistry.getHost() + ":" + schemaRegistry.getMappedPort(8081)
```

## Container image versions

Use pinned versions, not `latest`, for reproducibility in CI. Current recommended versions:
- Kafka: `confluentinc/cp-kafka:7.7.0`
- Schema Registry: `confluentinc/cp-schema-registry:7.7.0`
- ShadowTraffic: `shadowtraffic/shadowtraffic:latest` (ShadowTraffic doesn't publish stable tags yet — `latest` is acceptable)
