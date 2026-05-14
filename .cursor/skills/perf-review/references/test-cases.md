# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Review Kafka performance configs"
- "Check producer settings"
- "Are my consumer configs tuned?"
- "Tune Kafka settings for throughput"
- "What batch size should I use?"
- "Check compression settings"
- "Review acks and linger.ms configuration"
- "Performance review for the staging cluster"
- "Find Kafka anti-patterns in the codebase"
- "Why is my producer slow?"

### Should NOT Trigger
- "How many brokers do I need?"
- "What hardware should I use for Kafka?"
- "Plan capacity for 10 million messages per second"
- "Set up a new Kafka cluster"
- "Explain the Kafka protocol"

## Functional Tests

### Test 1: Full performance review (cluster + codebase)
**Given**: Healthy environment and codebase with Kafka producer/consumer configs.
**When**: Skill executes full review.
**Then**:
- Cluster-side configs are checked via MCP
- Codebase is searched for producer and consumer properties
- Findings reference both references/producer-defaults.md and references/consumer-defaults.md
- Anti-patterns (synchronous produce, missing callbacks) are flagged
- Output follows the defined report format

### Test 2: Codebase-only review (MCP unavailable)
**Given**: MCP connection fails or environment is not specified.
**When**: Skill proceeds with codebase-only analysis.
**Then**: Report notes the MCP limitation and provides codebase findings only.

### Test 3: No Kafka configs found in codebase
**Given**: Codebase uses a framework wrapper that hides raw Kafka properties.
**When**: Skill searches for standard property names.
**Then**: Reports that no raw Kafka configs were found and suggests framework-specific alternatives.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 8-12 | 1-2 |
| Failed MCP calls | 1-2 | 0 |
| Tool calls | 18+ | < 15 |
| User corrections needed | 3-5 | 0 |
