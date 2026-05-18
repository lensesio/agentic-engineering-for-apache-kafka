# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger

- "Build me a Python consumer for the payment events on our staging Kafka"
- "Scaffold a Kafka client in Python for `orders.payment.completed`"
- "Add a Kafka producer to my Python service"
- "Write a Python producer and consumer for our orders topic"
- "Consume from `orders.payment.completed` in Python"
- "I need to publish to Kafka from a FastAPI app"
- "Add a Kafka producer to my Quart service"
- "Wire Kafka into my Litestar service"
- "Integrate Kafka with my aiohttp worker"
- "Add a Kafka producer to my asyncio task runner"
- "Generate a confluent-kafka-python project for the payments topic"
- "Create a Kafka client to read events into my Django service"
- "Add a consumer to my existing Python app that reads from Kafka"
- "Build a script that produces test messages to a Kafka topic"

### Should NOT Trigger

- "Audit my Kafka topics" (use kafka-topic-audit)
- "Review my consumer lag" (use kafka-consumer-lag)
- "Check producer performance configs" (use kafka-perf-review)
- "Review this schema change for compatibility" (use kafka-schema-review)
- "Configure a Kafka Connect connector" (use kafka-connector-review)
- "Write a Kafka producer in Java" (wrong language)
- "Write a Kafka producer in Go" (wrong language)
- "Set up a Kafka cluster" (out of scope — infrastructure)
- "What is Apache Kafka?" (general explanation, no scaffold needed)
- "How do I install confluent-kafka?" (installation Q&A, no scaffold needed)

## Functional Tests

### Test 1: Greenfield scaffold with full MCP discovery

**Given**: Local Lenses CE with `orders.payment.completed` topic (12 partitions, JSON Schema registered with 6 required fields), a background producer publishing ~1 msg/sec, and the Lenses MCP server attached.

**When**: User says *"build a Python consumer for the payment events on staging"*.

**Then**:

- Step 1 makes at most 6 MCP calls: `list_environments`, `list_datasets(search="payment")`, `get_dataset`, `get_topic_metadata`, `list_consumer_groups_by_topic`.
- The recap in Step 2 includes topic name, 12 partitions, RF=1, 6 required fields, suggested group ID, and the producer-style default.
- The skill stops and waits after the recap.
- After user confirms, Step 3 generates exactly 8 files: `producer.py`, `consumer.py`, `common.py`, `schemas/value.schema.json`, `tests/test_project.py`, `.env.example`, `pyproject.toml`, `README.md`. **No** `requirements.txt` is generated — the project is `uv`-managed.
- `schemas/value.schema.json` matches the registered schema byte-for-byte.
- `pyproject.toml` declares all runtime deps under `[project].dependencies` and test deps under `[dependency-groups].dev`; `uv sync` succeeds and produces a `uv.lock`.
- Step 4: `uv run pytest tests/` passes on first run.
- Step 5: `kafka-topic-audit` runs and reports RF=1 as a warning (expected). `kafka-perf-review` reports zero critical findings on the generated code.
- Step 6 hand-back includes the two-terminal run commands and the validation-gate summary.

### Test 2: User specifies async (any async Python framework)

**Given**: Same cluster state as Test 1. User has an existing async Python app at `./payments-api/main.py`. Run this test against three framework variants in rotation: FastAPI, Quart, and aiohttp.

**When**: User says *"add a Kafka producer to my `<framework>` service for `orders.payment.refunded`"*.

**Then**:

- Step 1 discovers `orders.payment.refunded` (3 partitions, different schema shape).
- Step 2 recap notes async producer style (`AIOProducer`) and identifies the chosen framework's startup/shutdown hooks correctly (FastAPI: lifespan; Quart: `@app.before_serving` / `@app.after_serving`; aiohttp: `on_startup` / `on_cleanup`).
- Step 3 modifies `payments-api/main.py` to add `AIOProducer` at startup, a `produce()` helper, and a shutdown handler — does not scaffold a new project.
- Generated tests cover the new helper, not the whole app.
- Validation gate confirms async best practices (`AsyncSchemaRegistryClient`, `AsyncJSONSerializer`, kwargs-only construction).

### Test 3: MCP unavailable, hard-gate fallback

**Given**: Lenses MCP server not connected in Cursor.

**When**: User says *"scaffold a Python consumer for `orders.payment.completed`"*.

**Then**:

- Step 1 fails fast on `list_environments`.
- The skill explicitly tells the user MCP is unavailable.
- Step 2 hard gate asks for: bootstrap server, schema registry URL, topic (already supplied), schema (paste or path), consumer group ID.
- After user provides values, Steps 3–4 proceed normally.
- Step 5 still runs the validation gate but `kafka-topic-audit` runs in codebase-only mode (no cluster) — finding is a single suggestion to register the schema after deploy.
- Step 6 hand-back explicitly states: *"Without MCP I couldn't verify the schema matches the live registered version."*

### Test 4: Multiple candidate topics — must ask

**Given**: Cluster has three payment topics (`completed`, `failed`, `refunded`).

**When**: User says *"build a consumer for payment events"*.

**Then**:

- `list_datasets(search="payment")` returns three results.
- The skill **does not** silently pick the first match.
- The skill presents the three candidates with partition counts and the first 3 field names each.
- The skill waits for the user to choose.
- After the user picks one, proceeds normally from Step 3.

### Test 5: No schema registered

**Given**: Topic `events.raw` exists but no schema is registered against `events.raw-value`.

**When**: User says *"scaffold a consumer for `events.raw`"*.

**Then**:

- Step 1 discovers the topic but `get_dataset` returns empty `fields`.
- The skill asks the user: paste a schema, infer from sample messages (`execute_sql`), or proceed schema-less (warns this is brittle).
- The skill does **not** invent a schema silently.

### Test 6: Schema is Avro, not JSON

**Given**: Topic has an Avro schema registered.

**When**: User asks to scaffold a client.

**Then**:

- Step 1's `get_dataset` returns a schema with `"type": "record"`.
- The skill detects Avro and tells the user this skill only scaffolds JSON-Schema-backed clients.
- Offers (a) abort, or (b) convert to JSON Schema with lossy union handling.

### Test 7: Producer-instance-reuse anti-pattern caught by tests

**Given**: A generated `producer.py` that mistakenly instantiates `Producer()` inside `produce()`.

**When**: `uv run pytest tests/` runs.

**Then**:

- `test_producer_produce_uses_passed_instance` fails.
- The skill fixes the code (moves Producer construction to `main()`) and re-runs.
- After fix, all tests pass.

### Test 8: Generated `pytest` passes against the seeded cluster

**Given**: The seeded local Lenses CE per `webinar/SEEDING.md`.

**When**: A fresh scaffold runs end-to-end (Steps 1–6).

**Then**:

- `uv sync` succeeds with no resolver errors and produces a `uv.lock`.
- `uv run pytest tests/` passes without modification.
- `uv run python producer.py` publishes successfully to `orders.payment.completed`.
- `uv run python consumer.py` reads and deserializes the producer's output correctly.
- The end-to-end happy path runs in under three minutes wall-clock (the webinar money shot).

## Performance Baseline

Measured against a generic agent (no skill) producing the same scaffold from the same prompt.

| Metric                          | Without Skill | With Skill |
| ------------------------------- | ------------- | ---------- |
| Back-and-forth messages         | 12–18         | 1–2        |
| User-asked clarification turns  | 5–8           | 0–1        |
| Files generated correctly       | 4–6 / 8       | 8 / 8      |
| Schema matches registered one   | Never (hallucinated) | Always (pulled via MCP) |
| Test pass rate on first run     | 20–40 %       | > 80 %     |
| Validation-gate critical findings on generated code | 3–6 | 0 |
| Time from prompt to working `python consumer.py` | 15–30 min | < 5 min |
| Common-mistake instances triggered | 4–8 / 20      | 0 / 20     |

## How to run these tests

The triggering tests are manual — paste each phrase into Cursor with the skill installed and confirm whether the skill auto-loads. Track results in a spreadsheet over 2–3 review rounds.

The functional tests require the seeded local Lenses CE per `webinar/SEEDING.md`. Run each end-to-end against the cluster and check the assertions.

The performance baseline numbers come from running the same prompt twice — once with the skill disabled, once enabled — and timing each turn with a stopwatch. Re-baseline after every major skill version bump.
