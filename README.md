# 🌊 Agentic Engineering for Apache Kafka

Drop-in agent skills that turn your code editor into a Kafka-aware engineering assistant. Audit topic configurations, diagnose consumer lag, review schema changes, catch security misconfigurations and ship code - all from a single prompt instead of 15 minutes of manual investigation.

Built on best practices from Boris Cherny (creator of Claude Code), sourced from his [personal workflow](https://x.com/bcherny/status/2007179832300581177), [team tips](https://x.com/bcherny/status/2017742741636321619) and [customisation guide](https://x.com/bcherny/status/2021699851499798911). Ships with pre-configured agent skills and subagents for both **Cursor** and **Claude Code**. The customisation tips are naturally only supported in **Claude Code**. 

I code day to day in **Python** hence it's 🐍-centric, i.e. use of `uv`, `pytest` and `ruff` in hooks. For best performance, use [Lenses (Free Community Edition)](https://lenses.io/community-edition) and [Lenses MCP Server](https://github.com/lensesio/lenses-mcp). 

### Why MCP + Skills?

The [Lenses MCP server](https://github.com/lensesio/lenses-mcp) gives Claude **access** to your live Kafka cluster data - topics, consumer groups, connectors, schemas and metrics. The skills in this repo teach Claude **expertise** - your team's best practices, audit thresholds, remediation playbooks and standard workflows. Together they enable AI-powered Kafka engineering where Claude doesn't just read your cluster, it knows what to look for and how to fix it.

> ⚠️ NOTE: One of the tips is to adjust the effort level to `high`, for deeper reasoning and higher token consumption, but you are not Boris so I have set this to `medium`. Please adjust this accordingly in `settings.json` and if you're using Opus 4.6 you can also go all in with `max`.

## What's Included

### 📚 Agent Skills

| Skill | Invocation | Description | Source |
|-------|------------|-------------|--------|
| **Techdebt** | `/techdebt` | Scans the codebase for TODO/FIXME/HACK comments, commented out code, duplicated code, unused imports, inconsistent patterns and refactoring opportunities. Run this at the end of every session. | [Team tip #4](https://x.com/bcherny/status/2017742748984742078) |
| **Commit-Push-PR** | `/commit-push-pr` | Commits staged changes, pushes to remote and opens a PR in one step. Generates commit messages and PR descriptions from the diff. | [Personal tip #7](https://x.com/bcherny/status/2007179847949500714) |

### 🌊 Kafka Skills (powered by [Lenses MCP](https://github.com/lensesio/lenses-mcp))

| Skill | Invocation | Description | Frequency |
|-------|------------|-------------|-----------|
| **Topic Audit** | `/kafka-topic-audit` | Audits topic configs against best practices: replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata. | Daily/weekly |
| **Consumer Lag** | `/kafka-consumer-lag` | Analyses consumer group lag, diagnoses root causes (throughput bottlenecks, rebalancing, partition skew, stalled consumers) and suggests remediation. | Daily/on-incident |
| **Perf Review** | `/kafka-perf-review` | Reviews producer/consumer performance configs in both the live cluster and codebase. Flags un-tuned defaults, anti-patterns and missing best practices. | Per-change |
| **Schema Review** | `/kafka-schema-review` | Reviews schema changes (Avro, Protobuf, JSON Schema) for compatibility, breaking changes, missing defaults, naming issues and schema drift. | Per-PR |
| **Security Audit** | `/kafka-security-audit` | Audits authentication (SASL), encryption (SSL/TLS), secrets management and environment tier mismatches across codebase and cluster. | Monthly/pre-deploy |
| **Connector Review** | `/kafka-connector-review` | Reviews Kafka Connect configurations: error handling, DLQ setup, converters, transforms, task count and task health. | Per-change |
| **DLQ Review** | `/kafka-dlq-review` | Reviews dead letter queue completeness: topic config, monitoring, metadata preservation, retry logic, reprocessing paths and connector DLQ alignment. | Periodic |

### 🤖 Subagents

| Subagent | Role | Description | Source |
|----------|------|-------------|--------|
| **code-reviewer** | Staff Engineer | Reviews code changes for quality, security, architectural fit and Kafka best practices. Evaluates system-wide impact and long-term maintainability. | [Personal tip #8](https://x.com/bcherny/status/2007179850139000872) / [Team tip #8](https://x.com/bcherny/status/2017742755737555434) |
| **test-writer** | Test Engineer | Generates comprehensive pytest test suites with Kafka client mocks for unit tests and Docker-based integration tests. Targets >80% coverage. | [Team tip #8](https://x.com/bcherny/status/2017742755737555434) |
| **doc-writer** | Documentation Specialist | Generates Google-style docstrings, README files, module documentation and inline comments. Keeps docs in sync with code. | [Team tip #8](https://x.com/bcherny/status/2017742755737555434) |
| **code-simplifier** | Code Cleanup | Simplifies code after changes - flattens nested conditionals, removes dead branches, consolidates duplicated logic. Preserves behavior. | [Personal tip #8](https://x.com/bcherny/status/2007179850139000872) |

### 🪝 Hooks, Settings and Customisation (Claude Code)

| Feature | Description | Source |
|---------|-------------|--------|
| **PostToolUse formatting** | Auto-runs `ruff format` after every file Write/Edit to catch formatting issues before CI. | [Personal tip #9](https://x.com/bcherny/status/2007179852047335529) |
| **Stop hook for verification** | Runs `ruff check` and `pytest` when Claude finishes a turn, providing a feedback loop that 2-3x quality. | [Personal tip #13](https://x.com/bcherny/status/2007179861115511237) / [Customisation tip #9](https://x.com/bcherny/status/2021701059253874861) |
| **Effort level: high** | Maximum intelligence and token budget for every request. Boris: "I use High for everything." | [Customisation tip #2](https://x.com/bcherny/status/2021699860869902424) |
| **Pre-allowed permissions** | Wildcard patterns for safe commands (`uv run pytest *`, `Edit(src/**)`, `gh pr *`) reduce permission prompts. | [Personal tip #10](https://x.com/bcherny/status/2007179854077407667) / [Customisation tip #5](https://x.com/bcherny/status/2021700332292911228) |
| **Custom spinner verbs** | Kafka-themed spinner verbs for team personality ("Producing messages", "Committing offsets", etc.). | [Customisation tip #10](https://x.com/bcherny/status/2021701145023197516) |

### Cursor and Claude Code Support

Every skill and subagent is implemented for both Cursor and Claude Code. The customisations are only supported in Claude Code. 

There is duplication but only because there is currently no standard for skills (it's like the wild west early MCP days) so each tool has its nuances:

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

The Claude Code variants include additional configuration: explicit tool restrictions, model routing (`sonnet`), persistent `memory: project` for cross-session learning, inline bash pre-computation in skills, PostToolUse + Stop hooks, effort level, wildcard permissions and custom spinner verbs, all configured in `.claude/settings.json`.

All skills follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure: frontmatter with trigger phrases, negative triggers and categorised metadata, a `references/` directory for detailed lookup tables and test cases loaded on demand, success criteria with quantitative and qualitative metrics, concrete usage examples, troubleshooting for common errors and validation gates between workflow steps.

## Quick Start

### Installation

#### For Cursor

1. Copy `.cursor/` and `AGENTS.md` to your project root
2. If using Kafka skills, configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in Cursor's MCP settings
3. Verify by asking: *"Run a topic audit on staging"* (or any environment name)

#### For Claude Code

1. Copy `.claude/` and `CLAUDE.md` to your project root
2. If using Kafka skills, configure the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) in your Claude Code MCP settings
3. Verify by asking: *"Run a topic audit on staging"* (or any environment name)

#### For Claude.ai

1. Download the individual skill folder you want (e.g. `kafka-topic-audit/`)
2. Zip the folder
3. Open Claude.ai > Settings > Capabilities > Skills
4. Click "Upload skill" and select the zipped folder
5. Ensure your Lenses MCP server is connected (for Kafka skills)
6. Verify by asking: *"Run a topic audit on staging"*

#### Via API

For programmatic use cases (applications, agents, automated pipelines), skills can be added to Messages API requests via the `container.skills` parameter. See Anthropic's [Skills API Quickstart](https://docs.anthropic.com/en/docs/agents-and-tools/skills) for implementation details.

Having trouble? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues (upload errors, triggering problems, MCP connection failures).

## Using the Agentic Workflows

### Skills

#### Techdebt Slash Command

Run at the end of every coding session to find and eliminate technical debt:

```
/techdebt        # Scan src/ and tests/
/techdebt src/   # Scan a specific directory
```

The skill produces a categorised report:

- **Critical** - Must fix (duplicated logic, security issues)
- **Warning** - Should fix (dead code, unused imports)
- **Suggestion** - Consider improving (refactoring opportunities)

#### Commit-Push-PR

Ship code in one step - commit, push and open a PR:

```
/commit-push-pr
```

The skill:

- Pre-computes git status, current branch and diff (Claude Code uses inline bash)
- Generates a conventional commit message from the diff
- Pushes to remote (creating the branch if needed)
- Opens a PR with a generated title and summary via `gh`

### Kafka Skills

These skills require the [Lenses MCP server](https://github.com/lensesio/lenses-mcp) to be configured and connected to your Kafka environment. They combine live cluster data with codebase inspection.

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

Detects breaking changes, missing defaults, schema drift between repo and cluster and naming issues.

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

### Test Writer

Generate tests for new or changed code:

```
Use the test-writer to add tests for src/kafka/producer.py
```

Produces:

- pytest-based unit tests with Kafka client mocks
- Integration tests marked with `@pytest.mark.integration`
- Reusable fixtures in `tests/conftest.py`
- Coverage report targeting >80%

### Doc Writer

Generate or update documentation:

```
Use the doc-writer to document src/kafka/
```

Produces:

- Google-style docstrings with Args, Returns, Raises and Example sections
- Module-level docstrings explaining purpose and typical usage
- README updates reflecting current code behavior

### Code Simplifier

Run after completing a feature or fix to clean up the code:

```
Use the code-simplifier to clean up my recent changes
```

Performs:

- Flattens deeply nested conditionals with early returns
- Removes dead code branches and unnecessary intermediate variables
- Consolidates duplicated logic into shared utilities
- Preserves all external behavior (simplification only, no functional changes)
- Runs tests after each significant change to verify correctness

## Conventions

### Code Style

- `snake_case` for functions, variables and file names
- `PascalCase` for class names
- `UPPER_SNAKE_CASE` for constants
- Type hints and Google-style docstrings on all public functions
- 100-character maximum line length
- Absolute imports within the project

### Kafka

- Topic names: `<domain>.<entity>.<event>` (e.g., `orders.payment.completed`)
- Consumer group IDs: `<service-name>-<purpose>` (e.g., `analytics-order-processor`)
- Explicit serialisers/deserialisers (no implicit defaults)
- Idempotent producers where possible
- Context managers for all producers and consumers
- Graceful shutdown with signal handlers

### Git

- Branch naming: `feature/`, `fix/`, `docs/`, `refactor/`
- Descriptive commit messages
- Atomic, focused commits
- Squash WIP commits before merging

## Background: Agentic Engineering, Boris Cherny's Best Practices and Anthropic's Skill Guide

This repository is an example of Agentic Engineering, where AI agents handle implementation with engineering rigor under human oversight, as distinct from "vibe coding" where output goes unreviewed. The human directs, reviews and owns the codebase; the AI agents accelerate the work through pre-configured skills, subagents and workflows.

It implements practices from three X posts by Boris Cherny (creator of Claude Code) and Anthropic's official [Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf):

- [Personal workflow](https://x.com/bcherny/status/2007179832300581177) (2 Jan 2026) - 13 tips on how Boris personally uses Claude Code
- [Team tips](https://x.com/bcherny/status/2017742741636321619) (1 Feb 2026) - 10 tips from the Claude Code team
- [Customisation guide](https://x.com/bcherny/status/2021699851499798911) (11 Feb 2026) - 12 tips on customising Claude Code

### From the personal workflow

- **Tip #7 - Slash commands for inner loops**: The `/commit-push-pr` skill automates commit, push and PR creation. Boris uses this "dozens of times every day."
- **Tip #8 - Subagents for common workflows**: The `code-simplifier` subagent cleans up code after Claude finishes working, just like Boris's own `code-simplifier` agent.
- **Tip #9 - PostToolUse hooks**: A formatting hook auto-runs `ruff format` after every file edit, catching the last 10% of formatting issues before CI.
- **Tip #10 - Pre-allow safe permissions**: Common safe commands are pre-approved in `.claude/settings.json` to avoid unnecessary permission prompts.
- **Tip #13 - Verification**: The single most important tip - always give the AI agent a way to verify its work. This is reflected in the test-writer and code-reviewer subagents and now in the Stop hook.

### From the team tips

- **Tip #3 - Invest in CLAUDE.md / AGENTS.md**: Both memory files are maintained with project conventions, coding standards and Kafka-specific patterns. After every correction, update them so the AI agent doesn't repeat mistakes.
- **Tip #4 - Create your own skills**: The `/techdebt` slash command runs at the end of every session to find and kill duplicated code. Skills are committed to git so the whole team benefits.
- **Tip #8 - Use subagents**: Specialised subagents (`code-reviewer`, `test-writer`, `doc-writer`) offload specific tasks to keep the main agent's context window clean and focused. The code reviewer adopts a Staff Engineer persona per tip #2's advice of having "a second Claude review it as a staff engineer."

### From the customisation guide

- **Tip #2 - Effort level**: Set to "high" for maximum intelligence. Boris: "I use High for everything."
- **Tip #5 - Wildcard permissions**: Use patterns like `Edit(src/**)` and `Bash(uv run pytest *)` to pre-approve safe operations with full wildcard syntax.
- **Tip #9 - Hooks for verification**: A Stop hook runs linting and tests when Claude finishes a turn, creating the verification feedback loop that 2-3x result quality.
- **Tip #10 - Custom spinner verbs**: Kafka-themed verbs ("Producing messages", "Committing offsets") make the tool feel personal to the team.
- **Tip #12 - Check settings into git**: All settings live in `.claude/settings.json` so the whole team benefits from the same configuration.

### From Anthropic's skill guide

- **Chapter 1 - Fundamentals**: All skills follow the three-level progressive disclosure system (frontmatter -> SKILL.md body -> references/). Descriptions include trigger phrases so Claude knows when to load each skill. Frontmatter includes `license`, `metadata` (author, version, mcp-server) and `compatibility` fields per the open standard. Each skill has an Examples section and a Troubleshooting section.
- **Chapter 2 - Planning and design**: Skills are categorised (`mcp-enhancement` for Kafka skills, `workflow-automation` for general skills) and include negative triggers to prevent over-triggering ("Do NOT use for X"). Each skill defines quantitative and qualitative success criteria. Workflow steps include expected output descriptions and validation gates - explicit checkpoints that stop or adjust the workflow if a step produces unexpected results.
- **Chapter 3 - Testing and iteration**: Every skill has a `references/test-cases.md` with three testing layers: triggering tests (should/should not trigger query lists), functional tests (Given/When/Then scenarios) and performance baselines (tool calls, errors, user corrections with vs without the skill). These test cases support manual testing in Claude.ai, scripted testing in Claude Code and programmatic evaluation via the skills API.
- **Chapter 4 - Distribution and sharing**: README follows the recommended distribution pattern - outcome-focused positioning ("turn your code editor into a Kafka-aware engineering assistant"), platform-specific installation guides (Cursor, Claude Code, Claude.ai, API) with verification steps and the MCP + Skills narrative explaining why both together are more valuable than either alone. Skills follow the open standard for portability across tools and platforms.
- **Chapter 5 - Patterns and troubleshooting**: Each skill's metadata classifies its `approach` (problem-first or tool-first) and architecture `patterns` (sequential-workflow, iterative-refinement, context-aware-selection, domain-intelligence). A shared `TROUBLESHOOTING.md` covers general platform issues (upload errors, triggering problems, MCP connection failures, instructions not followed, large context) while each SKILL.md retains its own skill-specific troubleshooting section.

## Resources

- [Anthropic - The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Lenses MCP Server for Apache Kafka](https://github.com/lensesio/lenses-mcp)
- [Lenses Community Edition](https://lenses.io/community-edition)
- [Cursor Skills Documentation](https://cursor.com/docs/context/skills)
- [Cursor Subagents Documentation](https://cursor.com/docs/context/subagents)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Settings Documentation](https://code.claude.com/docs/en/settings)
- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [Claude Code Permissions Documentation](https://code.claude.com/docs/en/permissions)

## License

[MIT](https://opensource.org/license/mit)