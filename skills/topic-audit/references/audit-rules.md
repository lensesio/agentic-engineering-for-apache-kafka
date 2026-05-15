# Topic Audit Rules

Detailed threshold rules for each audit category. Referenced from the main SKILL.md workflow.

## Replication Factor

- **Critical**: RF=1 in any environment (no fault tolerance)
- **Warning**: RF=2 in production (tolerates only 1 broker failure)
- **OK**: RF >= 3 in production

## Retention Policies

- **Critical**: `retention.ms=-1` with no compaction (unbounded growth)
- **Warning**: `retention.ms` < 1 hour (potential data loss if consumers lag)
- **Warning**: `retention.ms` > 30 days without justification (storage waste)
- Check `retention.bytes` is set where appropriate

## Partition Count

- **Warning**: 1 partition (throughput bottleneck, no consumer parallelism)
- **Warning**: > 100 partitions (overhead, slow rebalancing)
- Check partition count aligns with expected consumer count

## Compaction Settings

- **Warning**: `cleanup.policy=compact` without a key schema (compaction requires keys)
- **Suggestion**: State/changelog topics should use `compact` rather than `delete`

## Naming Conventions

- Verify topic names follow `<domain>.<entity>.<event>` convention
- Flag topics not matching the pattern
- Flag topics using underscores instead of dots as separators
- Flag topics with no clear domain prefix
