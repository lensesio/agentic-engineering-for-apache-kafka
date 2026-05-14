---
name: topic-audit
description: Audit all Kafka topic configurations against production best practices using the Lenses MCP server. Checks replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata. Use when user says "audit my topics", "check topic configs", "topic health check" or asks about retention, replication or partition settings. Do NOT use for creating, deleting or modifying topics.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, mcp__Lenses__check_environment_health, mcp__Lenses__list_topics, mcp__Lenses__get_topic, mcp__Lenses__get_topic_broker_configs, mcp__Lenses__get_topic_partitions, mcp__Lenses__list_topic_metadata, mcp__Lenses__list_consumer_groups_by_topic, mcp__Lenses__list_datasets
argument-hint: "[required: environment name]"
compatibility: Requires the Lenses MCP server (lenses-mcp) connected and configured with a valid environment.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: lenses-mcp
  category: mcp-enhancement
  approach: problem-first
  patterns: sequential-workflow, domain-intelligence
  tags: [kafka, topics, audit, configuration, best-practices]
---

# Kafka Topic Configuration Audit

Audits all topic configurations against production best practices. Misconfigured topics are the #1 cause of Kafka data loss - engineers create topics and forget to tune them.

Target environment: $ARGUMENTS

## Workflow

Copy this checklist and track your progress:

```
Audit Progress:
- [ ] Step 1: Check environment health
- [ ] Step 2: Fetch all topics
- [ ] Step 3: Audit configurations against best practices
- [ ] Step 4: Check metadata completeness
- [ ] Step 5: Detect orphaned topics
- [ ] Step 6: Run consistency checks
- [ ] Step 7: Generate report
```

1. **Check environment health** for a high-level summary
2. **Fetch all topics** and their configurations
3. **Audit each topic** against best practices (see `references/audit-rules.md`)
4. **Cross-reference metadata** for completeness
5. **Detect orphaned topics** with no consumers
6. **Report findings** with prioritised recommendations

## Step 1: Environment Overview

Use the Lenses MCP `check_environment_health` tool to get a quick summary:
- Broker count, topic count, consumer count, connector count
- Any existing issues flagged by Lenses

Expected output: Environment health summary with broker, topic and consumer counts.

**Validation**: If the environment is unhealthy or unreachable, stop and report the connection issue before proceeding.

## Step 2: Fetch All Topics

Use the Lenses MCP `list_topics` tool to retrieve all topics with their configurations in one call.

For topics that need deeper inspection, use:
- `get_topic` for detailed config including partitions and consumers
- `get_topic_broker_configs` for broker-level config overrides
- `get_topic_partitions` for partition-level message counts and bytes

Expected output: Full list of topics with their configurations. If zero topics are returned, report this and stop.

## Step 3: Audit Configurations

For each topic, check against the thresholds in `references/audit-rules.md`:
- **Replication factor** - RF=1 is critical, RF=2 is a warning in production
- **Retention policies** - unbounded growth, too short or excessively long
- **Partition count** - single-partition bottlenecks or excessive partitions
- **Compaction settings** - compact without keys, delete for state topics
- **Naming conventions** - must follow `{domain}.{entity}.{event}` pattern

## Step 4: Metadata Completeness

Use the Lenses MCP `list_topic_metadata` tool to check:
- Topics missing descriptions
- Topics missing tags
- Topics without registered schemas (key or value)

Use `list_datasets` with filters (`is_compacted`, `has_records`) to find anomalies.

## Step 5: Orphan Detection

For each topic, use `list_consumer_groups_by_topic` to check for active consumers.
- **Warning**: Topics with zero consumer groups (may be orphaned/dead)
- **Suggestion**: Topics with only inactive/empty consumer groups

## Step 6: Consistency Checks

- Flag topics in the same domain with different retention policies
- Flag topics in the same domain with different replication factors
- Flag topics with inconsistent serialisation formats within a domain

## Success Criteria

### Quantitative
- Triggers on 90% of topic-related queries (test with 10-20 varied phrasings)
- Completes full audit in under 15 MCP tool calls
- 0 failed MCP calls per run

### Qualitative
- Report is actionable without follow-up questions from the user
- Consistent severity categorisation (critical/warning/suggestion) across runs
- Every finding includes a concrete remediation step

## Examples

### Example 1: Routine weekly audit

User says: "Run a topic audit on the staging environment"

Actions:
1. Check staging environment health via Lenses MCP
2. Fetch all topics and configs
3. Audit each topic against rules in `references/audit-rules.md`
4. Check metadata completeness and orphaned topics
Result: Full audit report with prioritised findings

### Example 2: Pre-deployment check

User says: "Check if my topic configs are production-ready"

Actions:
1. Audit all topics for RF < 3, unbounded retention, single partitions
2. Flag any critical issues that would block a production deployment
Result: Report highlighting critical issues that must be fixed before go-live

### Example 3: Investigate a specific topic

User says: "Is the orders.payment.completed topic configured correctly?"

Actions:
1. Fetch detailed config for the specific topic using `get_topic`
2. Check broker-level overrides with `get_topic_broker_configs`
3. Verify metadata and consumer groups
Result: Focused report on a single topic with all findings

## Troubleshooting

### Lenses MCP connection failed
Cause: Environment name is incorrect or Lenses agent is offline.
Solution: Run `check_environment_health` first. Verify the environment name matches what `list_environments` returns.

### No topics returned
Cause: Environment exists but has no topics or permissions are restricted.
Solution: Confirm the cluster has topics via the Lenses UI. Check that the Lenses agent has read access.

### Metadata endpoint returns empty
Cause: Schema Registry is not configured or topics have no registered schemas.
Solution: This is a valid finding - report it as missing metadata rather than treating it as an error.

## Output Format

```
## Topic Audit Report

### Environment: {name}
- Brokers: X | Topics: Y | Consumer groups: Z

### Critical (must fix)
- [topic-name] Description of the issue
  Current: {current value} | Recommended: {recommended value}

### Warning (should fix)
- [topic-name] Description of the issue
  Current: {current value} | Recommended: {recommended value}

### Suggestion (consider improving)
- [topic-name] Description of the issue
  Recommendation: How to fix it

### Summary
- X critical issues found
- Y warnings found
- Z suggestions found
- Topics audited: N
- Orphaned topics: M
```
