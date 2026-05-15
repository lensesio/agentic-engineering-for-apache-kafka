# Consumer Configuration Defaults and Recommendations

Detailed lookup table for Kafka consumer performance properties. These property names are identical across all client libraries (Python, Java, Go, etc.).

## Properties to Search For

- `max.poll.records` or `max_poll_records`
- `max.poll.interval.ms` or `max_poll_interval_ms`
- `auto.offset.reset` or `auto_offset_reset`
- `enable.auto.commit` or `enable_auto_commit`
- `fetch.min.bytes` or `fetch_min_bytes`
- `fetch.max.wait.ms` or `fetch_max_wait_ms`
- `session.timeout.ms` or `session_timeout_ms`

## Audit Table

| Property | Default | Issue | Recommendation |
|----------|---------|-------|----------------|
| `max.poll.records` | 500 | Too low for high throughput | Increase to 1000-5000 if processing is fast |
| `max.poll.interval.ms` | 300000 (5m) | Too short for heavy processing | Increase if processing takes > 1 minute per batch |
| `auto.offset.reset` | `latest` | Misses messages produced before consumer starts | Use `earliest` unless explicitly justified |
| `enable.auto.commit` | `true` | Risks processing failures going unnoticed | Use `false` with manual commit for at-least-once |
| `fetch.min.bytes` | 1 | Single-byte fetches are inefficient | Increase to 1024-65536 for throughput |
