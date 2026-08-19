# Contributing to Agentic Engineering for Apache Kafka

First, thank you for considering a contribution. This repository is a community resource for engineers who run Apache Kafka in production, and it gets meaningfully better every time someone shares a skill, a fix or an honest bug report. No single team has seen every Kafka problem, and the best skills in this repo will come from people who have lived through one and want to spare the next engineer the pain.

This document covers how to participate, whether you want to file an issue, propose a new Kafka skill, fix a typo or become a regular contributor.

> **TL;DR.** Open an issue first for anything non-trivial, particularly a complex new skill. Fork the repo, work on a topic branch, follow the [Skill structure conventions](#skill-structure-conventions) if you are touching a skill, and open a PR with a clear description and a test case. We aim to triage within a few working days.

## Table of contents

- [Code of conduct](#code-of-conduct)
- [Ways to contribute](#ways-to-contribute)
- [Before you start](#before-you-start)
- [Reporting bugs](#reporting-bugs)
- [Suggesting a new skill or feature](#suggesting-a-new-skill-or-feature)
- [Your first contribution](#your-first-contribution)
- [Development workflow](#development-workflow)
- [Skill structure conventions](#skill-structure-conventions)
- [Evals](#evals)
- [Testing your changes](#testing-your-changes)
- [Pull request process](#pull-request-process)
- [Commit and branch conventions](#commit-and-branch-conventions)
- [Sign-off and licensing](#sign-off-and-licensing)
- [Style guide](#style-guide)
- [Where to get help](#where-to-get-help)
- [Recognition](#recognition)

## Code of conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold a respectful, inclusive environment. Please report unacceptable behaviour to the maintainers via the contact channels listed in [Where to get help](#where-to-get-help).

## Ways to contribute

There are many ways to help, and writing code is only one of them. All of these are valuable:

- **Report a bug** — a skill that does not trigger, an MCP call that fails, a hook that misbehaves, broken docs.
- **Improve documentation** — fix a typo, clarify a workflow step, add a worked example, expand a troubleshooting entry.
- **Improve an existing skill** — better trigger phrases, more accurate audit thresholds, sharper remediation advice, additional reference material in `references/`, or new test cases in `references/test-cases.md`.
- **Propose a new Kafka skill** — Schema Registry workflows, cluster upgrades, capacity planning, ACL audits, quota tuning, tiered storage review, Kafka Streams or ksqlDB workflows, MirrorMaker review and many more are all good candidates.
- **Share a real-world story** — if you used a skill in anger and learnt something, open an issue or a discussion. That signal directly improves the next iteration.
- **Triage issues** — reproduce, label and link related issues. This is one of the highest-leverage things a community member can do.

## Before you start

For anything beyond a small fix, **please open or comment on an issue first**. This avoids duplicated effort and gives maintainers a chance to flag design constraints early. Specifically:

- For **bug fixes that touch a single file or a docs typo**, you can go straight to a PR.
- For **new skills, new hooks, new MCP variants or changes to skill structure conventions**, please open an issue first describing the proposal. We will discuss approach, scope and where it fits in the existing surface, then you can implement with confidence.
- For **breaking changes** to the plugin layout (`.claude-plugin/`, `.cursor-plugin/`, `skills/`, `assets/`) or the Anthropic open-standard frontmatter, an issue is mandatory.

If you are unsure which category your change falls into, open an issue and ask. We would rather have a short discussion up front than ask you to rework an otherwise good PR.

## Reporting bugs

Use the [GitHub Issues](https://github.com/lensesio/agentic-engineering-for-apache-kafka/issues) tracker. Before opening a new issue, please search existing issues (open and closed) to avoid duplicates. If you find one that matches, add a 👍 reaction or a comment with your reproduction so we can prioritise.

A good bug report includes:

1. **Environment** — Cursor or Claude Code (and version), OS, model in use (Sonnet, Opus, GPT, etc.), MCP server version where relevant.
2. **Skill affected** — for example, `/kafka-topic-audit`.
3. **What you expected to happen.**
4. **What actually happened**, including any agent output. Redact secrets, broker addresses and customer data before pasting.
5. **Reproduction steps** — the exact prompt, the relevant repo state, and any MCP environment context.
6. **Logs and screenshots** where they help. For MCP failures, the MCP server logs are gold.

If you can reproduce the issue with a minimal example, that triples the chance of a fast fix.

## Suggesting a new skill or feature

Open a feature request issue and include:

1. **The problem.** Describe the Kafka pain point in plain language. What is the engineer trying to do? What slows them down today?
2. **The proposed skill or change.** Skill name (kebab-case), one-paragraph description, expected trigger phrases, negative triggers, and the kind of MCP tools or codebase inspection it would need.
3. **Audit rules or domain knowledge.** What thresholds, defaults or playbooks should the skill encode? This is the content that goes into `references/`.
4. **Success criteria.** How will we know the skill is working? Quantitative (number of findings, false-positive rate) and qualitative (does the agent now ask the right follow-up questions?).
5. **Examples.** Two or three "User says X → Claude does Y" scenarios.

If the proposal is accepted, you can either implement it yourself or leave it tagged `help wanted` for someone else to pick up.

## Your first contribution

Looking for somewhere to start? These are usually a good entry point:

- Issues labelled [`good first issue`](https://github.com/lensesio/agentic-engineering-for-apache-kafka/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and [`help wanted`](https://github.com/lensesio/agentic-engineering-for-apache-kafka/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).
- **Add a worked example** to a skill's SKILL.md.
- **Add a test case** to a skill's `references/test-cases.md` that covers a real situation you have encountered.
- **Improve a description** so a skill triggers more reliably for phrasing your team actually uses.
- **Tighten reference material** in `references/` (audit thresholds, default values, compatibility matrices) when you spot something out of date.
- **Tighten a SKILL.md description or trigger phrase** in `skills/<name>/SKILL.md` based on real-world prompt wording you have seen.

If you are new to the project and unsure where to start, open a discussion or comment on an issue and ask. We will help you find something the right size.

## Development workflow

We use the standard [fork-and-pull workflow](https://github.com/susam/gitpr).

1. **Fork** the repository to your own GitHub account.
2. **Clone** your fork:
   ```bash
   git clone git@github.com:<your-username>/agentic-engineering-for-apache-kafka.git
   cd agentic-engineering-for-apache-kafka
   ```
3. **Add the upstream remote** so you can pull in changes:
   ```bash
   git remote add upstream git@github.com:lensesio/agentic-engineering-for-apache-kafka.git
   ```
4. **Create a topic branch** with a descriptive name (see [Commit and branch conventions](#commit-and-branch-conventions)):
   ```bash
   git checkout -b feature/capacity-planning
   ```
5. **Make your changes**, keeping the diff focused on one concern.
6. **Test your changes** — see [Testing your changes](#testing-your-changes).
7. **Commit** using descriptive messages and sign your commits (`-s`); see [Sign-off and licensing](#sign-off-and-licensing).
8. **Push** to your fork and open a Pull Request against `main`.

Most contributions to this repository are Markdown and YAML, so no build step is required.

### Adding a new skill

Every skill lives in a single source of truth at `skills/<skill-name>/` at the repo root. The same `SKILL.md` is consumed by both the Claude Code plugin (via `.claude-plugin/plugin.json`) and the Cursor plugin (via `.cursor-plugin/plugin.json`). Cursor silently ignores Claude-Code-specific frontmatter fields, so there is no duplicate Cursor tree to maintain.

To scaffold a new skill:

1. Pick a kebab-case `name` (for example `kafka-streams-review`).
2. Create the folder:
   ```
   skills/<name>/SKILL.md
   skills/<name>/references/test-cases.md
   ```
3. Use an existing skill (for example `kafka-topic-audit`) as a template. Match the frontmatter fields, the section ordering and the progressive disclosure pattern.
4. Add the skill to the tables in `README.md` and `AGENTS.md`.
5. Add the new skill's path (for example `./skills/<name>`) to the `skills` array in **both** [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) and [`.cursor-plugin/marketplace.json`](.cursor-plugin/marketplace.json). That array is the canonical published surface for the Claude Code marketplace and for the [`npx skills add`](https://github.com/vercel-labs/skills) install path; without it, the new skill will not be exposed to either channel.
6. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) so you avoid the most common authoring mistakes (frontmatter, trigger phrases, over-triggering).
7. Bump the plugin version in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) (typically a minor bump for a new skill) so existing users get the new skill on their next `/plugin update` or `npx skills update`. See [Releasing the Claude Code plugin](#releasing-the-claude-code-plugin).

## Skill structure conventions

All skills must follow the [Anthropic open standard for skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) with progressive disclosure. Concretely:

- **YAML frontmatter** read by both ecosystems: `name`, `description` (including trigger phrases and negative triggers), `license`, `metadata` (author, version, mcp-server, category, approach, patterns, tags), `compatibility` (for MCP skills).
- **Claude-Code-only frontmatter** (still kept in the same `SKILL.md`, ignored by Cursor): `allowed-tools` to restrict the tool surface, `argument-hint` to document expected arguments, and `disable-model-invocation: true` for skills that should only run on explicit invocation.
- **SKILL.md body** with workflow steps that include expected output notes and validation gates, a Success Criteria section with quantitative and qualitative metrics, an Examples section with concrete "User says X → Claude does Y" scenarios, and a Troubleshooting section for skill-specific edge cases.
- **`references/` directory** for detailed lookup tables loaded on demand (audit thresholds, config defaults, compatibility matrices). Keep `SKILL.md` itself under ~5,000 words; offload depth to `references/`.
- **`references/test-cases.md`** with three layers:
  - Triggering tests (should trigger / should not trigger phrases).
  - Functional tests in Given/When/Then form.
  - Performance baselines (tool calls, errors and user corrections, with vs without the skill).
- **Skill category** in metadata: `workflow-automation` or `mcp-enhancement`.
- **Negative triggers** in the description ("Do NOT use for X") so the skill stays sharply scoped.

A single `SKILL.md` per skill serves both Cursor and Claude Code. Claude-Code-only frontmatter (`allowed-tools`, `argument-hint`, `disable-model-invocation`) and Claude-Code substitution tokens (`$ARGUMENTS`) live alongside the shared content; Cursor reads only the fields it understands and treats unknown frontmatter as a no-op. Avoid creating a separate Cursor-flavoured copy of any skill - keep one source of truth.

For a fuller treatment, see the [Skill Structure Conventions](AGENTS.md#skill-structure-conventions) section in `AGENTS.md`.

## Evals

Alongside the human-run test plan in `references/test-cases.md`, skills can (and new skills should) ship a machine-gradeable eval suite in `skills/<name>/evals/`, following the [agentskills.io evaluating-skills format](https://agentskills.io/skill-creation/evaluating-skills). The reference implementation is [`skills/kafka-python-client/evals/`](skills/kafka-python-client/evals/).

The layout:

- **`evals/evals.json`** — the suite itself: for each test case an `id`, a `name`, a realistic `prompt` (the kind of thing a user would actually type — vary formality and detail across cases), a human-readable `expected_output`, optional input `files`, and a list of `expectations`. We use the `expectations` field name (rather than the `assertions` alias some tooling accepts) to line up with Anthropic's [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator), which is the recommended way to run these suites.
- **`evals/files/`** (optional) — input fixtures a test case needs, referenced by relative path from the skill directory. Keep fixtures minimal.
- **No separate setup doc.** The environment prerequisites `skill-creator` cannot infer are encoded where it actually reads them — the top-level `description` in `evals.json` (cluster bring-up command, Kafka MCP, `uv`, fresh-context requirement) plus each case's `prompt`/`expected_output`/`files` — so an agent running a benchmark has everything from `evals.json` alone, with no sidecar file to drift out of sync. Human run/install guidance lives here in this section.

Conventions, informed by the agentskills.io guide and [OpenAI's eval-skills guidance](https://developers.openai.com/blog/eval-skills):

1. **Target Lenses CE seed data.** Evals must run against an out-of-the-box local Lenses Community Edition with no bespoke seeding. This repo does not check in a `docker-compose.yml` — fetch the official one fresh from the [Lenses Community Edition page](https://lenses.io/community-edition) as part of the run (`curl -L https://lenses.io/preview -o docker-compose.yml && ACCEPT_EULA=true docker compose up -d --wait`), so evals always test against the current CE release rather than a copy that can drift. Default to the `nyc_yellow_taxi_trip_data` topic; use the other telemetry seed topics (`sea_vessel_position_reports`, `telecom_italia_data`, `backblaze_smart`) where they add distinct coverage.
2. **Expectations must be objectively gradeable.** "The generated producer sets `enable.idempotence=true`" is checkable; "the output is production-ready" is not. Prefer checks a script or a fresh LLM grader can verify from the outputs alone, and require concrete evidence for a PASS. (The `evals[].expectations` array and the `grading.json` rows that grade them use the fields `text`/`passed`/`evidence`, matching `skill-creator`'s `eval-viewer`.)
3. **Don't restate the skill's own wording.** Assert on observable outcomes (files produced, configs set, questions asked, live-cluster values echoed correctly), not on the skill's internal instructions.
4. **Include at least one negative control** — a prompt that should *not* trigger the skill — to catch over-triggering.
5. **Cover at least one edge case** where the skill must stop and ask rather than guess (missing schema, ambiguous topic).
6. **Run with a baseline.** Each iteration runs every case twice in fresh contexts — with the skill and without (or against a snapshot of the previous skill version) — so the delta shows what the skill actually buys. Keep run artifacts in a `<skill>-workspace/` directory (gitignored) or outside the repo entirely; only `evals/` itself is part of the published payload.
7. **Run the suites with `skill-creator`.** The recommended runner is Anthropic's [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill, which spawns the fresh per-run contexts, grades every `expectation`, and aggregates `benchmark.json` for you. It is a development tool, not part of the published payload — install it at project scope in the gitignored `.claude/skills/skill-creator/` (never under the shipped `skills/` tree or a committed `.cursor/skills/` tree). The install snippet:

   ```bash
   git clone --depth 1 --filter=blob:none --sparse https://github.com/anthropics/skills /tmp/anthropic-skills
   git -C /tmp/anthropic-skills sparse-checkout set skills/skill-creator
   mkdir -p .claude/skills && cp -R /tmp/anthropic-skills/skills/skill-creator .claude/skills/skill-creator
   ```

   Then, from a Claude Code session at the repo root, ask: *"Use skill-creator to run the evals in `skills/kafka-python-client/evals/evals.json` against my local Lenses CE, with a with-skill vs without-skill baseline."*
8. **Keep evals and `references/test-cases.md` aligned.** The test-cases file remains the human-readable test plan; the evals automate it. Changing skill behaviour means updating both.

## Testing your changes

There is no unit test runner for skill content itself, so we rely on a few lightweight checks. Please run through these before opening a PR:

1. **Trigger tests.** In a session with the skill loaded, ask the questions listed in `references/test-cases.md`. Verify that "should trigger" prompts load the skill and "should not trigger" prompts do not.
2. **Functional tests.** Walk through at least the primary Given/When/Then scenario. Verify the agent follows the workflow steps, calls the expected MCP tools, and produces output in the documented shape.
   If the skill ships an eval suite (see [Evals](#evals)), run at least the primary eval case with the skill against a local Lenses CE (via `skill-creator`, or by hand) and check its expectations pass.
3. **Self-check via the agent.** Ask Claude (or Cursor's agent): *"When would you use the `<skill-name>` skill?"* The answer should match the description. If not, the description needs more specific trigger phrases.
4. **Cross-tool sanity.** Verify the skill in both Cursor and Claude Code. If you only have access to one, say so in the PR and a maintainer will verify the other.
5. **Skills CLI sanity** (optional but encouraged). From a clean directory, run `npx skills add lensesio/agentic-engineering-for-apache-kafka --list` against your branch's fork to confirm the new skill is discovered, then `npx skills add … --skill <name> -y` to confirm it installs cleanly into a per-agent folder. This catches `skills` array typos in the marketplace manifests early.
6. **Markdown sanity.** Render the changed files locally or in the GitHub web UI to catch broken links and table formatting.

If your change introduces a regression in trigger reliability or workflow output, please mention it in the PR so we can discuss tradeoffs explicitly.

## Pull request process

A good PR is small, focused and easy to review. To make ours an easy "yes":

- **One concern per PR.** A new skill, a docs improvement and a connector fix should be three PRs.
- **Title** uses [Conventional Commits](https://www.conventionalcommits.org/) (see below). The title is what ends up in the squashed commit message.
- **Description** explains *why* the change is needed and *what* a reviewer should look at first. If your PR is the implementation of a previously discussed issue, link it with `Closes #123`. Include before/after agent transcripts where useful.
- **Reference test cases.** If you added or modified a skill, point to the test cases you ran in the PR description.
- **Keep the diff readable.** Avoid drive-by formatting changes in unrelated files.
- **Update docs.** If your change affects user-facing behaviour, update `README.md`, `AGENTS.md` and `TROUBLESHOOTING.md` as appropriate.
- **Sign your commits.** See [Sign-off and licensing](#sign-off-and-licensing).

### Review process

- A maintainer will triage your PR within a few working days. If you have not heard back after a week, feel free to ping the PR.
- Reviews focus on: correctness of skill behaviour, clarity of descriptions and trigger phrases, depth and accuracy of `references/`, behaviour parity between Cursor and Claude Code (since both consume the same `SKILL.md`), and overall fit with existing conventions.
- We may ask for changes. We try to bundle review comments rather than drip-feed them. If a reviewer is asking for something that feels at odds with another comment, please call it out.
- Once two maintainers approve (or one maintainer for low-risk changes), we will squash and merge.

### What gets rejected

We will push back on PRs that:

- Add a skill that overlaps significantly with an existing one without a clear differentiator.
- Introduce a parallel skill tree outside `skills/` at the repo root (we deliberately maintain a single source of truth for both Cursor and Claude Code).
- Hardcode broker addresses, topic names, credentials or environment names.
- Embed long reference material inline in `SKILL.md` instead of using `references/`.
- Significantly inflate `SKILL.md` past the recommended size without justification.
- Lack test cases (`references/test-cases.md` is required for new skills).

None of these are personal — they are usually a sign that a short discussion in an issue would have helped. We will say so explicitly and try to suggest the smallest change that gets the PR over the line.

## Releasing the Claude Code plugin

The Kafka skills are distributed as the `kafka-skills` plugin via the in-repo `lensesio` marketplace ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)). End users install via `/plugin install kafka-skills@lensesio`. To cut a new release:

1. **Bump the version.** Edit `version` in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) (and matching [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) for Cursor users) following [SemVer](https://semver.org/):
   - **Patch** (`0.1.0` -> `0.1.1`): wording tweaks, reference updates, no workflow change.
   - **Minor** (`0.1.0` -> `0.2.0`): new skill added, new step in an existing skill, new optional argument.
   - **Major** (`0.1.0` -> `1.0.0`): renamed skill, removed skill, breaking change to required arguments or expected MCP tool set.
2. **Validate.** Run `claude plugin validate .` from the repo root - both the marketplace and plugin manifests must pass.
3. **Smoke test locally:**
   ```bash
   claude plugin marketplace add ./ --scope local
   claude plugin install kafka-skills@lensesio
   claude plugin list                        # confirm new version installed
   claude plugin uninstall kafka-skills@lensesio
   claude plugin marketplace remove lensesio
   ```
4. **Open the PR**, get it reviewed and merged to `main`.
5. **Tag the release:**
   ```bash
   git tag -a kafka-skills-v<new-version> -m "kafka-skills v<new-version>"
   git push origin kafka-skills-v<new-version>
   ```
   Existing users will pick up the new version on their next `/plugin update kafka-skills@lensesio` because [version resolution](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels) compares the `version` string in `plugin.json`. Without a bump, no client sees the change.

**Do not** set `version` in the plugin's marketplace entry - the docs warn that `plugin.json` always silently wins over the marketplace entry, which makes drift hard to debug. Keep `version` in `plugin.json` only.

## Commit and branch conventions

### Branch names

Use the prefixes already established in `AGENTS.md`:

- `feature/<short-description>` — new skill, hook or capability.
- `fix/<short-description>` — bug fix.
- `docs/<short-description>` — documentation-only change.
- `refactor/<short-description>` — internal restructuring with no behaviour change.

### Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional-scope>): <short description>

<optional longer body explaining why>
```

Common types:

- `feat` — new skill, hook or capability.
- `fix` — bug fix.
- `docs` — documentation only.
- `refactor` — internal change without behaviour change.
- `chore` — tooling, dependencies, repo housekeeping.
- `test` — test cases or test infrastructure.

Examples:

```
feat(skill): add kafka-streams-review skill
fix(kafka-topic-audit): correct retention threshold for compacted topics
docs(readme): clarify Cursor vs Claude Code setup
```

Keep commits atomic and focused. Squash WIP commits before opening the PR (or let the maintainer squash on merge — your call).

## Sign-off and licensing

This project is released under the [MIT License](LICENSE). By contributing, you agree that your contribution will be licensed under the same terms.

We use a Developer Certificate of Origin (DCO) sign-off to make the contributor's intent explicit. Add `-s` to your `git commit`:

```bash
git commit -s -m "feat(skill): add kafka-streams-review skill"
```

This appends a `Signed-off-by: Your Name <your.email@example.com>` line to your commit. The DCO text is at [developercertificate.org](https://developercertificate.org/). PRs without sign-off may be asked to re-sign before merge.

If your employer requires a CLA or has restrictions on open-source contributions, please clear it on your side before contributing.

## Style guide

### Markdown

- Use sentence case for headings (`## Topic audit`, not `## Topic Audit`).
- Use British English where there is a choice (organise, behaviour, colour) — this matches the existing prose.
- Wrap long lines at a natural sentence break; do not hard-wrap at a fixed column.
- Prefer fenced code blocks with a language tag (` ```yaml `, ` ```bash `).
- Use relative links for anything inside the repo.

### YAML frontmatter

- Two-space indentation.
- Quote strings only when they contain colons, quotes or other YAML metacharacters.
- Keep `description` between one and three sentences with explicit trigger phrases and at least one negative trigger.

## Where to get help

- **GitHub Issues** — bug reports, feature requests, design discussion.
- **GitHub Discussions** — open-ended questions and ideas (when enabled).
- **Lenses Community Slack** — join via [launchpass.com/lensesio](https://launchpass.com/lensesio). Useful for quick questions and informal feedback.
- **Lenses documentation** — [docs.lenses.io](https://docs.lenses.io/) for Lenses HQ and Lenses MCP.

For Code of Conduct concerns, please contact the maintainers directly via the Lenses Community Slack rather than via a public issue.

## Recognition

Contributors are recognised in the GitHub contributors graph and in release notes for substantive changes. If you would like to be highlighted differently (or not at all), let us know in your PR.

---

Thank you for helping make AI agents genuinely useful for Kafka engineering. The best skills in this repo will come from people who have lived through the problems they encode — that might be you.
