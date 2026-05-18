---
name: kafka-python-client
description: Scaffold a production-ready Python Kafka producer and consumer using `confluent-kafka-python`, with Schema Registry, graceful shutdown, idempotent producer, tests and a complete project layout. Discovers the target topic, partition count and registered JSON Schema directly from the live cluster via any attached Kafka MCP server (Lenses MCP, Confluent's MCP, Aiven's, custom) before asking the user. Use when user says "build a Python Kafka consumer", "scaffold a Kafka client in Python", "add Kafka to my Python service", "consume from `<topic>` in Python" or "write a Kafka producer". Do NOT use for Kafka Connect connectors, schema-evolution reviews or non-Python clients.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, Write, mcp__*
argument-hint: "[optional: target environment name] [optional: keyword from the topic name]"
compatibility: Works with any Kafka MCP server (Lenses MCP, Confluent MCP, AivenLabs MCP, custom) that exposes topic listing and schema retrieval. Tool names vary per vendor - the skill probes for the equivalent capability rather than calling fixed tool names. Reference implementation tested against the Lenses MCP server (`lensesio/mcp`). Without any Kafka MCP attached, the skill falls back to a hard gate that asks the user for topic, schema and cluster details directly.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: any-kafka-mcp
  category: workflow-automation
  approach: problem-first
  patterns: sequential-workflow, iterative-refinement, context-aware-selection
  tags: [kafka, python, producer, consumer, scaffold, schema-registry, json-schema, mcp-agnostic]
---

# Kafka Python Client Scaffold

Generates a production-ready Python project that produces to and consumes from a Kafka topic using `confluent-kafka-python`, with Schema Registry (JSON Schema), graceful shutdown, idempotent producer, header-based schema identification, and tests. The agent should discover everything about the target topic (name, partitions, registered schema) from the live cluster via whichever Kafka MCP server is attached — Lenses MCP, Confluent's, Aiven's, or any other — **before** asking the user. Only fall back to questions if no Kafka MCP is attached or discovery returns nothing.

Target environment and keyword: $ARGUMENTS

Open your first reply with: "Running the kafka-python-client skill to scaffold this project."

## Workflow

Copy this checklist and track your progress:

```
Scaffold Progress:
- [ ] Step 1: Discover topic + schema via the attached Kafka MCP
- [ ] Step 2: Hard gate - confirm with user before generating
- [ ] Step 3: Generate the project files
- [ ] Step 4: Run pytest against the generated tests
- [ ] Step 5: Run validation gate (kafka-topic-audit + kafka-perf-review)
- [ ] Step 6: Hand back with run instructions
```

1. **Discover topic + schema** via whichever Kafka MCP is attached (see `references/mcp-discovery.md`)
2. **Hard gate**: recap what was discovered, confirm with user before generating anything
3. **Generate the project** using the templates in `references/`
4. **Run pytest** against the generated `tests/` and fix any failures (fix the code, not the tests)
5. **Run validation gate**: invoke `kafka-topic-audit` against the target topic and `kafka-perf-review` against the generated `producer.py` and `consumer.py`
6. **Hand back** with run instructions and the validation-gate findings inline

## Step 1: Discover topic + schema via any attached Kafka MCP

Read `references/mcp-discovery.md` for the full probing procedure, vendor-specific tool-name hints and fallbacks. The high-level shape:

1. **Identify the attached Kafka MCP server** by looking at what's available in the session. Common ones: `mcp__Lenses__*` (Lenses MCP — reference implementation), `mcp__Confluent__*`, `mcp__Aiven__*`, custom servers tagged for Kafka.
2. **Discover the environment / cluster** using whichever tool the MCP exposes (Lenses: `list_environments`; Confluent: `list_clusters`; others vary).
3. **Search for candidate topics** by keyword from the user's prompt (Lenses: `list_datasets(search=...)`; raw Kafka admin MCPs: `list_topics` then filter).
4. **Fetch the registered schema** for the chosen topic's value subject (Lenses: `get_dataset`; Confluent: `get_schema(subject=<topic>-value)`; bare Schema Registry MCPs: HTTP GET against `/subjects/<topic>-value/versions/latest`).
5. **Read partition count and replication factor** (Lenses: `get_topic_metadata`; most others expose a `describe_topic` or `get_topic` equivalent).
6. **Check existing consumer groups** to suggest a non-colliding `GROUP_ID` (Lenses: `list_consumer_groups_by_topic`; most others: `list_consumer_groups`).

**If multiple candidate topics match the keyword**, ask the user which one — don't guess. List them with their partition counts and field names so the choice is obvious.

**If no Kafka MCP is attached, or discovery returns nothing**, fall back to the hard gate in Step 2 and ask the user for the missing pieces directly. Be explicit about what was lost: *"Without a Kafka MCP I can't verify the schema matches what's registered against the topic."*

Expected output of Step 1: a recap like

```
Discovered via <MCP server name> (Lenses MCP / Confluent MCP / ...):
- Cluster:        staging
- Topic:          orders.payment.completed
- Partitions:     12
- RF:             1 (single-broker cluster — kafka-topic-audit will flag this)
- Value schema:   JSON Schema, 6 required fields + 1 optional (pulled from registry)
- Suggested group: payments-service-<8-char-random>
```

## Step 2: Hard gate — confirm before generating

**Mandatory.** Do not write any file before sending one message that:

1. Recaps the discovered values from Step 1 as a bulleted list.
2. Lists any open questions the discovery couldn't answer (e.g. project directory, sync vs async producer style if the user has a strong preference).
3. Explicitly asks the user to confirm or correct.

Then STOP and wait for the user's reply. The recap exists so the user can spot a misread before any files are written, and it is mandatory even on prompts that look fully specified.

The only way to skip the gate is if the user has already confirmed the recap earlier in this conversation.

Defaults to apply once confirmed:

- **Producer style:** synchronous `Producer` from `confluent_kafka` unless the user signals an async runtime, in which case offer `AIOProducer`. Async signals include: explicit mention of `asyncio`; any async-first web framework (FastAPI, Starlette, Quart, Litestar, BlackSheep, Robyn, aiohttp, Sanic, Tornado); ASGI applications generally; or async task systems (ARQ, Dramatiq, Celery with async tasks). If the user mentions Django, default to sync `Producer` unless they explicitly say async ASGI. If unsure, ask.
- **Consumer style:** always async `AIOConsumer`. The poll loop typically runs for hours or days and should never block the event loop.
- **Schema format:** JSON Schema. Schema Registry is always wired up; this skill does not generate a schemaless project.
- **Project directory:** `./payments-service/` (or derive from the user's wording).

## Step 3: Generate the project files

Create this layout in the chosen project directory:

```
<project-dir>/
├── producer.py
├── consumer.py
├── common.py
├── schemas/
│   └── value.schema.json
├── tests/
│   └── test_project.py
├── .env.example
├── pyproject.toml
└── README.md
```

The project uses [`uv`](https://docs.astral.sh/uv/) to manage the Python environment and dependencies — **not** `pip`, `venv`, `pipenv`, `poetry` or `conda`. Dependencies are declared in `pyproject.toml`; the environment is provisioned with `uv sync`; commands run via `uv run`. Generated documentation must reflect this throughout.

Use the templates in `references/`:

- `producer-template.py` for `producer.py`
- `consumer-template.py` for `consumer.py`
- `common-template.py` for `common.py`
- `tests-template.py` for `tests/test_project.py`

Write `schemas/value.schema.json` directly from the schema pulled in Step 1 — **do not regenerate or paraphrase it**. The whole point of MCP discovery is that the schema is the real one.

### `.env.example`

Populate with values from MCP discovery where possible. For a local Lenses CE setup:

```
KAFKA_ENV=local
BOOTSTRAP_SERVER=localhost:9092
TOPIC=<topic from discovery>
SCHEMA_REGISTRY_URL=http://localhost:8081
CLIENT_ID=payments-service
GROUP_ID=<suggested group from discovery>
```

For a remote managed cluster, replace `BOOTSTRAP_SERVER` and `SCHEMA_REGISTRY_URL` with whatever the MCP's dataset/cluster-metadata call returned, and add SASL credentials placeholders.

### `pyproject.toml`

Declare dependencies in a PEP 621 `[project]` table so `uv` can resolve and lock them. Do **not** also emit a `requirements.txt` — `pyproject.toml` is the single source of truth and `uv sync` produces a `uv.lock` next to it.

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = "Kafka producer and consumer scaffolded by kafka-python-client"
requires-python = ">=3.10"
dependencies = [
    "confluent-kafka[json,schema_registry]>=2.13.2",
    "jsonschema",
    "python-dotenv",
    "requests>=2.25.0",
    "httpx",
    "authlib",
    "cachetools",
    "attrs",
    "typing_extensions",
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Every third-party package imported by `producer.py`, `consumer.py` or `common.py` must appear in `[project].dependencies`. Test-only packages (`pytest`, `pytest-asyncio`) belong in the `dev` dependency group, installed automatically by `uv sync` and excluded from production installs via `uv sync --no-dev`. Include `pytest-asyncio` because the consumer is always async. The async Schema Registry client imports `httpx` and `authlib` at runtime even though they aren't declared as `confluent-kafka` dependencies — list them explicitly.

Either edit `pyproject.toml` by hand or generate it incrementally with `uv init --bare <project-dir>` followed by `uv add` calls, e.g.:

```bash
uv init --bare <project-dir>
cd <project-dir>
uv add "confluent-kafka[json,schema_registry]>=2.13.2" jsonschema python-dotenv "requests>=2.25.0" httpx authlib cachetools attrs typing_extensions
uv add --dev pytest pytest-asyncio
```

### `README.md`

A short README with: prerequisites ([`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed, Python 3.10+ — `uv` will fetch a managed interpreter automatically if none is present — and Docker if running Kafka locally), setup commands (`uv sync` to create `.venv` and install everything), how to register the schema if it isn't already (link to `schemas/value.schema.json`), how to run the producer and consumer with `uv run`, and how to run the tests with `uv run pytest`. The README must not reference `pip`, `python -m venv`, `source .venv/bin/activate` or `requirements.txt` — uv handles all of that.

### Rules the generated code must follow

Read `references/common-mistakes.md` for the full lookup table. The short version:

1. **One producer per process.** Construct it in `main()` and hand it to `produce()` as an argument. Never build a new one per call.
2. **Register the schema as its own step.** Configure the serializer with `auto.register.schemas=False` and `use.latest.version=True`, and publish the schema from a small `register_schema()` helper that calls `sr_client.register_schema()` directly and lets any exception bubble up.
3. **Use kwargs when constructing serializers.** `JSONSerializer`, `AvroSerializer`, and `ProtobufSerializer` do not share the same positional order in `confluent-kafka-python`. Passing `schema_str` and `schema_registry_client` by name on every call keeps the call site identical across formats and avoids the `TypeError: ... got multiple values for argument 'schema_registry_client'` surprise.
4. **Idempotent producer.** `enable.idempotence=true`, `acks=all`.
5. **Graceful shutdown.** Sync producer: `flush()` in `finally`. Async consumer: `unsubscribe()` then `close()`, both awaited.
6. **Key on entity ID.** Pass `key=<entity_id>.encode("utf-8")` for any per-entity event stream so partition ordering is preserved.
7. **Verify connectivity before running.** `AdminClient.list_topics()` for the broker, an HTTP GET on `/subjects` for the schema registry.

## Step 4: Run the tests

Use `uv` for the environment and `uv run` to execute commands inside it. `uv sync` creates `.venv/` next to `pyproject.toml`, resolves the dependencies declared there, writes a `uv.lock`, and installs everything in one step — no manual `python -m venv` or `pip install` needed.

```bash
cd <project-dir>
uv sync
uv run pytest tests/
```

If `uv` is missing on the user's machine, point them at the official installer (`curl -LsSf https://astral.sh/uv/install.sh | sh`) before continuing — do not fall back to `pip`.

If any test fails, fix the generated code (not the tests) until they pass.

## Step 5: Validation gate — chain into kafka-topic-audit and kafka-perf-review

This is what differentiates this skill from a one-shot scaffolder. After Step 4, automatically run two existing skills as a quality gate.

1. **kafka-topic-audit on the target topic.** Trigger by invoking the skill against the specific topic from Step 1. Surface any critical findings inline (RF=1 on a single-broker CE is expected — call it out but don't treat it as a blocker).
2. **kafka-perf-review on the generated code.** Trigger against the generated project directory. The generated `producer.py` and `consumer.py` should pass all of `enable.idempotence`, `acks=all`, `linger.ms` > 0, `compression.type` set, `max.poll.interval.ms` sensible, graceful shutdown present. If the audit finds anything, fix it in the generated code and re-run.

## Step 6: Hand back

Final message to the user must include:

- The project directory and a one-line description of what was generated
- The exact commands to run the producer and consumer (in two terminals)
- A one-paragraph summary of the validation-gate findings
- A note that the schema in `schemas/value.schema.json` came from the live cluster, not from inference

## Success Criteria

### Quantitative

- Triggers on 90% of "build a Python Kafka client" queries (test with 10-20 varied phrasings — see `references/test-cases.md`)
- Completes scaffold in under 15 MCP tool calls total
- 0 failed MCP calls per run (excluding genuine cluster-unreachable scenarios)
- Generated `pytest tests/` passes on first run > 80% of the time, after at most one self-fix
- Validation gate (Step 5) returns zero critical findings against the generated code

### Qualitative

- The user is asked at most one question before generation begins (the Step 2 confirmation), not a multi-turn interrogation
- The generated schema file matches the registered schema byte-for-byte (no paraphrasing)
- The generated code can be run end-to-end against the seeded local Lenses CE without further edits
- The hand-back message is self-contained — the user doesn't have to ask "okay, how do I run it?"

## Examples

### Example 1: Greenfield consumer with full MCP discovery (Lenses MCP attached)

User says: *"build me a Python consumer for the payment events on our staging Kafka"*

Actions:

1. Step 1: Lenses MCP is attached, so the agent uses its tools: `list_environments` → pick `staging`. `list_datasets(search="payment")` returns three topics. Three are presented to the user with their partition counts and message rates; the user picks `orders.payment.completed`. `get_dataset` pulls the registered JSON Schema. `get_topic_metadata` returns 12 partitions, RF=1. (With Confluent's MCP the equivalent calls would be `list_clusters` → `list_topics` → `get_schema` → `describe_topic` — same shape, different names. See `references/mcp-discovery.md`.)
2. Step 2: Recap and confirm. User confirms.
3. Step 3: Generate `producer.py`, `consumer.py`, `common.py`, `schemas/value.schema.json`, `tests/test_project.py`, `.env.example`, `pyproject.toml`, `README.md`.
4. Step 4: Tests pass.
5. Step 5: `kafka-topic-audit` flags RF=1 (expected on single-broker CE — passed through with a note). `kafka-perf-review` confirms idempotent producer, graceful shutdown, sensible `max.poll.interval.ms`.
6. Step 6: Hand back with run commands and the validation summary.

Result: A production-shaped project the user can run end-to-end in under five minutes, with a schema that exactly matches what's registered against the topic.

### Example 2: Adding a producer to an existing async Python service

User says: *"add a Kafka producer to my Quart service for `orders.payment.refunded`"* — the same flow applies to any async runtime: FastAPI / Starlette / Litestar / BlackSheep / Robyn / aiohttp / Sanic / Tornado / plain `asyncio` workers / ASGI-based services.

Actions:

1. Step 1: MCP discovery resolves the topic and schema. The agent detects the async framework signal (Quart) and selects `AIOProducer` as the producer style for Step 2.
2. Step 2: Recap notes async producer style, identifies the framework's startup/shutdown hooks (Quart: `@app.before_serving` / `@app.after_serving`; FastAPI: lifespan handler; Starlette: lifespan handler; aiohttp: `on_startup` / `on_cleanup`; Sanic: `@app.before_server_start` / `@app.before_server_stop`; Litestar: `on_startup` / `on_shutdown`; plain `asyncio` script: instantiate in `main()`, wrap in `try/finally`), and asks the user for the app's root file. User confirms.
3. Step 3: Instead of scaffolding from scratch, edit the user's existing app: add `common.py` if missing, instantiate `AIOProducer` once using the framework's startup hook, add a `produce()` helper that takes the producer as a parameter, ensure `await producer.flush()` then `await producer.close()` are wired into the framework's shutdown hook. Use `AsyncSchemaRegistryClient` (not the sync one) so registry calls don't block the event loop.
4. Step 4: Tests for the new helper pass.
5. Step 5: `kafka-perf-review` on the new code confirms async best practices (async SR client, `AsyncJSONSerializer`, kwargs-only construction, graceful shutdown wired to the framework's native lifecycle).
6. Step 6: Hand back with route / handler examples in the framework the user is actually using.

Result: Existing service gains a Kafka producer using its native startup/shutdown lifecycle, without losing its existing structure.

### Example 3: No Kafka MCP attached, fall back to hard gate

User says: *"scaffold a Python Kafka consumer for `orders.payment.completed`"* but no Kafka MCP server is connected (or only non-Kafka MCPs like Atlassian/GitHub are attached).

Actions:

1. Step 1: Agent enumerates attached MCPs, finds none Kafka-shaped. Skill notes the limitation.
2. Step 2: Hard gate asks the user for: bootstrap server, schema registry URL, the schema itself (paste or path), partition count (optional, defaults to 1), consumer group ID.
3. Step 3-6: Proceed normally with the user-supplied values.

Result: Scaffold still works, but the agent explicitly tells the user what was lost without MCP — exact phrasing: *"Without a Kafka MCP I can't verify the schema is what's actually registered against the topic. Run `kafka-schema-review` after you've registered this schema to confirm it matches."*

## Troubleshooting

### Topic-search returns zero results

Cause: Topic doesn't exist in this cluster, or the MCP hasn't indexed it yet, or the search keyword is too narrow.

Solution: Retry with a broader keyword. If still empty, use the MCP's full-list call (Lenses: `list_topics`; Confluent: `list_topics`; etc.) and let the user pick from the full list. If the topic genuinely doesn't exist, ask the user whether to create it via the MCP's topic-creation tool or abort.

### Topic exists but no registered schema

Cause: Topic exists but no schema is registered against `<topic>-value`.

Solution: Ask the user to either (a) provide a JSON Schema to register, or (b) confirm they want to scaffold a schema-less consumer (in which case fall back to `JSONDeserializer` without Schema Registry — but warn this is brittle and recommend registering a schema later).

### Generated tests fail on `AIOProducer` / `AIOConsumer` mocks

Cause: `pytest-asyncio` isn't installed, or the test fixture is sync.

Solution: Confirm `pytest-asyncio` is in `pyproject.toml` under `[dependency-groups].dev`, re-run `uv sync`, and ensure the test functions are decorated with `@pytest.mark.asyncio`.

### `TypeError: ... got multiple values for argument 'schema_registry_client'`

Cause: Serializer/deserializer constructed with positional arguments. JSON, Avro and Protobuf classes have different positional signatures.

Solution: See `references/common-mistakes.md` row 8. Always pass `schema_str` and `schema_registry_client` as keyword arguments.

### Validation gate (Step 5) reports critical findings on the generated code

Cause: The skill version drifted from the audit thresholds in `kafka-perf-review`.

Solution: Fix the generated code to satisfy the audit (the audit is the source of truth for "what good looks like" in this repo) and re-run the validation gate. If the audit threshold itself seems wrong, raise a PR against `kafka-perf-review/references/`.

## Output Format

When handing back in Step 6, use this structure:

```
## Project scaffolded

Generated at: <project-dir>/

### Files written
- producer.py
- consumer.py
- common.py
- schemas/value.schema.json   (pulled from registry — matches live schema)
- tests/test_project.py
- .env.example
- pyproject.toml              (uv-managed; uv.lock generated by `uv sync`)
- README.md

### Run it

# One-off setup (creates .venv and installs everything via uv)
cd <project-dir>
uv sync

# Terminal 1 — producer
cd <project-dir>
uv run python producer.py

# Terminal 2 — consumer
cd <project-dir>
uv run python consumer.py

### Validation gate

kafka-topic-audit findings:
- [topic-name] <severity> <finding>

kafka-perf-review findings:
- [file:line] <severity> <finding>

### Notes
- Schema in `schemas/value.schema.json` was pulled from `<topic>-value` in the registry, not inferred.
- Consumer group ID: `<group-id>` (unique, no collision).
- Idempotent producer enabled, graceful shutdown implemented.
```
