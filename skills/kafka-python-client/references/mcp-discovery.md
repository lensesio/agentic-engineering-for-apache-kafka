# MCP discovery sequence

How to use **any attached Kafka MCP server** to discover everything the scaffold needs about the target topic, **before** asking the user. The whole point of this skill is to eliminate "what fields are in your message?" — the cluster already knows.

This skill is **MCP-agnostic**: it probes for the capability (e.g. "list topics matching a keyword") rather than calling fixed tool names. Tool names vary per vendor. The reference implementation is tested against the [Lenses MCP server](https://github.com/lensesio/lenses-mcp); other Kafka MCPs (Confluent's, Aiven's, custom) work the same way with different identifiers.

## The capability map

Six discovery capabilities the skill needs. For each, the agent should look at the attached MCP servers in the session, find a tool that matches the capability, and invoke it. If multiple Kafka MCPs are attached, prefer the one the user mentioned most recently (or the first `RUNNING` one if they didn't say).

| # | Capability | Lenses MCP (`mcp__Lenses__*`) | Confluent MCP (`mcp__Confluent__*` typical) | Raw Kafka admin MCP (typical) | Bare Schema Registry HTTP |
|---|---|---|---|---|---|
| 1 | List environments / clusters | `list_environments()` | `list_clusters()` | (single cluster — skip) | n/a |
| 2 | Search topics by keyword | `list_datasets(search="<kw>", connections=["kafka"])` | `list_topics(cluster_id=...)` then filter | `list_topics()` then filter | n/a |
| 3 | Fetch topic + registered schema | `get_dataset(environment, connection="kafka", dataset="<t>")` | `describe_topic(...)` + `get_schema(subject="<t>-value")` | `describe_topic(...)` + curl `/subjects/<t>-value/versions/latest` | curl `/subjects/<t>-value/versions/latest` |
| 4 | Read partition count and RF | `get_topic_metadata(environment, topic="<t>")` | `describe_topic(...)` returns it | `describe_topic(...)` returns it | n/a |
| 5 | Per-partition message distribution (optional) | `get_topic_partitions(environment, topic="<t>")` | `describe_topic(...)` may include | `describe_topic(...)` may include | n/a |
| 6 | List consumer groups on this topic | `list_consumer_groups_by_topic(environment, topic="<t>")` | `list_consumer_groups(cluster_id=...)` then filter | `list_consumer_groups()` then filter | n/a |

If the attached MCP exposes a tool with a similar name and an obviously matching purpose, **try it**. If unsure, ask the user *"I see `mcp__<server>__<tool>` attached — is that the right Kafka MCP for this task?"* before invoking it.

## Procedure

Run capabilities **1 → 6** in order. Stop as soon as you have enough to recap in Step 2 of the workflow.

### 1. Identify the attached Kafka MCP

Enumerate available MCP servers. A server is "Kafka-shaped" if it exposes any of: a topic-list tool, a topic-describe tool, a consumer-group tool, or a Kafka schema tool. Common identifying prefixes:

- `mcp__Lenses__*` — Lenses MCP (reference implementation)
- `mcp__LensesCE__*` — Lenses Community Edition local container
- `mcp__Confluent__*` — Confluent's MCP server
- `mcp__Aiven__*`, `mcp__AivenLabs__*` — Aiven for Apache Kafka MCP
- `mcp__RedpandaConsole__*` — Redpanda's MCP (if available)
- `mcp__kafka_admin__*`, `mcp__kafka__*` — generic / custom servers

If **multiple** Kafka MCPs are attached, prefer (in order): the one whose server prefix matches `$ARGUMENTS` keywords, then the one the user mentioned in the prompt, then the first `RUNNING` one.

If **zero** Kafka MCPs are attached, skip directly to the "No Kafka MCP attached" fallback below.

### 2. Discover the environment / cluster

Use capability 1 from the map. Resolve to a single `<environment>` or `<cluster_id>` value.

- If `$ARGUMENTS` named an environment, verify it appears in the list and is reachable.
- If not supplied, pick the first reachable one. If there are multiple, **ask the user** — don't guess.

Capture: `cluster_label` (string, used in the recap), `cluster_handle` (whatever the MCP needs as a key for subsequent calls — environment name, cluster id, etc.).

### 3. Search for candidate topics

Use capability 2 from the map. The keyword should come from any noun in the user's prompt (e.g. "payment", "order", "transaction").

- If exactly one result: it's the target topic.
- If multiple results: list them to the user with their partition counts and message rates (if cheap to fetch), ask which one. Do **not** pick the first match silently.
- If zero results: retry with a broader keyword, then with no filter. If still empty, the topic doesn't exist — see "Topic doesn't exist" in the fallbacks section.

Capture: `topic` (string, the user-confirmed topic name).

### 4. Fetch the topic with its registered schema

Use capability 3 from the map. Different MCPs return this differently:

- **Lenses-style** (`get_dataset`): one call returns topic metadata + `fields` (structured) + `schema` / `valueSchemaRaw` (raw JSON string).
- **Confluent-style** (`describe_topic` + `get_schema`): two calls. Get topic metadata from `describe_topic`, then `get_schema(subject="<topic>-value")` for the raw schema.
- **Bare schema-registry-HTTP** (rarely as MCP, more as a CLI fallback): `curl http://<sr>/subjects/<topic>-value/versions/latest` returns `{"schema": "...", "schemaType": "JSON"}`.

**Whatever shape the response takes, capture the raw schema string verbatim.** Use it byte-for-byte in `schemas/value.schema.json`. Do not paraphrase, reformat, or "fix" it — even if you spot what looks like a bug. The registered schema is the source of truth for what producers are sending today; "fixing" it silently breaks every other consumer.

If the topic exists but the response has no schema (empty `fields`, null `valueSchemaRaw`, `404` on `/subjects/<t>-value`), see "No schema registered" in the fallbacks.

Capture: `valueSchemaJson` (string, raw JSON Schema), `valueSchemaFields` (list of `{name, type}` if the MCP returned it structured).

### 5. Read partition count and replication factor

Use capability 4 from the map. With Lenses this is a separate `get_topic_metadata` call; with Confluent/raw admin MCPs it's typically returned by `describe_topic` in step 4 — in which case you can skip the extra call.

Capture: `partitions` (int), `replicationFactor` (int), `configs` (dict — retention, cleanup policy, compression, etc.).

### 6. Suggest a consumer group ID

Use capability 6 from the map to fetch existing consumer groups on the topic. Then propose a non-colliding `GROUP_ID`:

- Format: `<service-name>-<8-char-random>` (e.g. `payments-service-a3f8c2e1`).
- If the user mentioned a service name in the prompt, use it as the prefix.
- If a group with the proposed name already exists, regenerate the suffix.

Capture: `existingGroupIds` (list of strings), `suggestedGroupId` (string).

## Recap shape for Step 2

After running capabilities 1–6, the recap message to the user should look like:

```
Discovered via <MCP server display name>:
- Cluster:          <cluster_label>
- Topic:            <topic>
- Partitions:       <partitions>
- Replication:      <replicationFactor>
- Retention:        <configs["retention.ms"] in human-readable form>
- Value schema:     JSON Schema with <N> required fields + <M> optional (pulled from registry)
- Suggested group:  <suggestedGroupId> (no collision with <count> existing groups)

I'll generate a Python project with these defaults:
- Producer style:   <sync or async, based on context>
- Schema:           JSON Schema (registry-backed)
- Tests:            pytest with mocked Producer/AIOConsumer
- Project dir:      <inferred from user wording, e.g. ./payments-service/>

Confirm and I'll generate, or correct anything above.
```

Then **stop and wait** for the user's reply. Do not generate files in the same turn as the recap.

## Fallbacks

### No Kafka MCP attached at all

Cause: User has no MCP server attached, or only non-Kafka MCPs (Atlassian, GitHub, AWS, etc.).

Action: Skip the procedure entirely. Fall through to the hard gate in the main `SKILL.md`, asking the user for: bootstrap server, schema registry URL, topic name, the schema itself (paste or path), consumer group ID. Note explicitly in the final hand-back: *"Without a Kafka MCP I couldn't verify the schema is what's actually registered against the topic. Run `kafka-schema-review` after registration to confirm."*

### MCP attached but list-environments returns empty

Cause: MCP server is reachable but has no configured clusters / environments, or auth failed.

Action: Stop and tell the user *"`<MCP server>` is connected but reports no clusters / environments. Check the server's configuration and credentials."* Then offer to proceed via the no-MCP fallback above.

### Topic doesn't exist in this cluster

Cause: The user named or implied a topic that isn't in the cluster.

Action: Don't auto-create. Ask the user *"Topic `<name>` doesn't exist in this cluster. Want me to create it now (I'll need partition count and a schema), or did you mean one of these existing topics: `<top 5 alphabetically closest>`?"* If they want to create it, use the MCP's topic-creation tool (Lenses: `create_topic_with_schema`; Confluent: `create_topic` + `register_schema`; etc.) and then resume from capability 5.

### No schema registered for the topic

Cause: Topic exists but no schema is registered against `<topic>-value`.

Action: Ask the user *"`<topic>` exists with `<N>` partitions, but no value schema is registered. Want to (a) paste a JSON Schema for me to register and use, (b) infer one from a sample message and register that, or (c) scaffold without Schema Registry (brittle — not recommended)?"* For option (b), use the MCP's message-sampling tool if available (Lenses: `execute_sql` with `SELECT * FROM <topic> LIMIT 5`) to pull samples and propose a schema from their shape.

### Multiple candidate topics from the search

Cause: The keyword is ambiguous (e.g. "payment" matched three payment topics).

Action: List all matches with their partition counts and the first 3 schema field names so the user can pick by shape. Format:

```
Found 3 candidate topics:
  1. orders.payment.completed  (12 partitions, fields: payment_id, order_id, amount, ...)
  2. orders.payment.failed     ( 3 partitions, fields: payment_id, order_id, customer_id, ...)
  3. orders.payment.refunded   ( 3 partitions, fields: payment_id, original_payment_id, order_id, ...)

Which one?
```

### Schema is registered but not JSON (Avro / Protobuf)

Cause: Topic has an Avro or Protobuf schema instead of JSON Schema.

Action: Detect the schema type (Avro records start with `{"type": "record", ...}`; Protobuf starts with `syntax = "proto3";`). Tell the user *"Schema is `<format>`, not JSON. This skill only scaffolds JSON-Schema-backed clients. Want me to (a) abort, or (b) convert to JSON Schema (lossy for Avro unions and Protobuf one-of)?"*

### Tool name guess didn't match

Cause: You tried a likely tool name (e.g. `list_topics`) and the MCP returned "tool not found".

Action: Inspect the actual tool list from that MCP server (every MCP exposes a tool-listing capability). Find the closest functional match. If genuinely no match exists for a capability, treat that capability as unavailable and fall through to asking the user for the corresponding value.

## Performance budget

The full discovery sequence should complete in **at most 6 MCP tool calls** for the happy path on a Lenses-style MCP (one call per capability). On a Confluent-style MCP with `describe_topic` consolidating capabilities 4 and 5 it might be 5 calls. If you hit 10+ MCP calls discovering one topic, you're doing something wrong — stop and ask the user directly instead.

## What the agent must NOT do

- **Do not paraphrase the schema.** The raw JSON from the registry is the source of truth. Copy it byte-for-byte into `schemas/value.schema.json`.
- **Do not guess between multiple candidate topics.** Ask the user.
- **Do not silently fall back to inventing a schema** if the topic has none registered. Ask the user how to proceed.
- **Do not skip the recap in Step 2** even when MCP discovery looks complete. The user's intent might differ from what the cluster suggests (e.g. they want to consume from production, not staging).
- **Do not invoke MCP tools that aren't obviously Kafka-related.** If you only see `mcp__Atlassian__*` and `mcp__GitHub__*` attached, fall through to the no-MCP fallback — don't try to creatively use a JIRA tool for Kafka discovery.
- **Do not invoke destructive MCP tools.** The discovery procedure is read-only. Tools like `delete_topic`, `update_topic_config`, `delete_consumer_group` are never called during discovery — even if they're whitelisted.
