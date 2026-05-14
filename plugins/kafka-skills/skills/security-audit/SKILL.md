---
name: security-audit
description: Audit Kafka security configuration across the codebase and live cluster using the Lenses MCP server. Checks authentication (SASL), encryption (SSL/TLS), authorisation (ACLs), secrets management and environment tier mismatches. Use when user says "audit Kafka security", "check security config", "is my cluster secure" or asks about authentication, encryption or credentials. Do NOT use for configuring certificates, creating SASL users or setting up ACLs.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, mcp__Lenses__check_environment_health, mcp__Lenses__get_environment, mcp__Lenses__list_topics
argument-hint: "[required: environment name]"
compatibility: Recommended - the Lenses MCP server (lenses-mcp) connected and configured with a valid environment. Any Kafka MCP that exposes an equivalent broker-config and ACL tool surface will also work; without an MCP server, the skill falls back to codebase-only inspection and skips live-cluster checks.
metadata:
  author: Tun Shwe
  version: 1.0.0
  mcp-server: lenses-mcp
  category: mcp-enhancement
  approach: problem-first
  patterns: context-aware-selection, domain-intelligence
  tags: [kafka, security, authentication, encryption, secrets]
---

# Kafka Security Posture Audit

Audits Kafka security configuration across the codebase and infrastructure. Kafka clusters often start as PLAINTEXT in dev and never get properly secured for production.

Target environment: $ARGUMENTS

## Workflow

Copy this checklist and track your progress:

```
Security Audit Progress:
- [ ] Step 1: Check environment health and tier
- [ ] Step 2: Scan codebase for security configuration
- [ ] Step 3: Audit authentication
- [ ] Step 4: Audit encryption
- [ ] Step 5: Audit secrets management
- [ ] Step 6: Generate report
```

1. **Check environment health and tier** via Lenses MCP
2. **Scan codebase** for security-related configuration (see `references/security-properties.md`)
3. **Audit authentication** (SASL mechanism)
4. **Audit encryption** (SSL/TLS)
5. **Audit secrets management** (hardcoded credentials)
6. **Report findings** with severity calibrated to environment tier

## Step 1: Environment Context

Use Lenses MCP tools to understand the environment:

- `check_environment_health` - verify environment is healthy and agent is connected
- `get_environment` - get environment tier (development, staging, production) to calibrate severity levels. A PLAINTEXT connection in dev is a suggestion; in production it's critical.

Expected output: Environment tier (development/staging/production) and health status.

**Validation**: If the environment tier cannot be determined, default to production-level severity - it is safer to over-report.

## Step 2: Codebase Inspection

Search the codebase for Kafka security configuration. Consult `references/security-properties.md` for the full list of authentication properties, encryption properties and files to scan.

## Step 3: Audit Authentication

Apply the authentication audit rules from `references/security-properties.md`. Key checks:
- PLAINTEXT protocol in production (critical)
- PLAIN SASL without TLS (critical)
- No authentication configured in production (critical)
- Weak SASL mechanisms (warning)

## Step 4: Audit Encryption

Apply the encryption audit rules from `references/security-properties.md`. Key checks:
- No SSL/TLS in production (critical)
- Disabled hostname verification (warning)
- Plaintext keystore passwords (warning)

## Step 5: Audit Secrets Management

Apply the secrets audit rules from `references/security-properties.md`. Key checks:
- Hardcoded credentials in source files (critical)
- Credentials tracked by git (critical)
- Missing `.gitignore` entries (warning)

## Step 6: Environment Tier Mismatch

Cross-reference findings with the environment tier from Lenses:
- **Production/Staging**: All findings at full severity
- **Development**: Downgrade encryption/auth findings to suggestions (acceptable for local dev)
- Flag any development environment configs that might accidentally be used in production

## Success Criteria

### Quantitative
- Triggers on 90% of security-related queries (test with 10-20 varied phrasings)
- Completes audit in under 12 tool calls (MCP + codebase search)
- 0 failed MCP calls per run

### Qualitative
- Severity is correctly calibrated to environment tier (dev vs production)
- Secrets findings have zero false negatives (never misses a hardcoded credential)
- Every finding includes a risk description and remediation step

## Examples

### Example 1: Pre-production security review

User says: "Audit Kafka security for the production environment"

Actions:
1. Get environment tier (production) from Lenses MCP
2. Scan codebase for all security properties
3. Apply full-severity rules for production
Result: Complete security audit report with all findings at production severity

### Example 2: Development environment check

User says: "Is my dev Kafka cluster secure enough?"

Actions:
1. Get environment tier (development) from Lenses MCP
2. Scan codebase for security properties
3. Downgrade auth/encryption findings to suggestions for dev
4. Keep secrets findings at full severity (credentials should never be hardcoded)
Result: Report calibrated to development environment

### Example 3: Secrets-focused audit

User says: "Check if there are any hardcoded Kafka credentials in the codebase"

Actions:
1. Search for secret patterns (passwords, tokens, API keys)
2. Check `.env` files tracked by git
3. Verify `.gitignore` includes credential files
Result: Focused report on secrets management only

## Troubleshooting

### Environment tier is unknown
Cause: Lenses `get_environment` returns no tier or a custom tier value.
Solution: Default to production-level severity. It is safer to over-report than under-report security issues.

### Cannot determine if .env files are tracked by git
Cause: Not running inside a git repository.
Solution: Check for `.env` files and report their presence. Note that git tracking could not be verified.

### False positives in secrets scan
Cause: Words like "password" appear in documentation or comments rather than actual credentials.
Solution: Report all findings but note the confidence level. Flag inline values as high confidence and reference-only mentions as low confidence.

## Output Format

```
## Security Audit Report

### Environment: {name} (tier: {development|staging|production})

### Critical (must fix)
- [file:line] Description of the security issue
  Risk: {what could go wrong}
  Remediation: {how to fix}

### Warning (should fix)
- [file:line] Description of the issue
  Risk: {what could go wrong}
  Remediation: {how to fix}

### Suggestion (consider improving)
- [file:line] Description of the issue
  Recommendation: {how to improve}

### Summary
- X critical issues found
- Y warnings found
- Z suggestions found
- Environment tier: {tier}
- Authentication: {configured|missing}
- Encryption: {configured|missing}
- Secrets exposed: {yes|no}
```
