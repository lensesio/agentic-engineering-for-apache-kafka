# kafka-skills

Lenses-curated Kafka agent skills for [Claude Code](https://code.claude.com/), distributed via the `lensesio` plugin marketplace.

## What's in the box

Seven Kafka skills powered by the [Lenses MCP server](https://github.com/lensesio/lenses-mcp):

| Skill | What it does |
| --- | --- |
| `topic-audit` | Audit topic configs against production best practices (replication, retention, partitions, compaction, naming, orphans, metadata). |
| `consumer-lag` | Diagnose consumer group lag root causes (throughput, rebalancing, partition skew, stalled consumers) and suggest remediation. |
| `perf-review` | Review producer/consumer performance configs in the live cluster and codebase; flag un-tuned defaults and anti-patterns. |
| `schema-review` | Review Avro/Protobuf/JSON Schema changes for compatibility, breaking changes, missing defaults and schema drift. |
| `security-audit` | Audit auth (SASL), encryption (SSL/TLS), ACLs and secrets management; calibrate severity by environment tier. |
| `connector-review` | Review Kafka Connect configurations: error handling, DLQ setup, converters, transforms, task count and task health. |
| `dlq-review` | Review dead letter queue completeness: topic config, monitoring, metadata preservation, retry logic and reprocessing paths. |

## Install

From within Claude Code:

```text
/plugin marketplace add lensesio/agentic-engineering-for-apache-kafka
/plugin install kafka-skills@lensesio
```

After install, skills are available namespaced as `/kafka-skills:topic-audit`, `/kafka-skills:consumer-lag`, etc.

## Recommended: Lenses MCP server

These skills are observed against the [Lenses MCP server](https://github.com/lensesio/lenses-mcp), which is the recommended setup. The skills call MCP tools (`list_topics`, `get_topic`, `list_consumer_groups`, etc.) to read live cluster state; without an MCP server connected, they'll fall back to codebase-only inspection where possible and skip live-cluster checks.

Any Kafka MCP that exposes an equivalent tool surface will also work - you may need to swap a few tool names in the affected SKILL.md if you use a non-Lenses server. PRs adding variants for other Kafka MCP servers are welcome.

To set up the recommended path:

1. Follow the setup instructions in the [Lenses MCP repo](https://github.com/lensesio/lenses-mcp).
2. Verify in Claude Code with `/mcp` that `lenses-mcp` is listed.

The fastest way to try the skills end-to-end is the free [Lenses Community Edition](https://lenses.io/community-edition/), which ships with Lenses HQ, the MCP server and a pre-configured single-broker Kafka cluster with demo data.

## Updates

The plugin's `version` is set in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json). Run `/plugin update kafka-skills@lensesio` to pull the latest published version.

## Source and full docs

This plugin is developed in [lensesio/agentic-engineering-for-apache-kafka](https://github.com/lensesio/agentic-engineering-for-apache-kafka). See the repo for skill source, conventions, contribution guide and release process.

## License

MIT - see [LICENSE](https://github.com/lensesio/agentic-engineering-for-apache-kafka/blob/main/LICENSE).
