# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Review dead letter queues"
- "Check DLQ setup"
- "DLQ audit for production"
- "Are my DLQs configured properly?"
- "Which DLQ topics have no consumers?"
- "Check DLQ message metadata"
- "Do all our consumers have DLQ handling?"
- "Review error handling and DLQ setup"
- "Messages are ending up in the DLQ"
- "DLQ maturity assessment"

### Should NOT Trigger
- "Reprocess the failed messages in the DLQ"
- "Reset offsets on the DLQ consumer"
- "Delete the DLQ topic"
- "Write a DLQ consumer in Python"
- "What is a dead letter queue?"

## Functional Tests

### Test 1: Full DLQ audit
**Given**: Environment with DLQ topics following standard naming (*.dlq, *.error).
**When**: Skill executes full review.
**Then**:
- All DLQ topics are discovered by naming convention
- Topic configuration, monitoring and metadata completeness are checked
- Connector DLQ configs are audited
- Maturity assessment (none/basic/complete) is provided
- Report follows the defined format

### Test 2: Unmonitored DLQ topic
**Given**: DLQ topic exists but has no consumer groups.
**When**: Skill checks DLQ monitoring.
**Then**: Flagged as critical - nobody is monitoring failures.

### Test 3: No DLQ topics found
**Given**: Environment with no topics matching DLQ naming patterns.
**When**: Skill searches for DLQ topics.
**Then**: Searches codebase for error topic configuration before concluding DLQs are not implemented.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 10-15 | 1-2 |
| Failed MCP calls | 1-2 | 0 |
| Tool calls | 18+ | < 15 |
| User corrections needed | 3-5 | 0 |
