# AGENTS.md

## Project Overview

A drop-in collection of agent skills that turn AI agents and tools such as Claude Code and Cursor into Kafka-specialised engineering assistants. The repository **is** the plugin - the same `skills/` payload at the repo root is consumed by both the Claude Code marketplace (`.claude-plugin/`) and the Cursor marketplace (`.cursor-plugin/`).

Maintained by [Lenses.io](https://lenses.io). Skills are MCP-agnostic by design but observed against the [Lenses MCP Server](https://github.com/lensesio/lenses-mcp); any Kafka MCP server that exposes an equivalent tool surface works.

This repo is a **Markdown skills payload**. It deliberately ships no source code, build system, tests, or runtime configuration - just `SKILL.md` files, their `references/`, plugin manifests, and documentation.

## Project Structure

```
.claude-plugin/
├── marketplace.json                  # Claude Code marketplace catalog (lists kafka-skills)
└── plugin.json                       # Claude Code plugin manifest
.cursor-plugin/
├── marketplace.json                  # Cursor marketplace catalog (lists kafka-skills)
└── plugin.json                       # Cursor plugin manifest (references assets/logo.svg)
assets/
└── logo.svg                          # Plugin logo (consumed by the Cursor manifest)
skills/                               # Shared SKILL.md payload (Claude Code + Cursor)
├── topic-audit/      (+ references/)
├── consumer-lag/     (+ references/)
├── perf-review/      (+ references/)
├── schema-review/    (+ references/)
├── security-audit/   (+ references/)
├── connector-review/ (+ references/)
└── dlq-review/       (+ references/)
AGENTS.md                             # Agent memory (this file)
README.md                             # Source of truth for end-user installation and usage
CONTRIBUTING.md                       # How to add a new skill, conventions, release process
TROUBLESHOOTING.md                    # Common issues (upload errors, triggering, MCP failures)
LICENSE                               # MIT
.gitignore                            # Includes .claude/ so Claude Code's per-user state stays out of git
```

For Claude Code, the seven skills ship as the `kafka-skills` plugin via the `lensesio` marketplace catalog. Install with `/plugin marketplace add lensesio/agentic-engineering-for-apache-kafka` then `/plugin install kafka-skills@lensesio`. Skills auto-trigger from their description; for explicit slash invocation use `/kafka-skills:<skill-name>`.

For Cursor, the same payload is exposed as a [Cursor plugin](https://cursor.com/docs/reference/plugins). Install through the [Cursor Marketplace](https://cursor.com/marketplace) or the `/add-plugin` command in the Cursor Agent. Cursor only requires `name` and `description` in skill frontmatter, so the same `SKILL.md` files serve both ecosystems without duplication. Claude-Code-only frontmatter fields (`allowed-tools`, `argument-hint`) are silently ignored by Cursor.

For the cross-tool [Skills CLI](https://github.com/vercel-labs/skills), the same payload is also installable via `npx skills add lensesio/agentic-engineering-for-apache-kafka`, which works with Cursor, Claude Code, Codex, OpenCode, Continue and 50+ other agents from one command. Discovery is driven by the `skills` array in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) per the [plugin-manifest discovery format](https://github.com/vercel-labs/skills#plugin-manifest-discovery), so the same array gates both the Claude Code marketplace and `npx skills`. The repo is auto-indexed at [skills.sh/lensesio/agentic-engineering-for-apache-kafka](https://skills.sh/lensesio/agentic-engineering-for-apache-kafka); no manual submission is needed.

The published plugin payload deliberately stays narrow - just the seven Kafka skills and their `references/`. Hook and settings recipes (PostToolUse formatting, Stop-hook verification, pre-approved permissions, custom spinner verbs) belong in each consuming team's own `.claude/settings.json`, not in a portable skills plugin.

## Skill Structure Conventions

All skills follow the [Anthropic open standard](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure:

- **YAML frontmatter** includes `name`, `description` (with trigger phrases and negative triggers), `license`, `metadata` (author, version, mcp-server, category) and `compatibility` (for MCP skills)
- **SKILL.md body** contains workflow steps with expected output notes and validation gates, success criteria, examples and troubleshooting
- **`references/` directory** holds detailed lookup tables and domain rules loaded on demand (audit thresholds, config defaults, compatibility matrices)
- Each skill includes a **Success Criteria** section with quantitative and qualitative metrics
- Each skill includes an **Examples** section with concrete "User says X -> Claude does Y" scenarios
- Each skill includes a **Troubleshooting** section for common errors and edge cases
- Skills are categorised as `workflow-automation` or `mcp-enhancement` in their metadata
- Every skill has a `references/test-cases.md` with triggering tests (should/should not trigger), functional tests (Given/When/Then) and performance baselines
- Each skill's metadata includes `approach` (problem-first or tool-first) and `patterns` (sequential-workflow, iterative-refinement, context-aware-selection, domain-intelligence)
- Skills are portable across Claude.ai, Claude Code, Cursor and the API (`/v1/skills` endpoint)
- General troubleshooting (upload errors, triggering issues, MCP connection failures, large context) is in `TROUBLESHOOTING.md` at the repo root; skill-specific troubleshooting is in each `SKILL.md`

## Kafka Skills

Recommended for use with the [Lenses MCP Server](https://github.com/lensesio/lenses-mcp):

- **`/topic-audit`** - Audits topic configs against best practices: replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata.
- **`/consumer-lag`** - Analyses consumer group lag and diagnoses root causes (throughput bottlenecks, rebalancing, partition skew, stalled consumers) with remediation suggestions.
- **`/perf-review`** - Reviews producer/consumer performance configs in both the live cluster and the codebase. Flags un-tuned defaults, anti-patterns and missing best practices.
- **`/schema-review`** - Reviews schema changes (Avro, Protobuf, JSON Schema) for compatibility, breaking changes, missing defaults, naming issues and schema drift.
- **`/security-audit`** - Audits authentication (SASL), encryption (SSL/TLS), secrets management and environment-tier mismatches across codebase and cluster.
- **`/connector-review`** - Reviews Kafka Connect configurations: error handling, DLQ setup, converters, transforms, task count and task health.
- **`/dlq-review`** - Reviews dead letter queue completeness: topic config, monitoring, metadata preservation, retry logic, reprocessing paths and connector DLQ alignment.

## Conventions

These match the conventions baked into the skill prompts and reflected in `README.md`. They describe how the skills expect Kafka resources to be named in a consumer's project; they are not enforced on this repo's Markdown.

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

## Things to avoid when editing this repo

- Don't create a parallel `.cursor/skills/` tree - `skills/` at the repo root is the single source of truth for both Cursor and Claude Code
- Don't add `hooks`, `mcpServers` or `permissionMode` to plugin-shipped skills or subagents - the Claude Code plugin loader silently drops them
- Don't change skill behaviour without updating the matching `references/test-cases.md` (triggering, functional and baseline layers)
- Don't add source code or build infrastructure (`src/`, `tests/`, language-specific build configs) - the repo is intentionally a Markdown payload
- Don't bump skill content without bumping `version` in both `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`; without a version bump, `/plugin update kafka-skills@lensesio` won't pick up changes (see [CONTRIBUTING.md](CONTRIBUTING.md))
- Don't add a new skill folder under `skills/` without also adding its path to the `skills` array in `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json` - that array is the canonical published surface for the Claude Code marketplace and the `npx skills add` install path
- Don't break the published plugin layout (`.claude-plugin/`, `.cursor-plugin/`, `skills/`, `assets/`) without an issue first
- Don't commit `.env` files, credentials, or any consumer-team configuration

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
- [Skills CLI (`vercel-labs/skills`)](https://github.com/vercel-labs/skills)
- [skills.sh - open agent skills directory](https://skills.sh)
- [Agent Skills Specification](https://agentskills.io)
