---
name: kafka-dlq-review
description: Review dead letter queue implementations for completeness using the Lenses MCP server. Checks DLQ topic existence, configuration, monitoring, metadata preservation, retry logic, reprocessing paths and connector DLQ alignment. Use when user says "review dead letter queues", "check DLQ setup", "DLQ audit" or asks about error handling, message failures or reprocessing. Do NOT use for reprocessing DLQ messages or managing consumer offsets.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, mcp__Lenses__list_topics, mcp__Lenses__get_topic, mcp__Lenses__list_consumer_groups_by_topic, mcp__Lenses__get_dataset_message_metrics, mcp__Lenses__execute_sql, mcp__Lenses__list_kafka_connectors, mcp__Lenses__get_kafka_connector_target_definition
argument-hint: "[required: environment name]"
compatibility: Requires the Lenses MCP server (lenses-mcp) connected and configured with a valid environment.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: lenses-mcp
  category: mcp-enhancement
  approach: problem-first
  patterns: sequential-workflow, domain-intelligence
  tags: [kafka, dlq, dead-letter-queue, error-handling, monitoring]
---

# Kafka Dead Letter Queue Review

Reviews dead letter queue implementations for completeness and best practices. DLQs are a cross-cutting concern that every Kafka consumer eventually needs. Most teams implement them as an afterthought and forget to monitor them.

Target environment: $ARGUMENTS

## Workflow

Copy this checklist and track your progress:

```
DLQ Review Progress:
- [ ] Step 1: Discover DLQ topics
- [ ] Step 2: Check DLQ topic configuration
- [ ] Step 3: Verify DLQ monitoring
- [ ] Step 4: Sample DLQ messages
- [ ] Step 5: Audit connector DLQ configs
- [ ] Step 6: Scan codebase for error handling
- [ ] Step 7: Generate report with maturity assessment
```

1. **Discover DLQ topics** in the cluster
2. **Check DLQ topic configuration** (retention, partitions)
3. **Verify DLQ monitoring** (consumers, alerting)
4. **Sample DLQ messages** for metadata completeness
5. **Audit connector DLQ configs**
6. **Scan codebase** for error handling patterns
7. **Report findings** with maturity assessment

## Step 1: Discover DLQ Topics

Use the Lenses MCP `list_topics` tool and filter for DLQ topics by naming convention:
- `*.dlq`
- `*.dead-letter`
- `*.error`
- `*.errors`
- `*.retry`
- `*-dlq`
- `*-dead-letter`

Also check connector configurations for DLQ topic names using `list_kafka_connectors`.

Expected output: List of DLQ topics discovered by naming convention and connector config.

**Validation**: If no DLQ topics are found, search the codebase for error topic configuration before concluding that DLQs are not implemented.

## Step 2: Check DLQ Topic Configuration

For each discovered DLQ topic, use `get_topic` to verify:

- **Warning**: Retention too short (DLQ messages should be kept longer than source topics for investigation)
- **Warning**: Only 1 partition (may bottleneck if DLQ volume spikes)
- **Warning**: Replication factor < source topic (DLQ data is often more critical to preserve)
- **Suggestion**: Consider compaction for DLQ topics where reprocessing overwrites errors

## Step 3: Verify DLQ Monitoring

Use `list_consumer_groups_by_topic` for each DLQ topic to check:

- **Critical**: DLQ topic has no consumer groups (nobody is monitoring failures)
- **Warning**: DLQ consumer groups are inactive/empty (monitoring may have stopped)
- **Suggestion**: DLQ consumer groups should include alerting or dashboarding services

Check DLQ message rates using `get_dataset_message_metrics`:
- **Warning**: Sustained high DLQ message rate (indicates upstream problem)
- **Warning**: DLQ message rate increasing over time (degrading system health)

## Step 4: Sample DLQ Messages

Use the Lenses MCP `execute_sql` tool to sample messages from DLQ topics:

```sql
SELECT * FROM `{dlq-topic}` LIMIT 10
```

Check that DLQ messages include complete metadata:

### Required Metadata
- **Critical**: Original topic name (where the message came from)
- **Critical**: Error message (what went wrong)
- **Warning**: Original partition and offset (for tracing)
- **Warning**: Original timestamp (when it was produced)
- **Suggestion**: Stack trace (for debugging)
- **Suggestion**: Retry count (how many times it was attempted)
- **Suggestion**: Consumer group ID (which consumer failed)

## Step 5: Audit Connector DLQ Configs

Use `list_kafka_connectors` and `get_kafka_connector_target_definition` to check:

- **Critical**: Connectors with `errors.tolerance=all` but no `errors.deadletterqueue.topic.name` (silently drops messages)
- **Warning**: Connectors with `errors.tolerance=none` and no DLQ (stops on any error, no recovery path)
- **Suggestion**: Enable `errors.deadletterqueue.context.headers.enable=true` for richer error context
- **Suggestion**: Enable `errors.log.enable=true` for error logging

## Step 6: Codebase Inspection

Search the codebase for error handling and DLQ patterns:

- DLQ producer setup (search for `dlq`, `dead.letter`, `error.topic`)
- Retry logic before DLQ routing (search for `retry`, `backoff`, `max_retries`)
- Error handling in consumers (search for exception handling around `poll`, `consume`, `process`)
- Reprocessing mechanisms (scripts or tools to replay DLQ messages)

Flag:
- **Warning**: Consumers with no error handling around message processing
- **Warning**: Immediate DLQ routing without retry attempts
- **Suggestion**: No reprocessing mechanism for DLQ messages (use `resend_message` via Lenses or custom tooling)

## Success Criteria

### Quantitative
- Triggers on 90% of DLQ-related queries (test with 10-20 varied phrasings)
- Completes review in under 15 tool calls (MCP + codebase search)
- Discovers 100% of DLQ topics matching standard naming patterns

### Qualitative
- Unmonitored DLQ topics are always flagged as critical
- Metadata completeness is assessed per DLQ topic with a clear checklist
- Maturity assessment (none/basic/complete) is consistently applied

## Examples

### Example 1: Full DLQ audit

User says: "Audit all dead letter queues in production"

Actions:
1. Discover all DLQ topics by naming convention
2. Check each DLQ topic's configuration and monitoring
3. Sample messages for metadata completeness
4. Audit connector DLQ configs
5. Scan codebase for error handling patterns
Result: Comprehensive DLQ maturity report across all consumers and connectors

### Example 2: Investigating message failures

User says: "Messages are ending up in the DLQ, what's going wrong?"

Actions:
1. Sample recent DLQ messages with `execute_sql`
2. Check error messages and stack traces
3. Trace back to the source topic and consumer group
4. Check DLQ message rate trends
Result: Root cause analysis of DLQ message flow

### Example 3: DLQ coverage check

User says: "Do all our consumers have DLQ handling?"

Actions:
1. List all consumer groups from Lenses
2. Check which groups have corresponding DLQ topics
3. Scan codebase for error handling in consumers
4. Report consumers missing DLQ implementation
Result: Coverage report showing DLQ maturity per consumer

## Troubleshooting

### No DLQ topics found
Cause: DLQ topics may use non-standard naming or DLQs may not be implemented yet.
Solution: Search the codebase for error topic configuration. Also check connector configs for DLQ topic names that may not follow common patterns.

### DLQ messages have no metadata
Cause: The DLQ producer does not include headers or structured error information.
Solution: Report this as a critical finding. DLQ messages without metadata are very difficult to investigate and reprocess.

### execute_sql returns binary/unreadable data
Cause: DLQ messages may use a different serialisation format than expected.
Solution: Try specifying the format in the query. Report the serialisation format issue and recommend consistent format usage.

## Output Format

```
## DLQ Review Report

### Environment: {name}

### DLQ Topics Discovered
| DLQ Topic | Source Topic | Retention | Partitions | Has Consumers | Message Rate |
|-----------|-------------|-----------|------------|--------------|-------------|
| topic.dlq | topic | 7d | 3 | Yes | 12/hr |

### Critical (must fix)
- [topic/connector/file] Description of the issue
  Impact: {what could go wrong}
  Remediation: {how to fix}

### Warning (should fix)
- [topic/connector/file] Description of the issue
  Remediation: {how to fix}

### Suggestion (consider improving)
- [topic/connector/file] Description of the suggestion
  Recommendation: {how to improve}

### DLQ Metadata Completeness
| DLQ Topic | Original Topic | Error Message | Partition/Offset | Timestamp | Stack Trace | Retry Count |
|-----------|---------------|--------------|-----------------|-----------|-------------|-------------|
| topic.dlq | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ |

### Maturity Assessment
| Consumer/Connector | DLQ Status | Maturity |
|-------------------|-----------|---------|
| consumer-name | Configured with monitoring | Complete |
| connector-name | Configured without monitoring | Basic |
| other-consumer | No DLQ | None |

### Summary
- X DLQ topics found
- Y consumers/connectors without DLQ
- Z unmonitored DLQ topics
- Overall DLQ maturity: none/basic/complete
```
