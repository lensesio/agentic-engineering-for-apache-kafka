---
name: kafka-shadowtraffic
description: Generate a ShadowTraffic configuration to populate a Kafka topic with realistic synthetic data. Discovers the target topic, its key and value schemas, and the correct serializers from the live cluster via any attached Kafka MCP server, then writes a ready-to-run `shadowtraffic-config.json` and Docker command. Use when the user says "populate my Kafka topic with test data", "set up ShadowTraffic for topic X", "generate synthetic events into my topic", "I need fake data flowing into Kafka", "seed my topic with data", or "mock data for my Kafka topic". Do NOT use for creating topics, reviewing schemas, or building Kafka consumers.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, Write, mcp__*
argument-hint: "[required: topic name or keyword] [optional: environment name]"
compatibility: Works with any Kafka MCP server (Lenses MCP, Confluent MCP, AivenLabs MCP, custom) that exposes topic listing and schema retrieval. Tool names vary per vendor - the skill probes for the equivalent capability rather than calling fixed tool names. Reference implementation tested against the Lenses MCP server (`lensesio/mcp`). Without any Kafka MCP attached, the skill falls back to a hard gate that asks the user for topic, schema, brokers and Schema Registry URL directly.
metadata:
  author: Michael Drogalis
  version: 1.0.0
  mcp-server: any-kafka-mcp
  category: workflow-automation
  approach: problem-first
  patterns: sequential-workflow, context-aware-selection
  tags: [kafka, shadowtraffic, synthetic-data, data-generation, schema-registry, avro, json-schema]
---

# Kafka ShadowTraffic Setup

Generates a ShadowTraffic configuration that populates a Kafka topic with realistic synthetic data. The agent discovers everything — topic name, bootstrap servers, Schema Registry URL, key and value schemas and their serialization format — from the live cluster via whichever Kafka MCP server is attached. It then maps each schema field to the most semantically appropriate ShadowTraffic `_gen` function and writes a ready-to-run config alongside an exact Docker command.

Target topic and environment: $ARGUMENTS

Open your first reply with: "Running the kafka-shadowtraffic skill to set up synthetic data generation."

## Workflow

Copy this checklist and track your progress:

```
ShadowTraffic Setup Progress:
- [ ] Step 1: Discover topic, schemas, and cluster details via the attached Kafka MCP
- [ ] Step 2: Hard gate - confirm with user before generating
- [ ] Step 3: Build the ShadowTraffic config
- [ ] Step 4: Write output files
- [ ] Step 5: Lint the config with ShadowTraffic's linter
- [ ] Step 6: Hand back with Docker run command
```

## Step 1: Discover topic + schemas via any attached Kafka MCP

Read `references/serializer-guide.md` for the full list of serializer classes per format. The high-level discovery shape:

1. **Identify the attached Kafka MCP server** by looking at what's available in the session. Common ones: `mcp__Lenses__*` (Lenses MCP — reference implementation), `mcp__Confluent__*`, `mcp__Aiven__*`, custom servers tagged for Kafka.

2. **Discover the environment / cluster** using whichever tool the MCP exposes (Lenses: `list_environments`; Confluent: `list_clusters`; others vary).

3. **Search for candidate topics** by keyword from the user's prompt:
   - Lenses: `list_datasets(search=<keyword>)` or `list_topics`
   - Confluent: `list_topics` then filter
   - If multiple topics match, present them to the user with partition counts — don't guess.

4. **Fetch the key and value schemas** for the chosen topic:
   - Lenses: `get_dataset` or `get_topic_metadata` — returns schema format (AVRO, JSON, PROTOBUF, NONE) and schema body for both key and value subjects
   - Confluent: `get_schema(subject=<topic>-value)` and `get_schema(subject=<topic>-key)`
   - Bare Schema Registry MCPs: HTTP GET `/subjects/<topic>-value/versions/latest` and `/subjects/<topic>-key/versions/latest`
   - Note both the **format** and the **schema body** — you need both to select the serializer and build generators.

5. **Fetch cluster connection details**:
   - Bootstrap servers (Lenses: `get_topic_metadata` or `list_environments`; most MCPs expose this in cluster/environment metadata)
   - Schema Registry URL (same call, or from environment metadata)

6. **Read partition count** (Lenses: `get_topic_metadata`; most others: `describe_topic` or `get_topic`).

**If no Kafka MCP is attached, or discovery returns nothing**, fall back to the hard gate in Step 2 and ask the user for: topic name, bootstrap servers, Schema Registry URL (if any), key schema format + body, value schema format + body. Be explicit: *"Without a Kafka MCP I can't verify the schema or cluster details — please supply them directly."*

Expected output of Step 1, a recap like:

```
Discovered via <MCP server name>:
- Environment:       staging
- Topic:             orders.payment.completed
- Partitions:        12
- Bootstrap servers: localhost:9092
- Schema Registry:   http://localhost:8081
- Key schema:        String (no schema registration)
- Value schema:      Avro — 6 fields (orderId, customerId, amount, currency, status, createdAt)
```

## Step 2: Hard gate — confirm before generating

**Mandatory.** Do not write any file before sending one message that:

1. Recaps the discovered values from Step 1 as a bulleted list.
2. Lists any open questions discovery couldn't answer (e.g., Schema Registry URL if the MCP didn't expose it).
3. Explicitly asks the user to confirm or correct.

Then STOP and wait for the user's reply. The only way to skip the gate is if the user has already confirmed the recap earlier in this conversation.

**Defaults applied once confirmed:**

- `throttleMs: 500` (2 events per second — a safe rate that won't overwhelm a local cluster)
- Output files written to the current working directory: `shadowtraffic-config.json` and `license.env.example`

## Step 3: Build the ShadowTraffic config

### 3a. Select serializers

Consult `references/serializer-guide.md` for the full class name table. The key rule:

- **Avro** → `io.confluent.kafka.serializers.KafkaAvroSerializer` for key and value; add `schema.registry.url` to `producerConfigs`
- **JSON Schema** → `io.confluent.kafka.serializers.json.KafkaJsonSchemaSerializer` for key and value; add `schema.registry.url`
- **Protobuf** → `io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializer` for key and value; add `schema.registry.url`
- **Plain string key, no schema** → `org.apache.kafka.common.serialization.StringSerializer` for key; `io.shadowtraffic.kafka.serdes.JsonSerializer` for value
- **No schema at all** → `io.shadowtraffic.kafka.serdes.JsonSerializer` for both

Apply serializer selection independently to key and value — they can differ (e.g., String key + Avro value is common).

### 3b. Schema auto-download

When a Confluent serializer is used and `schema.registry.url` is set, ShadowTraffic **automatically downloads the registered schema** from Schema Registry using TopicNameStrategy. You do not need to embed the schema inline — the generator's field structure just needs to match what the downloaded schema expects. ShadowTraffic validates and registers on write.

Only supply `avroSchemaHint` or `jsonSchemaHint` in `localConfigs` if:
- The topic uses a non-standard subject naming strategy, OR
- Auto-download fails (ShadowTraffic will tell you)

### 3c. Build generators from the schema

For each field in the discovered schema, select the most semantically appropriate `_gen`. Consult `references/gen-types.md` for the full mapping table. Summary of common patterns:

| Field pattern | Recommended `_gen` |
|---|---|
| `*Id`, `*_id`, `id` | `{"_gen": "uuid"}` |
| `*name`, `*Name` | `{"_gen": "string", "expr": "#{Name.fullName}"}` |
| `*email*` | `{"_gen": "string", "expr": "#{Internet.emailAddress}"}` |
| `*amount*`, `*price*`, `*cost*` | `{"_gen": "uniformDistribution", "bounds": [1, 1000], "decimals": 2}` |
| `*status*`, `*state*`, `*type*` with enum values | `{"_gen": "oneOf", "choices": [...enum values from schema...]}` |
| `*timestamp*`, `*createdAt*`, `*updatedAt*` | `{"_gen": "now"}` |
| boolean | `{"_gen": "boolean"}` |
| integer count | `{"_gen": "uniformDistribution", "bounds": [0, 100]}` |
| nested object | recurse — apply same rules to each nested field |
| array field | `{"_gen": "repeatedly", "target": <element gen>, "times": {"_gen": "uniformDistribution", "bounds": [1, 5]}}` |

**When the schema has enum symbols** (Avro `"type": "enum"` or JSON Schema `"enum": [...]`), always use `oneOf` with the actual allowed values extracted from the schema — never invent new ones.

**When the schema has a null union** (Avro `["null", "string"]`), use `weightedOneOf` to generate null some fraction of the time:
```json
{"_gen": "weightedOneOf", "choices": [{"weight": 1, "value": null}, {"weight": 9, "value": {"_gen": "string", "expr": "#{Lorem.word}"}}]}
```

### 3d. Full config shape

```json
{
  "generators": [
    {
      "topic": "<topic-name>",
      "connection": "kafka",
      "key": <key-generator>,
      "value": <value-generator>,
      "localConfigs": {
        "throttleMs": 500
      }
    }
  ],
  "connections": {
    "kafka": {
      "kind": "kafka",
      "producerConfigs": {
        "bootstrap.servers": "<discovered-brokers>",
        "key.serializer": "<selected-class>",
        "value.serializer": "<selected-class>"
      }
    }
  }
}
```

When Schema Registry is involved, add to `producerConfigs`:
```json
"schema.registry.url": "<discovered-sr-url>"
```

When connecting to a secured cluster (Confluent Cloud, Aiven, MSK), add the appropriate SASL/SSL fields — see `references/serializer-guide.md` for complete examples.

## Step 4: Write output files

Write exactly two files to the current working directory:

**`shadowtraffic-config.json`** — the complete ShadowTraffic configuration built in Step 3.

**`license.env.example`** — template for the required license environment variables:
```
LICENSE_ID=
LICENSE_EMAIL=
LICENSE_ORGANIZATION=
LICENSE_EDITION=
LICENSE_EXPIRATION=
LICENSE_SIGNATURE=
```

Do not write any other files. Do not write a README unless the user asks.

## Step 5: Lint the config with ShadowTraffic's linter

After writing `shadowtraffic-config.json`, run the ShadowTraffic linter against it to catch typos, unrecognized keys, and structural mistakes before handing back. ShadowTraffic uses open config parsing that silently ignores unknown fields — the linter makes those mistakes visible.

Run:
```bash
docker run --env-file license.env \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --action lint \
  --config /home/config.json
```

**If `license.env` doesn't exist yet** (the user hasn't set up their license), run the linter with placeholder env vars so it can still validate the config structure:
```bash
docker run \
  -e LICENSE_ID=lint \
  -e LICENSE_EMAIL=lint \
  -e LICENSE_ORGANIZATION=lint \
  -e LICENSE_EDITION=lint \
  -e LICENSE_EXPIRATION=lint \
  -e LICENSE_SIGNATURE=lint \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --action lint \
  --config /home/config.json
```

**If the linter reports issues**: fix `shadowtraffic-config.json` to address every finding — unrecognized generator keys, bad `localConfigs` fields, misplaced parameters — and re-run the linter until it passes clean. Do not hand back with lint errors outstanding.

**If Docker is not available** in the user's environment: note that linting was skipped and recommend the user run the lint command themselves before starting data generation.

## Step 6: Hand back with Docker run command

Final message must include all of these:

1. **One-line summary**: what topic, what schema format, how many fields.

2. **Files written**: list `shadowtraffic-config.json` and `license.env.example` with their absolute paths.

3. **Setup instructions**:
   ```bash
   # 1. Get a ShadowTraffic license at https://shadowtraffic.io and fill in your details:
   cp license.env.example license.env
   # (edit license.env with your license values)

   # 2. Run ShadowTraffic:
   docker run --net=host --env-file license.env \
     -v $(pwd)/shadowtraffic-config.json:/home/config.json \
     shadowtraffic/shadowtraffic:latest \
     --config /home/config.json
   ```

4. **Field summary**: a brief table showing each schema field and the `_gen` chosen for it, so the user can spot anything that needs tweaking before running.

5. **Tuning note**: mention that `throttleMs` in `localConfigs` controls the rate (500ms = 2 events/sec); lower it for higher throughput or raise it to slow down.

6. **Auto-schema note** (if Schema Registry was used): *"ShadowTraffic will automatically download the `<topic>-value` schema from Schema Registry and validate generated events against it."*

## Success Criteria

### Quantitative

- Triggers on 90% of "set up ShadowTraffic" or "generate fake Kafka data" queries (see `references/test-cases.md`)
- Completes in under 10 MCP tool calls total
- Generated `shadowtraffic-config.json` passes the ShadowTraffic linter with zero findings before hand-back

### Qualitative

- The user is asked at most one question before generation (the Step 2 confirmation)
- Serializer class matches the topic's actual schema format — never use `JsonSerializer` for an Avro topic
- `_gen` choices are semantically appropriate — a `customerId` field gets `uuid`, not `uniformDistribution`
- The Docker command in Step 5 can be copy-pasted and run immediately without editing (except filling in the license)

## Examples

### Example 1: Avro topic with full MCP discovery (Lenses MCP attached)

User says: *"set up ShadowTraffic for the orders topic in staging"*

Actions:
1. Step 1: `list_environments` → pick `staging`. `list_datasets(search="orders")` → one match: `orders.created`. `get_dataset` returns Avro value schema with fields `orderId (string)`, `customerId (string)`, `amount (double)`, `status (enum: PENDING/CONFIRMED/SHIPPED)`, `createdAt (long/timestamp)`. Bootstrap: `localhost:9092`. Schema Registry: `http://localhost:8081`.
2. Step 2: Recap and confirm — user confirms.
3. Step 3: `KafkaAvroSerializer` for both key and value. `schema.registry.url` set. Generators: `orderId → uuid`, `customerId → uuid`, `amount → uniformDistribution [1,500] decimals:2`, `status → oneOf ["PENDING","CONFIRMED","SHIPPED"]`, `createdAt → now`. Key is a plain `uuid` (string key, no key schema registered).
4. Step 4: Write `shadowtraffic-config.json` and `license.env.example`.
5. Step 5: Run linter — passes clean.
6. Step 6: Hand back with Docker command and field summary table.

Result: User copies the Docker command, runs it, and sees Avro events flowing into `orders.created` at 2/sec.

### Example 2: JSON Schema topic

User says: *"I need fake data flowing into my payments topic"*

Actions:
1. Step 1: MCP discovery finds `payments.initiated` with a JSON Schema value — fields: `paymentId (string)`, `userId (string)`, `amount (number)`, `currency (string, enum: USD/EUR/GBP)`, `status (string)`.
2. Step 2: Recap and confirm.
3. Step 3: `KafkaJsonSchemaSerializer` for value. `schema.registry.url` set. Generators: `paymentId → uuid`, `userId → uuid`, `amount → uniformDistribution [0.01, 5000] decimals:2`, `currency → oneOf ["USD","EUR","GBP"]`, `status → oneOf ["INITIATED","PROCESSING","COMPLETED","FAILED"]`.
4. Steps 4-6: Write files, lint (passes clean), and hand back.

### Example 3: No Kafka MCP attached

User says: *"set up ShadowTraffic to send test data to my Kafka topic"*

Actions:
1. Step 1: No Kafka MCP found in session.
2. Step 2: Hard gate asks the user for: topic name, bootstrap servers, Schema Registry URL (or "none"), key schema format and body, value schema format and body.
3. Steps 3-5: Proceed with user-supplied values.

Result: Config is generated correctly; user is told *"Without a Kafka MCP I couldn't verify these details against the live cluster — run `kafka-schema-review` after to confirm the generated schema matches what's registered."*

## Troubleshooting

### Topic has no registered schema

Cause: Topic exists but nothing is registered in Schema Registry for it.

Solution: Fall back to `io.shadowtraffic.kafka.serdes.JsonSerializer` for both key and value (no Schema Registry needed). Ask the user to describe the expected shape of the messages so you can build generators for it. Note in the hand-back that the generated data won't be schema-validated.

### Multiple topics match the keyword

Cause: Search returns more than one candidate.

Solution: List all candidates with their partition counts and schema formats, and ask the user to pick one. Do not guess.

### Bootstrap server or Schema Registry URL not available from MCP

Cause: The MCP doesn't expose cluster connection details, or the environment has restrictions.

Solution: Ask the user to supply the missing values directly. For bootstrap servers, the default for a local Lenses CE is `localhost:9092`; for Schema Registry, `http://localhost:8081`.

### Linter reports unrecognized keys

Cause: A `_gen` type name is misspelled, a `localConfigs` field doesn't exist, or a key was placed at the wrong nesting level.

Solution: Fix the flagged path in `shadowtraffic-config.json` and re-run the linter. Common mistakes: using `start` instead of `startingFrom` on `sequentialInteger`; putting `throttleMs` directly in the generator instead of inside `localConfigs`; misspelling `weightedOneOf` choices structure.

### ShadowTraffic auto-schema download fails at runtime

Cause: Subject doesn't exist in Schema Registry, or `schema.registry.url` is wrong.

Solution: Fetch the schema body via the MCP (or ask the user to paste it) and add `avroSchemaHint` / `jsonSchemaHint` to `localConfigs`. See `references/serializer-guide.md` for the exact inline schema syntax.

## Output Format

```
## ShadowTraffic config generated

Topic: <topic-name> | Format: <Avro/JSON Schema/plain>

### Files written
- shadowtraffic-config.json   <full path>
- license.env.example         <full path>

### Run it

# 1. Fill in your ShadowTraffic license (get one at https://shadowtraffic.io):
cp license.env.example license.env

# 2. Start generating data:
docker run --net=host --env-file license.env \
  -v $(pwd)/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --config /home/config.json

### What will be generated

| Field       | Generator                            |
|-------------|--------------------------------------|
| orderId     | uuid                                 |
| customerId  | uuid                                 |
| amount      | uniformDistribution [1, 500]         |
| status      | oneOf ["PENDING","CONFIRMED",...]    |
| createdAt   | now (current timestamp)              |

Rate: 2 events/sec (throttleMs: 500). Adjust `throttleMs` in the config to change throughput.

Schema Registry: ShadowTraffic will auto-download the `<topic>-value` schema and validate all generated events against it.

### Lint result
Config passed the ShadowTraffic linter with zero findings.
```
