# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Audit my Kafka topics"
- "Check topic configurations"
- "Are my topics production-ready?"
- "Topic health check for staging"
- "Review retention settings across all topics"
- "Check replication factor for our topics"
- "Find orphaned topics with no consumers"
- "Which topics are missing metadata?"
- "Run a topic audit on production"
- "Do any topics have RF=1?"

### Should NOT Trigger
- "Create a new Kafka topic called orders.payment.completed"
- "Delete the staging topics"
- "Change retention to 7 days on the events topic"
- "Write a Kafka consumer in Python"
- "What is Apache Kafka?"

## Functional Tests

### Test 1: Full audit on a healthy environment
**Given**: Healthy staging environment with 20+ topics.
**When**: Skill executes full audit workflow.
**Then**:
- Environment health summary is printed first
- All topics are audited against rules in references/audit-rules.md
- Findings are categorised as critical/warning/suggestion
- Orphaned topics (no consumers) are identified
- Metadata completeness is checked
- Output follows the defined report format

### Test 2: Topic with critical misconfiguration
**Given**: Environment contains a topic with replication factor 1.
**When**: Skill audits replication factor.
**Then**: Topic is flagged as Critical with recommendation to increase RF to 3.

### Test 3: Unreachable environment
**Given**: Environment name that does not exist or agent is offline.
**When**: Skill runs check_environment_health.
**Then**: Reports connection error and stops without proceeding to topic audit.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 8-12 | 1-2 |
| Failed MCP calls | 1-3 | 0 |
| Tool calls | 20+ | < 15 |
| User corrections needed | 3-5 | 0 |
