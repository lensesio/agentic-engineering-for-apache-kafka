# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Audit Kafka security"
- "Check security configuration"
- "Is my Kafka cluster secure?"
- "Security review for production"
- "Are there any hardcoded credentials?"
- "Check if we're using PLAINTEXT in production"
- "Review authentication settings"
- "Audit SSL/TLS configuration"
- "Find exposed secrets in the codebase"
- "Security posture check for staging"

### Should NOT Trigger
- "Configure SSL certificates for Kafka"
- "Create a new SASL user"
- "Set up ACLs for the orders topic"
- "Install Kafka on a new server"
- "What is SASL_SSL?"

## Functional Tests

### Test 1: Production security audit
**Given**: Production environment with SASL_SSL configured.
**When**: Skill executes full security audit.
**Then**:
- Environment tier is identified as production
- All severity levels are at full production weight
- Authentication, encryption and secrets are all checked
- Report follows the defined format

### Test 2: Development environment with PLAINTEXT
**Given**: Development environment using PLAINTEXT protocol.
**When**: Skill audits authentication.
**Then**: PLAINTEXT finding is downgraded to suggestion (acceptable for local dev) rather than critical.

### Test 3: Hardcoded credentials detected
**Given**: Codebase contains a hardcoded password in a config file.
**When**: Skill scans for secrets.
**Then**: Hardcoded credential is flagged as critical regardless of environment tier.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 8-12 | 1-2 |
| Failed MCP calls | 0-1 | 0 |
| Tool calls | 15+ | < 12 |
| User corrections needed | 2-4 | 0 |
