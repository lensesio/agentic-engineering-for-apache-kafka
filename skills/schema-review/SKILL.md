---
name: schema-review
description: Review Kafka schema changes (Avro, Protobuf, JSON Schema) for compatibility and evolution best practices using the Lenses MCP server. Detects breaking changes, missing defaults, schema drift and naming issues. Use when user says "review schema changes", "check schema compatibility", "will this schema break consumers" or asks about schema evolution. Do NOT use for creating new schemas from scratch or registering them in the cluster.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, mcp__Lenses__list_topic_metadata, mcp__Lenses__get_topic_metadata, mcp__Lenses__get_dataset, mcp__Lenses__list_datasets, mcp__Lenses__execute_sql
argument-hint: "[required: environment name] [optional: path to schema files]"
compatibility: Recommended - the Lenses MCP server (lenses-mcp) connected and configured with a valid environment. Any Kafka MCP that exposes an equivalent Schema Registry tool surface will also work; without an MCP server, the skill falls back to codebase-only inspection and skips live-cluster checks.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: lenses-mcp
  category: mcp-enhancement
  approach: problem-first
  patterns: context-aware-selection, domain-intelligence
  tags: [kafka, schema, avro, protobuf, compatibility]
---

# Kafka Schema Evolution Review

Reviews schema changes for compatibility and evolution best practices. A single breaking schema change can take down every consumer of a topic.

Target environment: $ARGUMENTS

## Workflow

Copy this checklist and track your progress:

```
Schema Review Progress:
- [ ] Step 1: Fetch registered schemas
- [ ] Step 2: Scan codebase for schema files
- [ ] Step 3: Detect breaking changes
- [ ] Step 4: Check schema quality
- [ ] Step 5: Check schema drift
- [ ] Step 6: Generate report
```

1. **Fetch registered schemas** from the live cluster via Lenses MCP
2. **Scan codebase** for schema definition files (see `references/compatibility-rules.md` for file types)
3. **Detect breaking changes** against compatibility rules in `references/compatibility-rules.md`
4. **Check schema quality** against best practices
5. **Check schema drift** between repo and cluster
6. **Report findings** with migration guidance

## Step 1: Fetch Registered Schemas

Use Lenses MCP tools to get the current state of schemas in the cluster:

- `list_topic_metadata` - get all schemas registered against topics (key and value)
- `get_topic_metadata` - get the current schema for a specific topic
- `get_dataset` - get dataset field-level details, policies and governance metadata
- `list_datasets` with `schema_format` filter - find all topics using a given format (AVRO, JSON, PROTOBUF)

Expected output: Map of topics to their registered schemas (key and value) with format and version info.

**Validation**: If no schemas are registered, note this as a governance gap and proceed with codebase-only analysis.

## Step 2: Codebase Inspection

Search the codebase for schema definition files. Consult `references/compatibility-rules.md` for the full list of file types and search patterns.

Use `git diff` to identify recently changed schema files if reviewing a PR.

## Step 3: Compatibility Checks

For each schema change, evaluate against the compatibility rules in `references/compatibility-rules.md`. Check backward, forward and full compatibility depending on the topic's configured compatibility level.

## Step 4: Schema Quality Checks

Apply the quality checks from `references/compatibility-rules.md`:
- Fields without documentation annotations
- Missing default values on optional fields
- Inconsistent naming conventions
- Unused or overly generic field names

## Step 5: Schema Drift Detection

Compare schema files in the repo against schemas registered in the cluster:

- Use `execute_sql` to sample live data and verify it matches the expected schema
- Flag schemas in the repo that differ from what's registered
- Flag topics with registered schemas that have no corresponding file in the repo

## Success Criteria

### Quantitative
- Triggers on 90% of schema-related queries (test with 10-20 varied phrasings)
- Completes review in under 12 tool calls (MCP + codebase search)
- 0 false positives on breaking change detection

### Qualitative
- Breaking changes include clear migration guidance
- Schema drift is reported with both repo and cluster versions
- Quality findings are actionable without external documentation

## Examples

### Example 1: Pre-merge schema review

User says: "Review the schema changes in this PR"

Actions:
1. Run `git diff` to find changed `.avsc`, `.proto` or `.json` schema files
2. Fetch the currently registered schema from the cluster via Lenses MCP
3. Evaluate each change against compatibility rules
Result: Report listing any breaking changes with migration guidance

### Example 2: Full schema audit

User says: "Audit all schemas in the staging environment"

Actions:
1. Fetch all registered schemas via `list_topic_metadata`
2. Scan the codebase for schema files
3. Check for drift between repo and cluster
4. Run quality checks on all schemas
Result: Comprehensive report covering compatibility, quality and drift

### Example 3: Investigating a consumer failure

User says: "Consumers are failing to deserialise messages from orders.payment.completed"

Actions:
1. Fetch the registered schema for that topic via `get_topic_metadata`
2. Sample live data with `execute_sql` to see actual message format
3. Compare against the schema file in the repo
Result: Diagnosis of schema mismatch with remediation steps

## Troubleshooting

### No schemas registered in the cluster
Cause: Schema Registry is not configured or topics use schemaless formats (plain JSON, CSV).
Solution: This is a valid finding - report it as a governance gap rather than an error. Recommend adding schema registration.

### Schema drift detected but intentional
Cause: The cluster schema was updated independently of the repo (e.g., via Schema Registry UI).
Solution: Report the drift and recommend syncing the repo to match the cluster as the source of truth.

### Cannot sample data with execute_sql
Cause: Topic is empty, permissions are restricted or the topic uses an unsupported format.
Solution: Note the limitation in the report. Use `get_topic_metadata` as a fallback for schema information.

## Output Format

```
## Schema Review Report

### Environment: {name}

### Breaking Changes (must fix before merge)
- [schema-file] Description of the breaking change
  Affected topics: {list}
  Migration: {guidance}

### Compatibility Warnings
- [schema-file] Description of the issue
  Recommendation: How to fix it

### Schema Quality
- [schema-file:field] Description of the quality issue
  Recommendation: How to improve it

### Schema Drift
- [topic-name] Schema in repo differs from registered schema
  Repo version: {summary} | Cluster version: {summary}

### Summary
- X breaking changes found
- Y compatibility warnings found
- Z quality issues found
- Schema files scanned: N
- Topics with drift: M
```
