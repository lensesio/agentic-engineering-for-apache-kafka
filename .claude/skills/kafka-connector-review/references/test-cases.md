# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Review my connectors"
- "Check connector configurations"
- "Why is my connector failing?"
- "Connector health check"
- "Are my sink connectors configured correctly?"
- "Review error handling on connectors"
- "Check DLQ setup for connectors"
- "Validate connector configs"
- "Which connectors have failed tasks?"
- "Review the elasticsearch-sink connector"

### Should NOT Trigger
- "Create a new JDBC source connector"
- "Deploy a connector to production"
- "Start the paused connector"
- "Write a custom Kafka Connect transform"
- "How does Kafka Connect work?"

## Functional Tests

### Test 1: Full connector review
**Given**: Environment with 5+ connectors in various states.
**When**: Skill executes full review.
**Then**:
- Status overview table lists all connectors
- Failed connectors are flagged as critical
- Configurations are validated against plugin schemas
- Error handling, converters, task count and naming are all audited
- Report follows the defined format

### Test 2: Connector with silent message drops
**Given**: Connector with errors.tolerance=all but no DLQ topic configured.
**When**: Skill audits error handling.
**Then**: Flagged as critical - silently dropping messages.

### Test 3: No connectors in environment
**Given**: Environment with no Connect cluster or no deployed connectors.
**When**: Skill lists connectors.
**Then**: Reports that no connectors were found and stops.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 6-10 | 1-2 |
| Failed MCP calls | 1-2 | 0 |
| Tool calls | 12+ | < 10 |
| User corrections needed | 2-3 | 0 |
