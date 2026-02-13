# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Check consumer lag"
- "Why are consumers slow?"
- "Consumer lag analysis for production"
- "Show me the lag report"
- "Are any consumer groups falling behind?"
- "Which consumers are lagging?"
- "Check lag for orders.payment.completed"
- "Consumer group health check"
- "Find stale consumer groups"
- "Is the analytics-order-processor group healthy?"

### Should NOT Trigger
- "Reset consumer offsets to earliest"
- "Delete the old consumer group"
- "Create a new consumer group"
- "Write a Kafka consumer in Python"
- "How do I configure a Kafka consumer?"

## Functional Tests

### Test 1: Full lag analysis
**Given**: Environment with 10+ consumer groups, some with lag.
**When**: Skill executes full lag analysis.
**Then**:
- All consumer groups are listed with state and lag
- Groups are categorised as critical/warning/suggestion
- Root cause diagnosis is provided for each flagged group
- Remediation steps are specific to each diagnosis
- Output follows the defined report format

### Test 2: Topic-specific lag check
**Given**: Topic "orders.payment.completed" with 3 consumer groups.
**When**: Skill runs with topic filter.
**Then**: Only consumer groups consuming from that topic are analysed.

### Test 3: All groups healthy
**Given**: Environment where all consumer groups have zero lag and are Stable.
**When**: Skill runs full analysis.
**Then**: Report confirms all groups are healthy with no critical or warning findings.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 6-10 | 1-2 |
| Failed MCP calls | 1-2 | 0 |
| Tool calls | 15+ | < 12 |
| User corrections needed | 2-4 | 0 |
