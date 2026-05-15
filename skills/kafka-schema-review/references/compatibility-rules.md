# Schema Compatibility Rules

Detailed compatibility matrix for Kafka schema evolution. Referenced from the main SKILL.md workflow.

## Backward Compatibility (new readers, old data)

- **Breaking**: Removing a required field without a default
- **Breaking**: Changing a field type (e.g., `string` to `int`)
- **Breaking**: Renaming a field (treated as remove + add)
- **Safe**: Adding a new field with a default value
- **Safe**: Removing an optional field

## Forward Compatibility (old readers, new data)

- **Breaking**: Adding a required field without a default
- **Safe**: Removing a field (old readers ignore it)
- **Safe**: Adding an optional field with a default

## Full Compatibility (both directions)

- Only optional fields with defaults can be added or removed

## Schema Quality Checks

- **Warning**: Fields without documentation/description annotations
- **Warning**: Missing default values on optional fields
- **Warning**: Inconsistent naming conventions across schemas (camelCase vs snake_case)
- **Suggestion**: Unused fields that could be deprecated
- **Suggestion**: Overly generic field names (`data`, `payload`, `value`)

## File Types to Scan

- `.avsc` files (Avro schemas)
- `.proto` files (Protobuf schemas)
- `.json` files in schema directories (JSON Schema)
- Inline schema definitions in code (search for `Schema`, `schema`, `SCHEMA`)
