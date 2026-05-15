# 🌊 Agentic Engineering for Apache Kafka

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills compatible](https://img.shields.io/badge/skills-Anthropic%20open%20standard-7C3AED)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
[![Lenses MCP](https://img.shields.io/badge/Lenses%20MCP-recommended%20for%20Kafka%20skills-1ABC9C)](https://github.com/lensesio/lenses-mcp)

A collection of agent skills that turn AI agents and coding tools such as Claude Code and Cursor into Kafka-specialised engineering assistants. Audit topic configurations, diagnose consumer lag, review schema changes, review connectors and DLQs, catch security misconfigurations and tune performance, all from a single prompt instead of 15 minutes of manual exploration or investigation.

Maintained by [Lenses.io](https://lenses.io), the team that pioneered the developer experience for Apache Kafka. Agentic engineering has shifted what that means. Making sure an AI agent knows how to handle streaming data is now part of the job.

## Why Skills and MCP?

A Kafka MCP server gives agents **access** to your live cluster: topics, consumer groups, connectors, schemas and metrics. The skills in this repository teach agents **expertise**: best practices, audit thresholds, remediation playbooks and standard workflows. Together they enable AI-powered Kafka engineering where the agent doesn't just read your cluster, it knows what to look for and how to fix it.

Without skills, agents are confident generalists. They will write a consumer for the `orders` topic that compiles and runs but does not handle deserialization errors properly, set up DLQs correctly, or partition consumption sensibly for the topic's layout. Skills close the gap between code that runs in a demo and code that holds up in production.

These skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf), so they are portable across Claude Code, Cursor, Claude.ai and the Claude Messages API. They are MCP-agnostic by design: every skill in this repo is tested against [Lenses MCP Server](https://github.com/lensesio/lenses-mcp) (the recommended setup), but will work with any Kafka MCP server that exposes similar tools.

The quickest way to try the skills end-to-end is with the free [Lenses Community Edition](https://lenses.io/community-edition/), which ships with Lenses HQ, a remote MCP Server and a pre-configured single-broker Kafka cluster with demo data.

## What's Included

### Kafka skills

| Skill | Invocation | Description | Frequency |
|-------|------------|-------------|-----------|
| **Topic Audit** | `/kafka-topic-audit` | Audits topic configs against best practices: replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata. | Daily/weekly |
| **Consumer Lag** | `/kafka-consumer-lag` | Analyses consumer group lag and diagnoses root causes (throughput bottlenecks, rebalancing, partition skew, stalled consumers) with remediation suggestions. | Daily/on-incident |
| **Perf Review** | `/kafka-perf-review` | Reviews producer/consumer performance configs in both the live cluster and the codebase. Flags un-tuned defaults, anti-patterns and missing best practices. | Per-change |
| **Schema Review** | `/kafka-schema-review` | Reviews schema changes (Avro, Protobuf, JSON Schema) for compatibility, breaking changes, missing defaults, naming issues and schema drift. | Per-PR |
| **Security Audit** | `/kafka-security-audit` | Audits authentication (SASL), encryption (SSL/TLS), secrets management and environment-tier mismatches across codebase and cluster. | Monthly/pre-deploy |
| **Connector Review** | `/kafka-connector-review` | Reviews Kafka Connect configurations: error handling, DLQ setup, converters, transforms, task count and task health. | Per-change |
| **DLQ Review** | `/kafka-dlq-review` | Reviews dead letter queue completeness: topic config, monitoring, metadata preservation, retry logic, reprocessing paths and connector DLQ alignment. | Periodic |

### Claude Code and Cursor support

Every skill is implemented for both Claude Code and Cursor from a single source of truth at the repo root. The repository itself *is* the plugin.

```
.claude-plugin/
├── marketplace.json        # Claude marketplace catalog
└── plugin.json             # Claude plugin manifest
.cursor-plugin/
├── marketplace.json        # Cursor marketplace catalog
└── plugin.json             # Cursor plugin manifest
assets/
└── logo.svg                # Plugin logo
skills/                     # Shared SKILL.md definitions and references
├── kafka-topic-audit/
├── kafka-consumer-lag/
├── kafka-perf-review/
├── kafka-schema-review/
├── kafka-security-audit/
├── kafka-connector-review/
└── kafka-dlq-review/
```

All skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure: frontmatter with trigger phrases, negative triggers and categorised metadata; a `references/` directory for detailed lookup tables and test cases loaded on demand; success criteria with quantitative and qualitative metrics; concrete usage examples; troubleshooting for common errors; and validation gates between workflow steps.

## Installation

### Claude Code

```bash
/plugin marketplace add lensesio/agentic-engineering-for-apache-kafka

/plugin install kafka-skills@lensesio
```

This installs all the Kafka skills as a single `kafka-skills` plugin.

Pull updates with `/plugin update kafka-skills@lensesio` whenever a new release is published.

### Cursor, Codex, OpenCode and others

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka
```

This cross-tool [Skills CLI](https://github.com/vercel-labs/skills) (`npx skills`) installs all Kafka skills from the [skills.sh](https://skills.sh) directory.

The CLI auto-detects the agents you have installed (Cursor, Claude Code, Codex, OpenCode, Continue and [50+ others](https://github.com/vercel-labs/skills#supported-agents)) and copies the skills into the right per-agent folder.

To install only a specific skill (the seven valid skill names are `kafka-topic-audit`, `kafka-consumer-lag`, `kafka-perf-review`, `kafka-schema-review`, `kafka-security-audit`, `kafka-connector-review`, `kafka-dlq-review`):

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka --skill kafka-topic-audit
```

To install globally (`~/`-scoped) instead of in the current project:

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka -g
```

## Quick Start

After installing skills, configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) (or any Kafka MCP that exposes an equivalent tool surface will work).

Verify by asking, *"Run a topic audit on staging"* (or your environment name).

Skills auto-trigger from their description. For explicit slash invocation, use the namespaced form, e.g. `/kafka-skills:kafka-topic-audit`.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if a skill fails to load.

## Conventions

The skills actively audit these conventions in your cluster or codebase:

- Topic names: `<domain>.<entity>.<event>` (e.g. `orders.payment.completed`) - checked by `kafka-topic-audit`
- Idempotent producers where possible (`enable.idempotence=true`) - checked by `kafka-perf-review`
- Graceful shutdown for producers and consumers - flagged as an anti-pattern by `kafka-perf-review`

## Contributing

No single team has seen every Kafka problem. The engineer running 200 topics on a multi-tenant cluster knows things we do not. The team that spent a month debugging a connector edge case has context that belongs in a skill file. If you have caught yourself coaching an agent through the same Kafka problem more than twice, that is a skill waiting to be written.

We welcome contributions across all three of the engineer profiles these skills serve: data engineers (schemas, pipeline reliability, data quality), backend engineers (clean produce/consume without getting buried in internals) and streaming data engineers (state, windowing, exactly-once). The Kafka surface is vast and these skills only scratch it. Kafka Streams, ksqlDB, MirrorMaker, deeper Schema Registry workflows, cluster upgrades, capacity planning, ACL audits, quota tuning and tiered storage review are all good candidates.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a new Kafka skill, the structural conventions every skill follows (frontmatter, `references/`, test cases, single source of truth shared by the Cursor and Claude Code plugins), and what good first contributions look like. Bug reports, doc improvements and prompt-engineering tweaks are all welcome too.

## Resources

- [Lenses MCP Server for Apache Kafka](https://github.com/lensesio/lenses-mcp)
- [Lenses Community Edition](https://lenses.io/community-edition/)
- [Lenses documentation](https://docs.lenses.io/)
- [Anthropic's Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Cursor Skills documentation](https://cursor.com/docs/context/skills)
- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills)
- [Skills CLI (`vercel-labs/skills`)](https://github.com/vercel-labs/skills)
- [skills.sh — open agent skills directory](https://skills.sh)
- [Agent Skills Specification](https://agentskills.io)

## License

Released under the [MIT License](LICENSE). See the `LICENSE` file for the full text.
