---
name: kafka-connector-review
description: Review Kafka Connect connector configurations for common misconfigurations using the Lenses MCP server. Checks error handling, DLQ setup, converters, transforms, task count and task health. Use when user says "review connectors", "check connector configs", "why is my connector failing" or asks about Kafka Connect configuration. Do NOT use for creating, deploying or controlling connectors.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, mcp__Lenses__list_kafka_connectors, mcp__Lenses__get_kafka_connector_target_definition, mcp__Lenses__validate_connector_configuration
argument-hint: "[required: environment name] [optional: connector name to focus on]"
compatibility: Recommended - the Lenses MCP server (lenses-mcp) connected and configured with a valid environment. Any Kafka MCP that exposes an equivalent Kafka Connect tool surface (list_connectors, get_connector, etc.) will also work; without an MCP server, the skill falls back to codebase-only inspection and skips live-cluster checks.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: lenses-mcp
  category: mcp-enhancement
  approach: problem-first
  patterns: sequential-workflow, domain-intelligence
  tags: [kafka, connect, connectors, configuration, error-handling]
---

# Kafka Connect Configuration Review

Reviews Kafka Connect connector configurations for common misconfigurations. Connectors are defined as JSON/YAML and are entirely language-agnostic.

Target environment: $ARGUMENTS

## Workflow

Copy this checklist and track your progress:

```
Connector Review Progress:
- [ ] Step 1: List all connectors
- [ ] Step 2: Inspect each connector's configuration
- [ ] Step 3: Validate configurations against plugin schemas
- [ ] Step 4: Audit for common misconfigurations
- [ ] Step 5: Generate report
```

1. **List all connectors** with status and task states
2. **Inspect each connector's configuration** in detail
3. **Validate configurations** against plugin schemas
4. **Audit for common misconfigurations**
5. **Report findings** with current and recommended configs

## Step 1: List All Connectors

Use the Lenses MCP `list_kafka_connectors` tool to get all connectors with:
- Connector name, class and type (source/sink)
- Status (RUNNING, PAUSED, FAILED, UNASSIGNED)
- Task states and count
- Cluster info

Flag immediately:
- **Critical**: Connectors in FAILED state
- **Critical**: Tasks in FAILED state
- **Warning**: Connectors in PAUSED state with no obvious reason

Expected output: List of all connectors with name, class, status and task states.

**Validation**: If no connectors are returned, report that no Connect cluster is configured and stop.

## Step 2: Inspect Configurations

Use the Lenses MCP `get_kafka_connector_target_definition` tool to get the full configuration YAML for each connector.

## Step 3: Validate Configurations

Use the Lenses MCP `validate_connector_configuration` tool to validate each connector's config against its plugin's schema. This catches:
- Missing required configuration fields
- Invalid configuration values
- Type mismatches

## Step 4: Audit Common Misconfigurations

### Error Handling
- **Critical**: `errors.tolerance=all` without `errors.deadletterqueue.topic.name` (silently drops messages)
- **Warning**: Missing `errors.tolerance` (defaults to `none`, connector stops on any error)
- **Warning**: Missing `errors.log.enable=true` (errors not logged)
- **Suggestion**: Add `errors.deadletterqueue.context.headers.enable=true` for richer DLQ metadata

### Converters
- **Warning**: `key.converter` or `value.converter` mismatch with topic serialisation format
- **Warning**: Using `org.apache.kafka.connect.storage.StringConverter` for structured data (should use Avro/JSON/Protobuf converter)
- **Warning**: Missing `schemas.enable` setting where schemas are expected

### Transforms (SMTs)
- **Warning**: Complex transform chains (> 3 SMTs) that may be hard to debug
- **Suggestion**: Consider Kafka Streams or ksqlDB for complex transformations
- Verify transform class names are valid and in the correct order

### Task Count
- **Warning**: `tasks.max=1` on high-throughput connectors (limits parallelism)
- **Suggestion**: Source connectors - `tasks.max` should align with source partitioning
- **Suggestion**: Sink connectors - `tasks.max` should align with topic partition count

### Connection and Retry
- **Warning**: Missing retry configuration for connectors that interact with external systems
- **Warning**: Missing connection timeout settings
- **Suggestion**: Set explicit `consumer.override.*` or `producer.override.*` for performance tuning

### Naming Conventions
- **Suggestion**: Connector names should follow a consistent pattern (e.g., `{source/sink}-{system}-{entity}`)

## Success Criteria

### Quantitative
- Triggers on 90% of connector-related queries (test with 10-20 varied phrasings)
- Completes review in under 10 MCP tool calls
- Catches 100% of validation errors reported by the plugin schema

### Qualitative
- Failed connectors are flagged immediately in the status overview
- Error handling gaps (missing DLQ, silent drops) are always identified
- Report is useful for both connector operators and developers

## Examples

### Example 1: Routine connector review

User says: "Review all connectors in staging"

Actions:
1. List all connectors with status
2. Inspect and validate each connector's configuration
3. Audit for common misconfigurations
Result: Full report covering all connectors with prioritised findings

### Example 2: Investigating a failed connector

User says: "My sink connector is failing, can you check why?"

Actions:
1. List connectors and identify those in FAILED state
2. Get the full configuration for the failed connector
3. Validate config against plugin schema
4. Check for common issues (DLQ, converters, error handling)
Result: Diagnosis of the specific failure with remediation steps

### Example 3: Single connector deep dive

User says: "Review the config for the elasticsearch-sink connector"

Actions:
1. Fetch the target definition for the named connector
2. Validate against its plugin schema
3. Audit error handling, converters, task count
Result: Focused report on a single connector

## Troubleshooting

### No connectors returned
Cause: No Kafka Connect cluster is configured in the environment or no connectors are deployed.
Solution: Verify that a Connect cluster exists via Lenses UI. Check `get_deployment_targets` for available Connect clusters.

### Validation fails with unknown plugin
Cause: The connector plugin class is not installed on the Connect cluster.
Solution: Report the missing plugin. This is a deployment issue, not a configuration issue.

### Connector shows RUNNING but tasks are FAILED
Cause: The connector framework is running but individual tasks have encountered errors.
Solution: Check each task's status. Common causes include authentication failures, network issues or schema mismatches with the external system.

## Output Format

```
## Connector Review Report

### Environment: {name}

### Connector Status Overview
| Connector | Class | Status | Tasks | Failed Tasks |
|-----------|-------|--------|-------|-------------|
| name | class | RUNNING | 3/3 | 0 |

### Critical (must fix)
- [connector-name] Description of the issue
  Current: {current config} | Recommended: {recommended config}

### Warning (should fix)
- [connector-name] Description of the issue
  Current: {current config} | Recommended: {recommended config}

### Validation Errors
- [connector-name] {field}: {validation error message}

### Suggestion (consider improving)
- [connector-name] Description of the suggestion
  Recommendation: {how to improve}

### Summary
- X connectors reviewed
- Y critical issues found
- Z warnings found
- Failed connectors: N
- Failed tasks: M
```
