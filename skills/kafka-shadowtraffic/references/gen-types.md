# ShadowTraffic Generator Type Mapping

Use this table to pick the right `_gen` for each schema field. Prefer semantic over structural: a field named `userId` should get `uuid` even if its type is `string`, because that's what the data actually is.

## Primitive type defaults

| Avro/JSON Schema type | Default `_gen` | Example |
|---|---|---|
| `string` (generic) | `{"_gen": "string", "expr": "#{Lorem.word}"}` | random word |
| `string` (uuid pattern) | `{"_gen": "uuid"}` | `"3fa85f64-..."` |
| `int`, `integer` | `{"_gen": "uniformDistribution", "bounds": [0, 1000], "decimals": 0}` | `42` |
| `long` | `{"_gen": "uniformDistribution", "bounds": [0, 1000000], "decimals": 0}` | `84321` |
| `float`, `double`, `number` | `{"_gen": "uniformDistribution", "bounds": [0, 1000], "decimals": 2}` | `3.14` |
| `boolean` | `{"_gen": "boolean"}` | `true` |
| `null` | `null` | literal null |
| `bytes` | `{"_gen": "bytes", "length": 16}` | base64-encoded bytes |

## Field name patterns → semantic generators

When the field name matches a pattern below, prefer the semantic generator over the default for the type.

| Field name pattern | Recommended `_gen` | Notes |
|---|---|---|
| `*id`, `*Id`, `*_id` | `{"_gen": "uuid"}` | Entity identifiers |
| `*key`, `*Key` | `{"_gen": "uuid"}` | Correlation keys |
| `*name` (person) | `{"_gen": "string", "expr": "#{Name.fullName}"}` | Full person name |
| `*firstName`, `*first_name` | `{"_gen": "string", "expr": "#{Name.firstName}"}` | |
| `*lastName`, `*last_name` | `{"_gen": "string", "expr": "#{Name.lastName}"}` | |
| `*email*` | `{"_gen": "string", "expr": "#{Internet.emailAddress}"}` | |
| `*phone*` | `{"_gen": "string", "expr": "#{PhoneNumber.phoneNumber}"}` | |
| `*address*` | `{"_gen": "string", "expr": "#{Address.fullAddress}"}` | |
| `*city*` | `{"_gen": "string", "expr": "#{Address.city}"}` | |
| `*country*` | `{"_gen": "string", "expr": "#{Address.country}"}` | |
| `*zip*`, `*postal*` | `{"_gen": "string", "expr": "#{Address.zipCode}"}` | |
| `*url*`, `*uri*` | `{"_gen": "string", "expr": "#{Internet.url}"}` | |
| `*ip*` | `{"_gen": "string", "expr": "#{Internet.ipV4Address}"}` | |
| `*username*`, `*user_name*` | `{"_gen": "string", "expr": "#{Name.username}"}` | |
| `*amount*`, `*price*`, `*cost*`, `*total*` | `{"_gen": "uniformDistribution", "bounds": [1, 1000], "decimals": 2}` | Monetary values |
| `*quantity*`, `*count*`, `*qty*` | `{"_gen": "uniformDistribution", "bounds": [1, 100], "decimals": 0}` | Integer counts |
| `*percent*`, `*rate*`, `*ratio*` | `{"_gen": "uniformDistribution", "bounds": [0, 1], "decimals": 4}` | 0-1 ratio |
| `*score*`, `*rating*` | `{"_gen": "uniformDistribution", "bounds": [1, 5], "decimals": 1}` | Ratings |
| `*age*` | `{"_gen": "uniformDistribution", "bounds": [18, 80], "decimals": 0}` | |
| `*timestamp*`, `*createdAt*`, `*updatedAt*`, `*time*`, `*date*` | `{"_gen": "now"}` | Current epoch ms |
| `*status*`, `*state*` | `{"_gen": "oneOf", "choices": [...from schema enum...]}` | Use actual schema symbols |
| `*type*`, `*kind*`, `*category*` | `{"_gen": "oneOf", "choices": [...from schema enum...]}` | Use actual schema symbols |
| `*description*`, `*comment*`, `*note*`, `*message*` | `{"_gen": "string", "expr": "#{Lorem.sentence}"}` | Short prose |
| `*title*` | `{"_gen": "string", "expr": "#{Lorem.words '3'}"}` | Short phrase |
| `*currency*` | `{"_gen": "oneOf", "choices": ["USD", "EUR", "GBP", "JPY"]}` | Adjust to schema enum if present |
| `*language*`, `*locale*` | `{"_gen": "oneOf", "choices": ["en", "fr", "de", "es", "ja"]}` | |
| `*region*`, `*zone*` | `{"_gen": "oneOf", "choices": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]}` | |
| `*version*` | `{"_gen": "sequentialInteger", "startingFrom": 1}` | Monotonic version counter |

## Avro logical types

| Avro logical type | Recommended `_gen` | Notes |
|---|---|---|
| `{"type": "long", "logicalType": "timestamp-millis"}` | `{"_gen": "now"}` | Epoch milliseconds |
| `{"type": "long", "logicalType": "timestamp-micros"}` | `{"_gen": "now"}` | ShadowTraffic handles units |
| `{"type": "long", "logicalType": "date"}` | `{"_gen": "now"}` | |
| `{"type": "string", "logicalType": "uuid"}` | `{"_gen": "uuid"}` | |
| `{"type": "bytes", "logicalType": "decimal"}` | `{"_gen": "uniformDistribution", "bounds": [1, 10000], "decimals": 2}` | |

## Avro type unions (nullable fields)

For `["null", "string"]` or `["null", <type>]`, generate null some percentage of the time:

```json
{
  "_gen": "weightedOneOf",
  "choices": [
    {"weight": 1, "value": null},
    {"weight": 9, "value": {"_gen": "string", "expr": "#{Lorem.word}"}}
  ]
}
```

Adjust weights based on how often the field is expected to be null in practice. For required-in-practice fields that are technically nullable in the schema, use weight 0 for null.

## Enum fields

Always use the actual enum symbols from the schema — never invent values:

```json
{"_gen": "oneOf", "choices": ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]}
```

For status fields that model a business lifecycle, consider `stateMachine` to make transitions realistic:

```json
{
  "_gen": "stateMachine",
  "initial": "PENDING",
  "transitions": {
    "PENDING": {"CONFIRMED": 0.7, "CANCELLED": 0.3},
    "CONFIRMED": {"SHIPPED": 0.9, "CANCELLED": 0.1},
    "SHIPPED": {"DELIVERED": 1.0},
    "DELIVERED": {},
    "CANCELLED": {}
  }
}
```

## Array fields

Generate arrays with a random element count:

```json
{
  "_gen": "repeatedly",
  "target": {"_gen": "uuid"},
  "times": {"_gen": "uniformDistribution", "bounds": [1, 5], "decimals": 0}
}
```

## Cross-topic references (lookup)

When generating a child topic that references a parent topic (e.g., `orders` referencing `customers`), use `lookup` to pull real IDs from the parent generator:

```json
{
  "customerId": {
    "_gen": "lookup",
    "topic": "customers",
    "path": ["key", "customerId"]
  }
}
```

The parent generator must be listed first in the `generators` array.

## Throughput control

`localConfigs` options for the generator:

| Config | Type | Effect |
|---|---|---|
| `throttleMs` | number | Wait N ms between events. 500 = 2/sec, 100 = 10/sec, 0 = max throughput |
| `maxEvents` | number | Stop after N total events |
| `throughput` | number | Target events per second (alternative to `throttleMs`) |

For load testing, set `throttleMs: 0` or use `throughput` with a high number. For demos, `throttleMs: 500` or `1000` is readable.
