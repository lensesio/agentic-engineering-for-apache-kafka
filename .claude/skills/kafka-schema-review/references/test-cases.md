# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Review schema changes"
- "Check schema compatibility"
- "Will this schema break consumers?"
- "Audit schemas in staging"
- "Is this Avro change backward compatible?"
- "Check for schema drift"
- "Review the schema changes in this PR"
- "Schema evolution review"
- "Are there any breaking changes in the new schema?"
- "Which topics have no registered schema?"

### Should NOT Trigger
- "Create a new Avro schema for the orders topic"
- "Register this schema in the cluster"
- "Generate a Protobuf schema from this JSON"
- "What is Avro?"
- "Convert this CSV to JSON Schema"

## Functional Tests

### Test 1: PR with breaking schema change
**Given**: PR modifies an .avsc file, removing a required field without a default.
**When**: Skill reviews the schema change.
**Then**:
- Breaking change is detected and flagged as critical
- Affected topics are listed
- Migration guidance is provided
- Report follows the defined format

### Test 2: Schema drift detection
**Given**: Schema file in the repo differs from what is registered in the cluster.
**When**: Skill compares repo vs cluster schemas.
**Then**: Drift is reported with both versions summarised.

### Test 3: No schemas registered
**Given**: Environment has topics but no schemas registered in Schema Registry.
**When**: Skill fetches registered schemas.
**Then**: Reports this as a governance gap and proceeds with codebase-only analysis.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 8-12 | 1-2 |
| Failed MCP calls | 0-1 | 0 |
| Tool calls | 15+ | < 12 |
| User corrections needed | 2-4 | 0 |
