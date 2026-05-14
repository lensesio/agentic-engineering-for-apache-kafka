# AGENTS.md

## Project Overview

Agentic Kafka engineering tools and utilities. This project provides tooling to help engineers work with Apache Kafka more effectively using AI assistance. It ships with pre-configured Kafka-specific agent skills for both **Cursor** and **Claude Code**.

## Tech Stack

- **Language**: Python 3.13+
- **Package Manager**: uv
- **Kafka Client**: confluent-kafka
- **AI/LLM**: Claude API (Anthropic)
- **Testing**: pytest
- **Linting**: ruff

## Project Structure

```
├── AGENTS.md                # Cursor agent memory (this file)
├── CLAUDE.md                # Claude Code agent memory
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Locked dependency versions
├── src/
│   ├── kafka/               # Kafka producers, consumers, admin utilities
│   ├── ai/                  # AI/LLM integration and prompts
│   ├── cli/                 # Command-line interface
│   └── utils/               # Shared utilities
├── tests/
│   ├── unit/                # Unit tests (mirrors src/ structure)
│   └── integration/         # Integration tests (require Docker Kafka)
├── config/                  # Configuration templates
├── docs/                    # Documentation
├── scripts/                 # Helper scripts
├── .cursor/
│   └── skills/
│       ├── topic-audit/           # Topic config audit
│       │   └── references/              #   audit-rules.md, test-cases.md
│       ├── consumer-lag/          # Consumer lag analysis
│       │   └── references/              #   test-cases.md
│       ├── perf-review/           # Performance review
│       │   └── references/              #   producer-defaults.md, consumer-defaults.md, test-cases.md
│       ├── schema-review/         # Schema evolution review
│       │   └── references/              #   compatibility-rules.md, test-cases.md
│       ├── security-audit/        # Security posture audit
│       │   └── references/              #   security-properties.md, test-cases.md
│       ├── connector-review/      # Kafka Connect config review
│       │   └── references/              #   test-cases.md
│       └── dlq-review/            # Dead letter queue review
│           └── references/              #   test-cases.md
├── .claude/
│   ├── settings.json                    # Repo-local: hooks, permissions, effort, spinner verbs (NOT shipped via plugin)
│   └── hooks/                           # Repo-local hooks (e.g. ruff-format.sh)
├── .claude-plugin/
│   └── marketplace.json                 # Claude Code marketplace catalog (lists kafka-skills)
└── plugins/
    └── kafka-skills/                    # Installable Claude Code plugin
        ├── .claude-plugin/plugin.json   # Plugin manifest (name, version, author, license)
        ├── README.md                    # Plugin-level readme
        └── skills/
            ├── topic-audit/           # Topic config audit
            │   └── references/              #   audit-rules.md, test-cases.md
            ├── consumer-lag/          # Consumer lag analysis
            │   └── references/              #   test-cases.md
            ├── perf-review/           # Performance review
            │   └── references/              #   producer-defaults.md, consumer-defaults.md, test-cases.md
            ├── schema-review/         # Schema evolution review
            │   └── references/              #   compatibility-rules.md, test-cases.md
            ├── security-audit/        # Security posture audit
            │   └── references/              #   security-properties.md, test-cases.md
            ├── connector-review/      # Kafka Connect config review
            │   └── references/              #   test-cases.md
            └── dlq-review/            # Dead letter queue review
                └── references/              #   test-cases.md
```

The Claude Code Kafka skills ship as a single plugin (`kafka-skills`) via the in-repo marketplace catalog (`lensesio`). Install with `/plugin marketplace add lensesio/agentic-engineering-for-apache-kafka` then `/plugin install kafka-skills@lensesio`. After install, skills are namespaced as `/kafka-skills:<skill-name>`. The parallel `.cursor/skills/` tree mirrors the same skill names without the plugin namespace - Cursor uses its own ecosystem.

## Skill Structure Conventions

All skills follow the [Anthropic open standard](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure:

- **YAML frontmatter** includes `name`, `description` (with trigger phrases and negative triggers), `license`, `metadata` (author, version, mcp-server, category) and `compatibility` (for MCP skills)
- **SKILL.md body** contains the workflow steps (with expected output notes and validation gates), success criteria, examples and troubleshooting
- **`references/` directory** holds detailed lookup tables and domain rules that Claude loads on demand (e.g., audit thresholds, config defaults, compatibility matrices)
- Each skill includes a **Success Criteria** section with quantitative and qualitative metrics
- Each skill includes an **Examples** section with concrete "User says X -> Claude does Y" scenarios
- Each skill includes a **Troubleshooting** section for common errors and edge cases
- Skills are categorised as `workflow-automation` or `mcp-enhancement` in their metadata
- Every skill has a `references/test-cases.md` with triggering tests (should/should not trigger), functional tests (Given/When/Then) and performance baselines
- Skills follow the [Anthropic open standard](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and are portable across Claude.ai, Claude Code, Cursor and the API (`/v1/skills` endpoint)
- Each skill's metadata includes `approach` (problem-first or tool-first) and `patterns` (sequential-workflow, iterative-refinement, context-aware-selection, domain-intelligence)
- General troubleshooting (upload errors, triggering issues, MCP connection failures, large context) is in `TROUBLESHOOTING.md` at the repo root; skill-specific troubleshooting is in each SKILL.md

## Kafka Skills (powered by Lenses MCP)

This project ships pre-configured Kafka skills, all observed against the [Lenses MCP server](https://github.com/lensesio/lenses-mcp):

- **`/topic-audit`** - Audit topic configs against best practices: replication factor, retention, partitions, compaction, naming conventions, orphaned topics and missing metadata.
- **`/consumer-lag`** - Analyse consumer group lag, diagnose root causes and suggest remediation.
- **`/perf-review`** - Review producer/consumer performance configs in both the live cluster and codebase.
- **`/schema-review`** - Review schema changes for compatibility, breaking changes, missing defaults and schema drift.
- **`/security-audit`** - Audit authentication, encryption, secrets management and environment tier mismatches.
- **`/connector-review`** - Review Kafka Connect configurations: error handling, DLQ setup, converters, transforms and task health.
- **`/dlq-review`** - Review dead letter queue completeness: topic config, monitoring, metadata preservation and reprocessing paths.

## Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates venv automatically)
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your Kafka and API credentials
```

## Common Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Lint code
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Type checking
uv run mypy src/

# Add a dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Update dependencies
uv lock --upgrade
uv sync
```

## Coding Conventions

- Use `snake_case` for functions, variables and file names
- Use `PascalCase` for class names
- Use `UPPER_SNAKE_CASE` for constants
- All public functions require type hints and docstrings (Google style)
- Maximum line length: 100 characters
- Use absolute imports within the project

## Kafka Conventions

- Topic names: `<domain>.<entity>.<event>` (e.g., `orders.payment.completed`)
- Consumer group IDs: `<service-name>-<purpose>` (e.g., `analytics-order-processor`)
- Always specify explicit serialisers/deserialisers
- Use idempotent producers when possible
- Handle rebalancing gracefully in consumers

## Testing

- Unit tests go in `tests/unit/`
- Integration tests go in `tests/integration/`
- Use fixtures for Kafka client mocks (see `tests/conftest.py`)
- Integration tests require a running Kafka instance (use Docker)
- Mark integration tests with `@pytest.mark.integration`
- Aim for >80% code coverage on new code

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker addresses | Yes |
| `KAFKA_SECURITY_PROTOCOL` | Security protocol (PLAINTEXT, SSL, SASL_SSL) | No |
| `ANTHROPIC_API_KEY` | Claude API key | Yes |

## Important Patterns

- Use context managers for Kafka producers/consumers
- Implement graceful shutdown with signal handlers
- Log all Kafka connection events and errors
- Use structured logging (JSON format in production)
- Retry transient failures with exponential backoff
- Always give the AI agent a way to verify its work (run tests, lint, type check). This 2-3x the quality of the result

## Things to Avoid

- Don't commit `.env` files or credentials
- Don't hardcode broker addresses or topics
- Don't ignore Kafka delivery callbacks
- Don't create consumers without proper error handling
- Don't use `auto.offset.reset=latest` without understanding implications
- Avoid synchronous produce calls in hot paths
- Don't use `pip install` directly; use `uv add` to manage dependencies
- Don't forget to commit `uv.lock` (it ensures reproducible builds)

## Git Workflow

- Branch naming: `feature/`, `fix/`, `docs/`, `refactor/`
- Write descriptive commit messages
- Keep commits atomic and focused
- Squash WIP commits before merging

## Resources

- [Lenses MCP Server](https://github.com/lensesio/lenses-mcp)
- [Lenses Documentation](https://docs.lenses.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Anthropic - The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Boris Cherny - Personal workflow tips](https://x.com/bcherny/status/2007179832300581177)
- [Boris Cherny - Team tips](https://x.com/bcherny/status/2017742741636321619)
- [Boris Cherny - Customisation guide](https://x.com/bcherny/status/2021699851499798911)
