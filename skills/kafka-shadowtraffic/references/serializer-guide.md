# ShadowTraffic Kafka Serializer Guide

## Serializer class names

All Confluent serializers listed here are supported by ShadowTraffic natively. ShadowTraffic also ships its own `JsonSerializer` for when Schema Registry is not involved.

| Schema format | key.serializer | value.serializer | schema.registry.url needed? |
|---|---|---|---|
| Avro | `io.confluent.kafka.serializers.KafkaAvroSerializer` | `io.confluent.kafka.serializers.KafkaAvroSerializer` | Yes |
| JSON Schema | `io.confluent.kafka.serializers.json.KafkaJsonSchemaSerializer` | `io.confluent.kafka.serializers.json.KafkaJsonSchemaSerializer` | Yes |
| Protobuf | `io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializer` | `io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializer` | Yes |
| String key only | `org.apache.kafka.common.serialization.StringSerializer` | _(value format applies)_ | Only if value needs it |
| Plain / no schema | `io.shadowtraffic.kafka.serdes.JsonSerializer` | `io.shadowtraffic.kafka.serdes.JsonSerializer` | No |

Apply serializer selection **independently** to key and value. String key + Avro value is the most common mixed case:

```json
"producerConfigs": {
  "bootstrap.servers": "localhost:9092",
  "schema.registry.url": "http://localhost:8081",
  "key.serializer": "org.apache.kafka.common.serialization.StringSerializer",
  "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer"
}
```

## Schema auto-download

When `schema.registry.url` is set and a Confluent serializer is used, ShadowTraffic automatically downloads the latest schema version from Schema Registry using **TopicNameStrategy** (`<topic>-key` and `<topic>-value` subjects). You do not need to embed the schema in the config.

To override the subject name (e.g. if the topic uses RecordNameStrategy), set `schemaRegistrySubject` in the generator's `localConfigs`:

```json
"localConfigs": {
  "schemaRegistrySubject": "foo.bar.MyRecord"
}
```

## Inline schema hints (fallback)

If auto-download fails or you want to override the downloaded schema, supply it explicitly via `localConfigs`:

**Avro — inline schema:**
```json
"localConfigs": {
  "avroSchemaHint": {
    "key": {
      "type": "record",
      "name": "OrderKey",
      "fields": [{"name": "orderId", "type": "string"}]
    },
    "value": {
      "type": "record",
      "name": "OrderValue",
      "fields": [
        {"name": "amount", "type": "double"},
        {"name": "status", "type": {"type": "enum", "name": "Status", "symbols": ["PENDING", "CONFIRMED"]}}
      ]
    }
  }
}
```

**Avro — load from file** (when the `.avsc` file is mounted into the container):
```json
"localConfigs": {
  "avroSchemaHint": {
    "value": {"_gen": "loadJsonFile", "file": "/home/schema.avsc"}
  }
}
```

**JSON Schema — inline:**
```json
"localConfigs": {
  "jsonSchemaHint": {
    "value": {
      "type": "object",
      "properties": {
        "orderId": {"type": "string"},
        "amount": {"type": "number"}
      },
      "required": ["orderId", "amount"]
    }
  }
}
```

## Connection templates

### Local cluster (no auth)
```json
"connections": {
  "kafka": {
    "kind": "kafka",
    "producerConfigs": {
      "bootstrap.servers": "localhost:9092",
      "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
      "value.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer"
    }
  }
}
```

### Local cluster with Schema Registry
```json
"connections": {
  "kafka": {
    "kind": "kafka",
    "producerConfigs": {
      "bootstrap.servers": "localhost:9092",
      "schema.registry.url": "http://localhost:8081",
      "key.serializer": "org.apache.kafka.common.serialization.StringSerializer",
      "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer"
    }
  }
}
```

### Confluent Cloud
```json
"connections": {
  "kafka": {
    "kind": "kafka",
    "producerConfigs": {
      "bootstrap.servers": "xxx.confluent.cloud:9092",
      "schema.registry.url": "https://xxx.confluent.cloud",
      "basic.auth.credentials.source": "USER_INFO",
      "basic.auth.user.info": "<sr-api-key>:<sr-api-secret>",
      "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='<api-key>' password='<api-secret>';",
      "sasl.mechanism": "PLAIN",
      "security.protocol": "SASL_SSL",
      "key.serializer": "org.apache.kafka.common.serialization.StringSerializer",
      "value.serializer": "io.confluent.kafka.serializers.KafkaAvroSerializer"
    }
  }
}
```

### Aiven (SSL client certificates)
```json
"connections": {
  "kafka": {
    "kind": "kafka",
    "producerConfigs": {
      "bootstrap.servers": "xxx.aivencloud.com:12345",
      "security.protocol": "SSL",
      "ssl.keystore.location": "/home/ssl/client.keystore.p12",
      "ssl.keystore.password": "<password>",
      "ssl.truststore.location": "/home/ssl/client.truststore.jks",
      "ssl.truststore.password": "<password>",
      "ssl.key.password": "<password>",
      "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
      "value.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer"
    }
  }
}
```

Mount the SSL directory: `-v $(pwd)/ssl:/home/ssl`

### Amazon MSK (IAM)
```json
"connections": {
  "kafka": {
    "kind": "kafka",
    "producerConfigs": {
      "bootstrap.servers": "xxxx.kafka-serverless.us-east-2.amazonaws.com:9098",
      "security.protocol": "SASL_SSL",
      "sasl.mechanism": "AWS_MSK_IAM",
      "sasl.jaas.config": "software.amazon.msk.auth.iam.IAMLoginModule required;",
      "sasl.client.callback.handler.class": "software.amazon.msk.auth.iam.IAMClientCallbackHandler",
      "key.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer",
      "value.serializer": "io.shadowtraffic.kafka.serdes.JsonSerializer"
    }
  }
}
```

## Docker run command

Basic:
```bash
docker run --net=host --env-file license.env \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --config /home/config.json
```

With mounted SSL certs (Aiven):
```bash
docker run --net=host --env-file license.env \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  -v $(pwd)/ssl:/home/ssl \
  shadowtraffic/shadowtraffic:latest \
  --config /home/config.json
```

## Linting the config

Always lint before handing back. Run:

```bash
docker run --env-file license.env \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --action lint \
  --config /home/config.json
```

If `license.env` isn't set up yet, use placeholder values — the linter validates config structure, not the license:

```bash
docker run \
  -e LICENSE_ID=lint -e LICENSE_EMAIL=lint \
  -e LICENSE_ORGANIZATION=lint -e LICENSE_EDITION=lint \
  -e LICENSE_EXPIRATION=lint -e LICENSE_SIGNATURE=lint \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --action lint \
  --config /home/config.json
```

Fix every finding the linter reports before proceeding.

## License environment variables

ShadowTraffic requires a license supplied via environment variables. Template (`license.env.example`):

```
LICENSE_ID=
LICENSE_EMAIL=
LICENSE_ORGANIZATION=
LICENSE_EDITION=
LICENSE_EXPIRATION=
LICENSE_SIGNATURE=
```

Get a license at https://shadowtraffic.io.
