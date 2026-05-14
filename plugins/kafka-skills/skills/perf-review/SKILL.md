---
name: perf-review
description: Review Kafka producer and consumer performance configurations in both the live cluster (via Lenses MCP) and the codebase. Flags un-tuned defaults, anti-patterns and missing best practices. Use when user says "review Kafka performance", "check producer configs", "tune Kafka settings" or asks about throughput, batching or compression. Do NOT use for cluster sizing or capacity planning.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, mcp__Lenses__get_topic, mcp__Lenses__get_topic_broker_configs, mcp__Lenses__get_topic_partitions, mcp__Lenses__get_dataset_message_metrics
argument-hint: "[required: environment name] [optional: path to scan, defaults to src/]"
compatibility: Requires the Lenses MCP server (lenses-mcp) connected and configured with a valid environment.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: lenses-mcp
  category: mcp-enhancement
  approach: tool-first
  patterns: context-aware-selection, domain-intelligence
  tags: [kafka, performance, tuning, producers, consumers]
---

# Kafka Performance Configuration Review

Reviews producer and consumer configurations in both the live cluster and the codebase for performance anti-patterns. These settings are the same across all Kafka client libraries (they're Kafka protocol properties).

Target environment and path: $ARGUMENTS (defaults to `src/` for codebase scan if path not specified)

## Workflow

Copy this checklist and track your progress:

```
Performance Review Progress:
- [ ] Step 1: Inspect live cluster configs
- [ ] Step 2: Scan codebase for producer/consumer configs
- [ ] Step 3: Audit producer configs
- [ ] Step 4: Audit consumer configs
- [ ] Step 5: Cross-reference cluster and code configs
- [ ] Step 6: Generate report
```

1. **Inspect live cluster configs** via Lenses MCP
2. **Scan codebase** for producer/consumer config properties (see `references/producer-defaults.md` and `references/consumer-defaults.md`)
3. **Audit producer configs** against recommended values
4. **Audit consumer configs** against recommended values
5. **Cross-reference** cluster and code configs
6. **Report findings** with current values, recommended values and trade-off explanations

## Step 1: Live Cluster Inspection

Use Lenses MCP tools to check cluster-side performance configs:

- `get_topic` - topic-level configs affecting performance (`min.insync.replicas`, `compression.type`, `max.message.bytes`)
- `get_topic_broker_configs` - broker-level configs (`message.max.bytes`, `replica.fetch.max.bytes`, `num.io.threads`)
- `get_topic_partitions` - message distribution across partitions (detect skew where one partition has significantly more bytes than others)
- `get_dataset_message_metrics` - message throughput over time to identify bottlenecks or capacity headroom

Expected output: Topic-level performance configs, partition distribution and throughput metrics.

**Validation**: If MCP calls fail, proceed with codebase-only analysis and note the limitation in the report.

## Step 2: Codebase Inspection

Search the codebase for Kafka producer and consumer configuration properties. Consult `references/producer-defaults.md` for the full list of producer properties and `references/consumer-defaults.md` for consumer properties.

Also search for anti-patterns listed in `references/producer-defaults.md`:
- Synchronous produce calls (`.get()`, `.result()`, `flush()` after every send)
- Missing delivery callbacks / error handlers
- Missing graceful shutdown / rebalance listeners

## Step 3: Audit Producer Configs

Compare found producer configs against the recommended values in `references/producer-defaults.md`. Key areas: `acks`, `batch.size`, `linger.ms`, `compression.type`, `enable.idempotence` and `retries`.

## Step 4: Audit Consumer Configs

Compare found consumer configs against the recommended values in `references/consumer-defaults.md`. Key areas: `max.poll.records`, `max.poll.interval.ms`, `auto.offset.reset`, `enable.auto.commit` and `fetch.min.bytes`.

## Success Criteria

### Quantitative
- Triggers on 90% of performance-related queries (test with 10-20 varied phrasings)
- Completes review in under 15 tool calls (MCP + codebase search)
- 0 failed MCP calls per run

### Qualitative
- Every finding shows current value, recommended value and trade-off explanation
- Anti-patterns are identified with file and line references
- Estimated throughput impact (low/medium/high) is consistently calibrated

## Examples

### Example 1: Routine performance review

User says: "Review Kafka performance configs for staging"

Actions:
1. Inspect cluster-side configs for all topics in staging
2. Scan `src/` for producer/consumer property definitions
3. Cross-reference code configs against reference tables
Result: Report with per-property findings and throughput impact estimates

### Example 2: Investigating slow consumers

User says: "Why are my consumers slow? Check the performance settings."

Actions:
1. Focus on consumer config properties in the codebase
2. Check `max.poll.records`, `fetch.min.bytes` and `enable.auto.commit`
3. Look for anti-patterns like synchronous processing
Result: Targeted report on consumer-side bottlenecks with remediation steps

### Example 3: Scoped codebase review

User says: "Check Kafka configs in src/kafka/ for the production environment"

Actions:
1. Scan only `src/kafka/` for producer and consumer configs
2. Cross-reference with live production cluster settings
Result: Focused report on a specific directory's Kafka configurations

## Troubleshooting

### No Kafka config properties found in codebase
Cause: The codebase may use a framework or wrapper that hides raw Kafka properties.
Solution: Search for framework-specific config patterns (e.g., Spring Boot `application.yml`, Django settings). Report the framework used and suggest manual review.

### Lenses MCP returns no topic data
Cause: Environment name is incorrect or Lenses agent is offline.
Solution: Run `check_environment_health` first. Verify the environment name matches what `list_environments` returns.

### Partition skew detection is inconclusive
Cause: Topic has very low throughput so byte counts are similar across partitions.
Solution: Note that skew detection requires meaningful throughput. For low-volume topics, skip the skew check and note it in the report.

## Output Format

```
## Performance Review Report

### Cluster-Side Findings
- [topic-name] {property}: {current value}
  Recommendation: {recommended value} - {explanation}

### Codebase Findings (Producers)
- [file:line] {property} = {current value}
  Recommendation: {recommended value} - {explanation}

### Codebase Findings (Consumers)
- [file:line] {property} = {current value}
  Recommendation: {recommended value} - {explanation}

### Anti-Patterns
- [file:line] Description of the anti-pattern
  Recommendation: How to fix it

### Summary
- X producer issues found
- Y consumer issues found
- Z anti-patterns found
- Estimated throughput impact: low/medium/high
```
