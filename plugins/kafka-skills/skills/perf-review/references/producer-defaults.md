# Producer Configuration Defaults and Recommendations

Detailed lookup table for Kafka producer performance properties. These property names are identical across all client libraries (Python, Java, Go, etc.).

## Properties to Search For

- `acks` or `request.required.acks`
- `batch.size` or `batch_size`
- `linger.ms` or `linger_ms`
- `compression.type` or `compression_type`
- `enable.idempotence` or `enable_idempotence`
- `max.in.flight.requests.per.connection`
- `buffer.memory` or `buffer_memory`
- `retries`

## Audit Table

| Property | Default | Issue | Recommendation |
|----------|---------|-------|----------------|
| `acks` | `all` | `acks=0` loses messages silently | Use `all` for durability or `1` for balanced throughput |
| `batch.size` | 16384 (16KB) | Un-tuned default limits throughput | 100000-200000 (100-200KB) for throughput workloads |
| `linger.ms` | 0 | Sends immediately, no batching benefit | 5-100ms to allow batch accumulation |
| `compression.type` | `none` | Wastes network and storage | `lz4` (fast) or `zstd` (better ratio) |
| `enable.idempotence` | `true` (Kafka 3.0+) | `false` risks duplicate messages | Always `true` for exactly-once semantics |
| `retries` | `MAX_INT` | `0` means no retry on transient errors | Leave as default or set > 3 |

## Anti-Patterns

- Synchronous produce calls (`.get()`, `.result()`, `flush()` after every send)
- Missing delivery callbacks / error handlers
- Missing graceful shutdown / rebalance listeners
