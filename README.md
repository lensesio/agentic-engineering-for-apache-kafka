# 🌊 Agentic Engineering for Apache Kafka

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills compatible](https://img.shields.io/badge/skills-Anthropic%20open%20standard-7C3AED)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
[![Lenses MCP](https://img.shields.io/badge/Lenses%20MCP-required%20for%20Kafka%20skills-1ABC9C)](https://github.com/lensesio/lenses-mcp)

A drop-in collection of agent skills, subagents and editor configuration that turns Claude Code and Cursor into a Kafka-aware engineering assistant. Audit topic configurations, diagnose consumer lag, review schema changes, catch security misconfigurations and ship code, all from a single prompt instead of 15 minutes of manual investigation.

Maintained by [Lenses.io](https://lenses.io), the team that pioneered the developer experience for Apache Kafka. Agentic coding has shifted what that means, and making sure an AI agent actually knows how to handle Kafka is now part of the job.

Skills are structured Markdown files that tell an AI agent exactly how to approach a domain or task. Think of them as the expert briefing you would give a new engineer before they wrote their first line of Kafka code in your codebase. They are MCP-agnostic by design: every skill in this repo is observed against the [Lenses MCP Server](https://github.com/lensesio/lenses-mcp) (the recommended setup), but the structure is open and contributions for other Kafka MCP servers are welcome.

The quickest way to try the skills end-to-end is with the free [Lenses Community Edition](https://lenses.io/community-edition/), which ships with Lenses HQ, the MCP Server and a pre-configured single-broker Kafka cluster with demo data, ideal for local evaluation.

## Why MCP + Skills?

A Kafka MCP server gives agents **access** to your live cluster: topics, consumer groups, connectors, schemas and metrics. The skills in this repository teach agents **expertise**: your team's best practices, audit thresholds, remediation playbooks and standard workflows. Together they enable AI-powered Kafka engineering where the agent doesn't just read your cluster, it knows what to look for and how to fix it.

Without skills, agents are confident generalists. They will write a consumer for the `orders` topic that compiles and runs but does not handle deserialization errors properly, set up DLQs correctly, or partition consumption sensibly for the topic's layout. Skills close the gap between code that runs in a demo and code that holds up in production.

The skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf), so they are portable across Claude Code, Cursor, Claude.ai and the Claude Messages API.

## What's Included

### 📚 General-purpose skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| **Techdebt** | `/techdebt` | Scans the codebase for TODO/FIXME/HACK comments, commented-out code, duplicated code, unused imports, inconsistent patterns and refactoring opportunities. Useful at the end of a coding session. |
| **Commit-Push-PR** | `/commit-push-pr` | Commits staged changes, pushes to the remote and opens a PR in one step. Generates the commit message and PR description from the diff. |

### 🌊 Kafka skills (observed against [Lenses MCP](https://github.com/lensesio/lenses-mcp))

| Skill | Invocation | Description | Frequency |
|-------|------------|-------------|-----------|
| **Topic Audit** | `/kafka-topic-audit` | Audits topic configs against best practices: replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata. | Daily/weekly |
| **Consumer Lag** | `/kafka-consumer-lag` | Analyses consumer group lag and diagnoses root causes (throughput bottlenecks, rebalancing, partition skew, stalled consumers) with remediation suggestions. | Daily/on-incident |
| **Perf Review** | `/kafka-perf-review` | Reviews producer/consumer performance configs in both the live cluster and the codebase. Flags un-tuned defaults, anti-patterns and missing best practices. | Per-change |
| **Schema Review** | `/kafka-schema-review` | Reviews schema changes (Avro, Protobuf, JSON Schema) for compatibility, breaking changes, missing defaults, naming issues and schema drift. | Per-PR |
| **Security Audit** | `/kafka-security-audit` | Audits authentication (SASL), encryption (SSL/TLS), secrets management and environment-tier mismatches across codebase and cluster. | Monthly/pre-deploy |
| **Connector Review** | `/kafka-connector-review` | Reviews Kafka Connect configurations: error handling, DLQ setup, converters, transforms, task count and task health. | Per-change |
| **DLQ Review** | `/kafka-dlq-review` | Reviews dead letter queue completeness: topic config, monitoring, metadata preservation, retry logic, reprocessing paths and connector DLQ alignment. | Periodic |

### 🤖 Subagents

| Subagent | Role | Description |
|----------|------|-------------|
| **code-reviewer** | Staff Engineer | Reviews code changes for quality, security, architectural fit and Kafka best practices. Evaluates system-wide impact and long-term maintainability. |
| **test-writer** | Test Engineer | Generates `pytest` test suites with Kafka client mocks for unit tests and Docker-based integration tests. Targets greater than 80% coverage. |
| **doc-writer** | Documentation Specialist | Generates Google-style docstrings, README files, module documentation and inline comments. Keeps docs in sync with code. |
| **code-simplifier** | Code Cleanup | Simplifies code after changes by flattening nested conditionals, removing dead branches and consolidating duplicated logic. Preserves behavior. |

### 🪝 Hooks, settings and customisation (Claude Code)

| Feature | Description |
|---------|-------------|
| **PostToolUse formatting** | Auto-runs `ruff format` after every file Write/Edit to catch formatting issues before CI. |
| **Stop hook for verification** | Runs `ruff check` and `pytest` when the agent finishes a turn, providing the verification feedback loop that materially improves output quality. |
| **Effort level** | Defaults to `medium`. Raise to `high` for deeper reasoning, or `max` if you are running Opus 4.6 and want maximum reasoning depth. |
| **Pre-allowed permissions** | Wildcard patterns for safe commands (`uv run pytest *`, `Edit(src/**)`, `gh pr *`) to reduce permission prompts. |
| **Custom spinner verbs** | Kafka-themed spinner verbs ("Producing messages", "Committing offsets", etc.) for a little personality. |

The example project ships with Python tooling (`uv`, `pytest`, `ruff`) because that is what the bundled hooks demonstrate. The skills themselves are language-agnostic; swap the hooks for your stack as needed.

### Cursor and Claude Code support

Every skill and subagent is implemented for both Cursor and Claude Code. The hooks, settings and customisation features above are Claude Code only.

There is some duplication across the two trees because there is currently no shared on-disk standard for editor skills. Each tool has its own conventions:

```
.cursor/                              .claude/
├── skills/                           ├── settings.json (hooks + permissions)
│   ├── techdebt/                     ├── skills/
│   │   └── references/               │   ├── techdebt/
│   ├── commit-push-pr/               │   │   └── references/
│   │   └── references/               │   ├── commit-push-pr/
│   ├── kafka-topic-audit/            │   │   └── references/
│   │   └── references/               │   ├── kafka-topic-audit/
│   ├── kafka-consumer-lag/           │   │   └── references/
│   │   └── references/               │   ├── kafka-consumer-lag/
│   ├── kafka-perf-review/            │   │   └── references/
│   │   └── references/               │   ├── kafka-perf-review/
│   ├── kafka-schema-review/          │   │   └── references/
│   │   └── references/               │   ├── kafka-schema-review/
│   ├── kafka-security-audit/         │   │   └── references/
│   │   └── references/               │   ├── kafka-security-audit/
│   ├── kafka-connector-review/       │   │   └── references/
│   │   └── references/               │   ├── kafka-connector-review/
│   └── kafka-dlq-review/             │   │   └── references/
│       └── references/               │   └── kafka-dlq-review/
└── agents/                            │       └── references/
    ├── code-reviewer.md               └── agents/
    ├── test-writer.md                     ├── code-reviewer.md
    ├── doc-writer.md                      ├── test-writer.md
    └── code-simplifier.md                 ├── doc-writer.md
                                           └── code-simplifier.md
```

The Claude Code variants include additional configuration: explicit tool restrictions, model routing (`sonnet`), persistent `memory: project` for cross-session learning, inline bash pre-computation in skills, PostToolUse and Stop hooks, effort level, wildcard permissions and custom spinner verbs, all configured in `.claude/settings.json`.

All skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure: frontmatter with trigger phrases, negative triggers and categorised metadata; a `references/` directory for detailed lookup tables and test cases loaded on demand; success criteria with quantitative and qualitative metrics; concrete usage examples; troubleshooting for common errors; and validation gates between workflow steps.

## Quick Start

### For Cursor

1. Copy `.cursor/` and `AGENTS.md` to your project root.
2. If you plan to use the Kafka skills, configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in Cursor's MCP settings.
3. Verify by asking: *"Run a topic audit on staging"* (or any environment name).

### For Claude Code

1. Copy `.claude/` and `CLAUDE.md` to your project root.
2. If you plan to use the Kafka skills, configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in your Claude Code MCP settings.
3. Verify by asking: *"Run a topic audit on staging"* (or any environment name).

### For Claude.ai

1. Download the individual skill folder you want (e.g. `kafka-topic-audit/`).
2. Zip the folder.
3. Open Claude.ai → Settings → Capabilities → Skills.
4. Click "Upload skill" and select the zipped folder.
5. Ensure your Lenses MCP server is connected (for Kafka skills).
6. Verify by asking: *"Run a topic audit on staging"*.

### Via the Messages API

For programmatic use cases (applications, agents, automated pipelines), skills can be added to Messages API requests via the `container.skills` parameter. See Anthropic's [Skills API Quickstart](https://docs.anthropic.com/en/docs/agents-and-tools/skills) for implementation details.

Having trouble? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues (upload errors, triggering problems, MCP connection failures).

## Using the Agentic Workflows

### General-purpose skills

#### Techdebt

Run at the end of a coding session to find and eliminate technical debt:

```
/techdebt        # Scan src/ and tests/
/techdebt src/   # Scan a specific directory
```

The skill produces a categorised report:

- **Critical:** Must fix (duplicated logic, security issues)
- **Warning:** Should fix (dead code, unused imports)
- **Suggestion:** Consider improving (refactoring opportunities)

#### Commit-Push-PR

Ship code in one step: commit, push and open a PR.

```
/commit-push-pr
```

The skill:

- Pre-computes git status, current branch and diff (Claude Code uses inline bash).
- Generates a conventional commit message from the diff.
- Pushes to the remote (creating the branch if needed).
- Opens a PR with a generated title and summary via `gh`.

### Kafka skills

These skills need a Kafka MCP server connected to your environment. The reference data, examples and triggers are observed against the [Lenses MCP server](https://github.com/lensesio/lenses-mcp), which is the recommended setup; if you run a different Kafka MCP server, fork the relevant skill, swap the tool calls and consider opening a PR with the variant. The skills combine live cluster data with codebase inspection.

#### Topic Audit

Audit all topic configurations against production best practices:

```
/kafka-topic-audit <environment>
```

Checks replication factor, retention policies, partition count, compaction settings, naming conventions, orphaned topics and metadata completeness.

#### Consumer Lag

Diagnose consumer group lag issues:

```
/kafka-consumer-lag <environment>
/kafka-consumer-lag <environment> <topic>   # Filter by topic
```

Identifies throughput bottlenecks, rebalancing issues, partition skew, stalled consumers and empty groups.

#### Performance Review

Review producer/consumer performance configurations:

```
/kafka-perf-review <environment>
/kafka-perf-review <environment> src/       # Scan specific path
```

Checks both live cluster configs and codebase for un-tuned defaults (`batch.size`, `linger.ms`, `compression.type`, `acks`, etc.).

#### Schema Review

Review schema changes for compatibility:

```
/kafka-schema-review <environment>
```

Detects breaking changes, missing defaults, schema drift between repo and cluster, and naming issues.

#### Security Audit

Audit Kafka security configuration:

```
/kafka-security-audit <environment>
```

Checks authentication (SASL), encryption (SSL/TLS), secrets management and calibrates severity by environment tier (dev vs production).

#### Connector Review

Review Kafka Connect configurations:

```
/kafka-connector-review <environment>
```

Checks error handling, DLQ setup, converters, transforms, task count and validates configs against plugin schemas.

#### DLQ Review

Review dead letter queue completeness:

```
/kafka-dlq-review <environment>
```

Discovers DLQ topics, checks monitoring, samples messages for metadata completeness, audits connector DLQ alignment and assesses overall DLQ maturity.

### Subagents

#### Code Reviewer (Staff Engineer)

Automatically invoked after code changes, or trigger explicitly:

```
Use the code-reviewer to review my recent changes
```

The reviewer evaluates:

- Architectural fit and system-wide impact
- Kafka best practices (context managers, idempotent producers, graceful shutdown)
- Code quality (naming, duplication, type hints, docstrings)
- Security (no hardcoded secrets, proper input validation)
- Operational readiness (logging, error handling, retry logic)

#### Test Writer

Generate tests for new or changed code:

```
Use the test-writer to add tests for src/kafka/producer.py
```

Produces `pytest`-based unit tests with Kafka client mocks, integration tests marked with `@pytest.mark.integration`, reusable fixtures in `tests/conftest.py`, and a coverage report targeting greater than 80%.

#### Doc Writer

Generate or update documentation:

```
Use the doc-writer to document src/kafka/
```

Produces Google-style docstrings (Args, Returns, Raises, Example), module-level docstrings explaining purpose and typical usage, and README updates that reflect current code behaviour.

#### Code Simplifier

Run after a feature or fix to clean up the code:

```
Use the code-simplifier to clean up my recent changes
```

Flattens deeply nested conditionals with early returns, removes dead branches and unnecessary intermediate variables, consolidates duplicated logic into shared utilities, preserves all external behaviour, and runs the tests after each significant change to verify correctness.

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a new skill or subagent, the structural conventions every skill follows (frontmatter, `references/`, test cases, dual `.cursor/` + `.claude/` variants), and what good first contributions look like. Bug reports, doc improvements and prompt-engineering tweaks are all welcome too. Open an issue or a PR.

## Background and inspiration

This repository is an example of *agentic engineering*, where AI agents handle implementation with engineering rigor under human oversight, as distinct from "vibe coding" where output goes unreviewed. The human directs, reviews and owns the codebase; the agent accelerates the work through pre-configured skills, subagents and workflows.

The structure and patterns draw on Anthropic's [Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and on three sets of public tips from Boris Cherny, creator of Claude Code:

- [Personal workflow](https://x.com/bcherny/status/2007179832300581177): 13 tips on day-to-day Claude Code usage
- [Team tips](https://x.com/bcherny/status/2017742741636321619): 10 tips from the Claude Code team
- [Customisation guide](https://x.com/bcherny/status/2021699851499798911): 12 tips on customising Claude Code

How those ideas show up in this repo:

**From the personal workflow.** The `/commit-push-pr` skill automates the inner loop of commit, push and PR creation (tip #7). The `code-simplifier` subagent cleans up after the agent finishes working (tip #8). A PostToolUse formatting hook runs `ruff format` after every edit to catch the last 10% of formatting issues before CI (tip #9). Common safe commands are pre-approved in `.claude/settings.json` to avoid unnecessary permission prompts (tip #10). Most importantly, the test-writer and code-reviewer subagents and the Stop hook all give the agent a way to verify its work — tip #13, the single most important tip.

**From the team tips.** Both `CLAUDE.md` and `AGENTS.md` are maintained with project conventions, coding standards and Kafka-specific patterns. Invest in them and update after every correction (tip #3). The `/techdebt` skill runs at the end of a session and is committed to the repo so the whole team benefits (tip #4). Specialised subagents (`code-reviewer`, `test-writer`, `doc-writer`) offload specific tasks to keep the main agent's context window clean (tip #8). The `code-reviewer` adopts a Staff Engineer persona, picking up on tip #2's advice of having "a second Claude review it as a staff engineer."

**From the customisation guide.** The default effort level is set explicitly so it can be tuned per workload (tip #2). Wildcard permission patterns like `Edit(src/**)` and `Bash(uv run pytest *)` pre-approve safe operations (tip #5). A Stop hook runs linting and tests when the agent finishes a turn, creating the verification feedback loop that materially improves output quality (tip #9). Kafka-themed spinner verbs make the tool feel like part of the team (tip #10). All settings are checked into `.claude/settings.json` so the whole team shares the same configuration (tip #12).

**From Anthropic's skill guide.** All skills follow the three-level progressive disclosure system (frontmatter → `SKILL.md` body → `references/`). Descriptions include trigger phrases so the agent knows when to load each skill, and frontmatter includes `license`, `metadata` (author, version, mcp-server) and `compatibility` fields per the open standard. Skills are categorised (`mcp-enhancement` for Kafka skills, `workflow-automation` for general skills) and include negative triggers to prevent over-triggering. Each skill defines quantitative and qualitative success criteria, and workflow steps include validation gates that stop or adjust the workflow if a step produces unexpected results. Every skill has a `references/test-cases.md` with three layers: triggering tests, functional Given/When/Then scenarios, and performance baselines (tool calls, errors, user corrections with vs without the skill).

## Resources

- [Lenses MCP Server for Apache Kafka](https://github.com/lensesio/lenses-mcp)
- [Lenses Community Edition](https://lenses.io/community-edition/)
- [Lenses documentation](https://docs.lenses.io/)
- [Anthropic's Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Cursor Skills documentation](https://cursor.com/docs/context/skills)
- [Cursor Subagents documentation](https://cursor.com/docs/context/subagents)
- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents documentation](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Settings documentation](https://code.claude.com/docs/en/settings)
- [Claude Code Hooks documentation](https://code.claude.com/docs/en/hooks)
- [Claude Code Permissions documentation](https://code.claude.com/docs/en/permissions)

## License

Released under the [MIT License](LICENSE). See the `LICENSE` file for the full text.
