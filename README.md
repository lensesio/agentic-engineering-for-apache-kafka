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

**Prefer to copy files** (e.g. you want to fork and customise the skills locally)? Copy `skills/` into your project's `.claude/skills/` and copy `CLAUDE.md` to your project root.

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

## Using the Kafka skills

These skills need a Kafka MCP server connected to your environment. The reference data, examples and triggers are observed against the [Lenses MCP server](https://github.com/lensesio/lenses-mcp), which is the recommended setup; if you run a different Kafka MCP server, fork the relevant skill, swap the tool calls and consider opening a PR with the variant. The skills combine live cluster data with codebase inspection.

#### Topic Audit

Audit all topic configurations against production best practices:

```
/topic-audit <environment>
```

Checks replication factor, retention policies, partition count, compaction settings, naming conventions, orphaned topics and metadata completeness.

#### Consumer Lag

Diagnose consumer group lag issues:

```
/consumer-lag <environment>
/consumer-lag <environment> <topic>   # Filter by topic
```

Identifies throughput bottlenecks, rebalancing issues, partition skew, stalled consumers and empty groups.

#### Performance Review

Review producer/consumer performance configurations:

```
/perf-review <environment>
/perf-review <environment> src/       # Scan specific path
```

Checks both live cluster configs and codebase for un-tuned defaults (`batch.size`, `linger.ms`, `compression.type`, `acks`, etc.).

#### Schema Review

Review schema changes for compatibility:

```
/schema-review <environment>
```

Detects breaking changes, missing defaults, schema drift between repo and cluster, and naming issues.

#### Security Audit

Audit Kafka security configuration:

```
/security-audit <environment>
```

Checks authentication (SASL), encryption (SSL/TLS), secrets management and calibrates severity by environment tier (dev vs production).

#### Connector Review

Review Kafka Connect configurations:

```
/connector-review <environment>
```

Checks error handling, DLQ setup, converters, transforms, task count and validates configs against plugin schemas.

#### DLQ Review

Review dead letter queue completeness:

```
/dlq-review <environment>
```

Discovers DLQ topics, checks monitoring, samples messages for metadata completeness, audits connector DLQ alignment and assesses overall DLQ maturity.

## Conventions

### Code style

- `snake_case` for functions, variables and file names
- `PascalCase` for class names
- `UPPER_SNAKE_CASE` for constants
- Type hints and Google-style docstrings on all public functions
- 100-character maximum line length
- Absolute imports within the project

### Kafka

- Topic names: `<domain>.<entity>.<event>` (e.g. `orders.payment.completed`)
- Consumer group IDs: `<service-name>-<purpose>` (e.g. `analytics-order-processor`)
- Explicit serialisers/deserialisers (no implicit defaults)
- Idempotent producers where possible
- Context managers for all producers and consumers
- Graceful shutdown with signal handlers

### Git

- Branch naming: `feature/`, `fix/`, `docs/`, `refactor/`
- Descriptive commit messages
- Atomic, focused commits
- Squash WIP commits before merging

## Engage with the community

- Join the Lenses Community on Slack via [launchpass.com/lensesio](https://launchpass.com/lensesio).
- Browse [docs.lenses.io](https://docs.lenses.io/) for Lenses HQ and Lenses MCP documentation.
- Try [Lenses Community Edition](https://lenses.io/community-edition/) for a zero-setup Kafka + Lenses environment to evaluate the skills against.

## Contributing

No single team has seen every Kafka problem. The engineer running 200 topics on a multi-tenant cluster knows things we do not. The team that spent a month debugging a connector edge case has context that belongs in a skill file. If you have caught yourself coaching an agent through the same Kafka problem more than twice, that is a skill waiting to be written.

We welcome contributions across all three of the engineer profiles these skills serve: data engineers (schemas, pipeline reliability, data quality), backend developers (clean produce/consume without getting buried in internals) and streaming developers (state, windowing, exactly-once). The Kafka surface is vast and these skills only scratch it. Kafka Streams, ksqlDB, MirrorMaker, deeper Schema Registry workflows, cluster upgrades, capacity planning, ACL audits, quota tuning and tiered storage review are all good candidates. PRs that add support for non-Lenses Kafka MCP servers are also welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a new Kafka skill, the structural conventions every skill follows (frontmatter, `references/`, test cases, single source of truth shared by the Cursor and Claude Code plugins), and what good first contributions look like. Bug reports, doc improvements and prompt-engineering tweaks are all welcome too. Open an issue or a PR.

## Background and inspiration

This repository is an example of *agentic engineering*, where AI agents handle implementation with engineering rigor under human oversight, as distinct from "vibe coding" where output goes unreviewed. The human directs, reviews and owns the codebase; the agent accelerates the work through pre-configured Kafka skills, validation gates and workflow conventions.

The structure and patterns draw on Anthropic's [Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and on three sets of public tips from Boris Cherny, creator of Claude Code:

- [Personal workflow](https://x.com/bcherny/status/2007179832300581177): 13 tips on day-to-day Claude Code usage
- [Team tips](https://x.com/bcherny/status/2017742741636321619): 10 tips from the Claude Code team
- [Customisation guide](https://x.com/bcherny/status/2021699851499798911): 12 tips on customising Claude Code

How those ideas show up in this repo:

**From the team tips.** Both `CLAUDE.md` and `AGENTS.md` are maintained with project conventions, coding standards and Kafka-specific patterns. Invest in them and update after every correction (tip #3). Skills are committed to the repo so the whole team benefits, rather than living in individual prompt history (tip #4). Each skill is sharply scoped with explicit trigger phrases and negative triggers so the right context loads at the right moment, keeping the agent's working context clean (tip #8).

**From Anthropic's skill guide.** All skills follow the three-level progressive disclosure system (frontmatter → `SKILL.md` body → `references/`). Descriptions include trigger phrases so the agent knows when to load each skill, and frontmatter includes `license`, `metadata` (author, version, mcp-server) and `compatibility` fields per the open standard. Skills are categorised as `mcp-enhancement` and include negative triggers to prevent over-triggering. Each skill defines quantitative and qualitative success criteria, and workflow steps include validation gates that stop or adjust the workflow if a step produces unexpected results. Every skill has a `references/test-cases.md` with three layers: triggering tests, functional Given/When/Then scenarios, and performance baselines (tool calls, errors, user corrections with vs without the skill).

This repository deliberately keeps the published plugin payload narrow - just the seven Kafka skills and their `references/`. Hook and settings recipes (PostToolUse formatting, Stop-hook verification, pre-approved permissions, custom spinner verbs) belong in your own project's `.claude/settings.json`, not in a portable skills plugin. Boris Cherny's [personal workflow](https://x.com/bcherny/status/2007179832300581177) and [customisation guide](https://x.com/bcherny/status/2021699851499798911) are the canonical references for setting those up in your own repo.

## Resources

- [Lenses MCP Server for Apache Kafka](https://github.com/lensesio/lenses-mcp)
- [Lenses Community Edition](https://lenses.io/community-edition/)
- [Lenses documentation](https://docs.lenses.io/)
- [Anthropic's Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Cursor Skills documentation](https://cursor.com/docs/context/skills)
- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Settings documentation](https://code.claude.com/docs/en/settings)
- [Claude Code Hooks documentation](https://code.claude.com/docs/en/hooks)
- [Claude Code Permissions documentation](https://code.claude.com/docs/en/permissions)

## License

Released under the [MIT License](LICENSE). See the `LICENSE` file for the full text.
