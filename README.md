# 🌊 Agentic Engineering for Apache Kafka

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills compatible](https://img.shields.io/badge/skills-Anthropic%20open%20standard-7C3AED)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
[![Lenses MCP](https://img.shields.io/badge/Lenses%20MCP-recommended%20for%20Kafka%20skills-1ABC9C)](https://github.com/lensesio/lenses-mcp)

A drop-in collection of agent skills that turn AI agents and tools such as Claude Code and Cursor into Kafka-specialised engineering assistants. Audit topic configurations, diagnose consumer lag, review schema changes, review connectors and DLQs, catch security misconfigurations and tune performance, all from a single prompt instead of 15 minutes of manual exploration or investigation.

Maintained by [Lenses.io](https://lenses.io), the team that pioneered the developer experience for Apache Kafka. Agentic coding has shifted what that means, and making sure an AI agent knows how to handle Kafka is now part of the job.

Skills are structured Markdown files that tell an AI agent exactly how to approach a domain or task. Think of them as the expert briefing you would give a new engineer before they wrote their first line of Kafka code in your codebase. They are MCP-agnostic by design: every skill in this repo is observed against [Lenses MCP Server](https://github.com/lensesio/lenses-mcp) (the recommended setup), but the structure is open and works with any Kafka MCP server that exposes similar tools.

The quickest way to try the skills end-to-end is with the free [Lenses Community Edition](https://lenses.io/community-edition/), which ships with Lenses HQ, a remote MCP Server and a pre-configured single-broker Kafka cluster with demo data, ideal for local evaluation.

## Why MCP + Skills?

A Kafka MCP server gives agents **access** to your live cluster: topics, consumer groups, connectors, schemas and metrics. The skills in this repository teach agents **expertise**: your team's best practices, audit thresholds, remediation playbooks and standard workflows. Together they enable AI-powered Kafka engineering where the agent doesn't just read your cluster, it knows what to look for and how to fix it.

Without skills, agents are confident generalists. They will write a consumer for the `orders` topic that compiles and runs but does not handle deserialization errors properly, set up DLQs correctly, or partition consumption sensibly for the topic's layout. Skills close the gap between code that runs in a demo and code that holds up in production.

The skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf), so they are portable across Claude Code, Cursor, Claude.ai and the Claude Messages API.

## What's Included

### 🌊 Kafka skills

| Skill | Invocation | Description | Frequency |
|-------|------------|-------------|-----------|
| **Topic Audit** | `/topic-audit` | Audits topic configs against best practices: replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata. | Daily/weekly |
| **Consumer Lag** | `/consumer-lag` | Analyses consumer group lag and diagnoses root causes (throughput bottlenecks, rebalancing, partition skew, stalled consumers) with remediation suggestions. | Daily/on-incident |
| **Perf Review** | `/perf-review` | Reviews producer/consumer performance configs in both the live cluster and the codebase. Flags un-tuned defaults, anti-patterns and missing best practices. | Per-change |
| **Schema Review** | `/schema-review` | Reviews schema changes (Avro, Protobuf, JSON Schema) for compatibility, breaking changes, missing defaults, naming issues and schema drift. | Per-PR |
| **Security Audit** | `/security-audit` | Audits authentication (SASL), encryption (SSL/TLS), secrets management and environment-tier mismatches across codebase and cluster. | Monthly/pre-deploy |
| **Connector Review** | `/connector-review` | Reviews Kafka Connect configurations: error handling, DLQ setup, converters, transforms, task count and task health. | Per-change |
| **DLQ Review** | `/dlq-review` | Reviews dead letter queue completeness: topic config, monitoring, metadata preservation, retry logic, reprocessing paths and connector DLQ alignment. | Periodic |

### Cursor and Claude Code support

Every skill is implemented for both Cursor and Claude Code from a single source of truth at the repo root - the repository itself IS the plugin.

```
.claude-plugin/
├── marketplace.json                  # Claude Code marketplace catalog
└── plugin.json                       # Claude Code plugin manifest
.cursor-plugin/
├── marketplace.json                  # Cursor marketplace catalog
└── plugin.json                       # Cursor plugin manifest
assets/
└── logo.svg                          # Plugin logo
skills/                               # Shared SKILL.md payload (both ecosystems)
├── topic-audit/   (+ references/)
├── consumer-lag/  (+ references/)
├── perf-review/   (+ references/)
├── schema-review/ (+ references/)
├── security-audit/(+ references/)
├── connector-review/(+ references/)
└── dlq-review/    (+ references/)
```

For Claude Code, the seven skills ship as the `kafka-skills` plugin defined by [.claude-plugin/plugin.json](.claude-plugin/plugin.json) and listed in the marketplace catalog at [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) (so the repo is itself an installable Claude Code marketplace).

For Cursor, the same payload is exposed as a [Cursor plugin](https://cursor.com/docs/reference/plugins) via [.cursor-plugin/plugin.json](.cursor-plugin/plugin.json), listed in the marketplace catalog at [.cursor-plugin/marketplace.json](.cursor-plugin/marketplace.json) so the repo is itself an installable Cursor marketplace. Cursor only requires `name` and `description` in skill frontmatter, which the existing skills already provide, so the same `SKILL.md` files serve both ecosystems without duplication. Claude-Code-only frontmatter fields (`allowed-tools`, `argument-hint`) are silently ignored by Cursor.

The Claude Code skill variants include additional configuration: explicit tool restrictions, argument hints, PostToolUse and Stop hooks, effort level, wildcard permissions and custom spinner verbs.

All skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure: frontmatter with trigger phrases, negative triggers and categorised metadata; a `references/` directory for detailed lookup tables and test cases loaded on demand; success criteria with quantitative and qualitative metrics; concrete usage examples; troubleshooting for common errors; and validation gates between workflow steps.

## Quick Start

### For Cursor

The fastest way is the [Cursor Marketplace](https://cursor.com/marketplace). Install the `kafka-skills` plugin directly from the Cursor IDE:

- Open the Cursor Marketplace, search for **Kafka Skills** and click *Install*, or
- Run the `/add-plugin` command in the Cursor Agent and point it at `lensesio/agentic-engineering-for-apache-kafka`.

This installs the seven Kafka skills via the marketplace catalog at [.cursor-plugin/marketplace.json](.cursor-plugin/marketplace.json) and the per-plugin manifest at [.cursor-plugin/plugin.json](.cursor-plugin/plugin.json). After install:

1. Configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in Cursor's MCP settings (recommended for live-cluster skills - any Kafka MCP that exposes an equivalent tool surface will also work).
2. Verify by asking: *"Run a topic audit on staging"* (or any environment name).

**Prefer to copy files** (e.g. you want to fork and customise the skills locally)? Copy `skills/` into your project's `.cursor/skills/` and copy `AGENTS.md` to your project root, then configure your Kafka MCP server as above.

If you'd rather use the cross-tool [Skills CLI](https://github.com/vercel-labs/skills), see [For `npx skills` (any agent)](#for-npx-skills-any-agent) below.

### For Claude Code

The fastest way is the official plugin marketplace. From inside Claude Code, run:

```text
/plugin marketplace add lensesio/agentic-engineering-for-apache-kafka
/plugin install kafka-skills@lensesio
```

This installs the seven Kafka skills as a single `kafka-skills` plugin. After install:

1. Configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in your Claude Code MCP settings (recommended for live-cluster skills - any Kafka MCP that exposes an equivalent tool surface will also work).
2. Verify by asking: *"Run a topic audit on staging"* (or any environment name). Skills auto-trigger from their description; for explicit slash invocation, use the namespaced form `/kafka-skills:topic-audit`.

Pull updates with `/plugin update kafka-skills@lensesio` whenever a new release is published.

**Prefer to copy files** (e.g. you want to fork and customise the skills locally)? Copy `skills/` into your project's `.claude/skills/` and copy `AGENTS.md` to your project root.

If you'd rather use the cross-tool [Skills CLI](https://github.com/vercel-labs/skills), see [For `npx skills` (any agent)](#for-npx-skills-any-agent) below.

### For `npx skills` (any agent)

If you use the cross-tool [Skills CLI](https://github.com/vercel-labs/skills) (`npx skills`), install all seven Kafka skills from the [skills.sh](https://skills.sh) directory with one command:

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka
```

The CLI auto-detects the agents you have installed (Cursor, Claude Code, Codex, OpenCode, Continue and [50+ others](https://github.com/vercel-labs/skills#supported-agents)) and copies the skills into the right per-agent folder.

To install only a specific skill (the seven valid skill names are `topic-audit`, `consumer-lag`, `perf-review`, `schema-review`, `security-audit`, `connector-review`, `dlq-review`):

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka --skill topic-audit
```

To target a specific agent runtime when you have several installed:

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka -a cursor  # or claude-code, codex, opencode, …
```

To install globally (`~/`-scoped) instead of in the current project:

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka -g
```

To preview what would be installed without writing anything:

```bash
npx skills add lensesio/agentic-engineering-for-apache-kafka --list
```

After install, configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in your agent (recommended; any Kafka MCP that exposes an equivalent tool surface also works) and verify with: *"Run a topic audit on staging."* See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if a skill fails to load.

The skills CLI discovers this repo's seven skills via the `skills` array declared in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) (the same manifest also serves Claude Code), so any new skill added to that array becomes available to `npx skills add` automatically. Browse the live listing at [skills.sh/lensesio/agentic-engineering-for-apache-kafka](https://skills.sh/lensesio/agentic-engineering-for-apache-kafka).

### For Claude.ai

1. Download the individual skill folder you want from `skills/` (e.g. `topic-audit/`).
2. Zip the folder.
3. Open Claude.ai → Settings → Capabilities → Skills.
4. Click "Upload skill" and select the zipped folder.
5. Ensure your Lenses MCP server is connected (for Kafka skills).
6. Verify by asking: *"Run a topic audit on staging"*.

### Via the Messages API

For programmatic use cases (applications, agents, automated pipelines), skills can be added to Messages API requests via the `container.skills` parameter. See Anthropic's [Skills API Quickstart](https://docs.anthropic.com/en/docs/agents-and-tools/skills) for implementation details.

Having trouble? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues (upload errors, triggering problems, MCP connection failures).

## Conventions

### Kafka

- Topic names: `<domain>.<entity>.<event>` (e.g. `orders.payment.completed`)
- Consumer group IDs: `<service-name>-<purpose>` (e.g. `analytics-order-processor`)
- Explicit serialisers/deserialisers (no implicit defaults)
- Idempotent producers where possible
- Context managers for all producers and consumers
- Graceful shutdown with signal handlers

## Contributing

No single team has seen every Kafka problem. The engineer running 200 topics on a multi-tenant cluster knows things we do not. The team that spent a month debugging a connector edge case has context that belongs in a skill file. If you have caught yourself coaching an agent through the same Kafka problem more than twice, that is a skill waiting to be written.

We welcome contributions across all three of the engineer profiles these skills serve: data engineers (schemas, pipeline reliability, data quality), backend engineers (clean produce/consume without getting buried in internals) and streaming data engineers (state, windowing, exactly-once). The Kafka surface is vast and these skills only scratch it. Kafka Streams, ksqlDB, MirrorMaker, deeper Schema Registry workflows, cluster upgrades, capacity planning, ACL audits, quota tuning and tiered storage review are all good candidates.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a new Kafka skill, the structural conventions every skill follows (frontmatter, `references/`, test cases, single source of truth shared by the Cursor and Claude Code plugins), and what good first contributions look like. Bug reports, doc improvements and prompt-engineering tweaks are all welcome too. Open an issue or a PR.

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
