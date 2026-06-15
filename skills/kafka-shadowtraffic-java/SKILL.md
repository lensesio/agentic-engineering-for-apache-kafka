---
name: kafka-shadowtraffic-java
description: Generate a TestContainers Java test class that spins up ShadowTraffic in-process to populate a Kafka topic with synthetic data during tests. Invokes the kafka-shadowtraffic skill to build the ShadowTraffic config, then adapts it for a containerized test network and scaffolds a JUnit 5 test class with Kafka, optional Schema Registry, and ShadowTraffic containers wired together. Use when the user says "set up a Java TestContainers test with ShadowTraffic", "write a Java test that generates Kafka data", "create a TestContainers test for my Kafka consumer", "I want to test my Kafka consumer with synthetic data in Java", or "scaffold a ShadowTraffic Java test". Do NOT use for non-Java projects, standalone Docker setups (use kafka-shadowtraffic instead), or creating Kafka topics.
license: MIT
allowed-tools: Read, Grep, Glob, Bash, Write, mcp__*
argument-hint: "[required: topic name or keyword] [optional: environment name] [optional: path to existing Java project]"
compatibility: Works with any Kafka MCP server (Lenses MCP, Confluent MCP, AivenLabs MCP, custom) that exposes topic listing and schema retrieval — delegated to the kafka-shadowtraffic skill. Targets Maven and Gradle projects. Targets JUnit 5 and Java 11+.
metadata:
  author: Michael Drogalis
  version: 1.0.0
  mcp-server: any-kafka-mcp
  category: workflow-automation
  approach: problem-first
  patterns: sequential-workflow, skill-chaining, context-aware-selection
  tags: [kafka, shadowtraffic, testcontainers, java, junit5, integration-testing, synthetic-data]
---

# Kafka ShadowTraffic Java TestContainers Setup

Generates a self-contained JUnit 5 test class that uses TestContainers to spin up Kafka and ShadowTraffic in-process, populating the target topic with synthetic data during the test run. The skill delegates schema discovery and config generation to `kafka-shadowtraffic`, then adapts the resulting config for a shared Docker network and scaffolds the Java test file and build dependencies.

Target topic, environment, and project path: $ARGUMENTS

Open your first reply with: "Running the kafka-shadowtraffic-java skill to scaffold a TestContainers test."

## Workflow

Copy this checklist and track your progress:

```
TestContainers Scaffold Progress:
- [ ] Step 1: Run kafka-shadowtraffic to discover topic and generate base ShadowTraffic config
- [ ] Step 2: Detect project structure (build tool, test directories, existing dependencies)
- [ ] Step 3: Hard gate - confirm before generating
- [ ] Step 4: Adapt ShadowTraffic config for TestContainers network
- [ ] Step 5: Write adapted config to src/test/resources/
- [ ] Step 6: Lint the adapted config
- [ ] Step 7: Generate the Java test class
- [ ] Step 8: Update build file with TestContainers dependencies
- [ ] Step 9: Hand back with run instructions
```

## Step 1: Run kafka-shadowtraffic

Invoke the `kafka-shadowtraffic` skill to discover the topic, schemas, and serialization format, and generate a base `shadowtraffic-config.json`.

The `kafka-shadowtraffic` skill handles:
- MCP-based topic and schema discovery
- Serializer selection (Avro / JSON Schema / Protobuf / plain)
- Generator construction from schema fields
- Config linting

Once `kafka-shadowtraffic` completes and `shadowtraffic-config.json` exists, continue from Step 2. If the file already exists in the working directory from a prior run of `kafka-shadowtraffic`, skip re-running it and proceed directly to Step 2.

**One change to request of kafka-shadowtraffic**: add `"maxEvents": 100` to the generator's `localConfigs` before linting. Tests must terminate; an unbounded ShadowTraffic run will hang the test suite. If the user specifies a different count, use that instead.

## Step 2: Detect project structure

Scan the project directory (the path from `$ARGUMENTS`, or the current working directory if not specified) for:

1. **Build tool**: look for `pom.xml` (Maven) or `build.gradle` / `build.gradle.kts` (Gradle). If both exist, prefer the one at the project root.
2. **Test source directory**: `src/test/java` (Maven convention) or equivalent Gradle layout.
3. **Test resources directory**: `src/test/resources` — create it if it doesn't exist.
4. **Package name**: infer from existing test files in `src/test/java/**/*Test.java`. Fall back to asking the user if none found.
5. **Existing TestContainers dependency**: check `pom.xml` / `build.gradle` for `org.testcontainers` — note if already present so we don't add a duplicate.
6. **Existing Kafka TestContainers dependency**: check for `org.testcontainers:kafka`.
7. **Java version**: check `<java.version>` in `pom.xml`, `sourceCompatibility` in `build.gradle`, or `.java-version` / `JAVA_HOME`. Default to Java 17 if not detectable.
8. **Schema Registry needed**: read from the base `shadowtraffic-config.json` — if `value.serializer` is `KafkaAvroSerializer`, `KafkaJsonSchemaSerializer`, or `KafkaProtobufSerializer`, a Schema Registry container is required.

## Step 3: Hard gate — confirm before generating

Send one message recapping:

1. Topic name, schema format, number of fields.
2. Build tool detected and test source directory.
3. Package name that will be used for the generated class.
4. Whether a Schema Registry container will be included (yes/no, and why).
5. `maxEvents` value (default 100).
6. Files that will be written (Java class path, config destination, build file change).

Ask the user to confirm or correct. Stop and wait. The only way to skip is if the user already confirmed in this conversation.

## Step 4: Adapt ShadowTraffic config for TestContainers network

The base config from `kafka-shadowtraffic` points at the real cluster (`localhost:9092` or the discovered broker). For the TestContainers test, both Kafka and ShadowTraffic share a Docker network, so the bootstrap server must be the Kafka container's internal network alias.

Make these changes to `shadowtraffic-config.json` (produce a separate copy — do not overwrite the standalone config):

| Original value | Replace with |
|---|---|
| `bootstrap.servers` (any value) | `kafka:9092` |
| `schema.registry.url` (if present) | `http://schema-registry:8081` |

Also ensure `"maxEvents": <count>` is present in `localConfigs`. Add it if `kafka-shadowtraffic` didn't include it.

The adapted config is only for the TestContainers test — the original `shadowtraffic-config.json` for standalone Docker use stays untouched.

## Step 5: Write adapted config to src/test/resources/

Write the adapted config to `src/test/resources/shadowtraffic-config.json`. Create the `src/test/resources/` directory if it doesn't exist.

The Java class will load this file via `MountableFile.forClasspathResource("shadowtraffic-config.json")`.

## Step 6: Lint the adapted config

Run the ShadowTraffic linter against the adapted config before generating any Java:

```bash
docker run \
  -e LICENSE_ID=lint -e LICENSE_EMAIL=lint \
  -e LICENSE_ORGANIZATION=lint -e LICENSE_EDITION=lint \
  -e LICENSE_EXPIRATION=lint -e LICENSE_SIGNATURE=lint \
  -v $(pwd)/src/test/resources/shadowtraffic-config.json:/home/config.json \
  shadowtraffic/shadowtraffic:latest \
  --action lint \
  --config /home/config.json
```

Fix any findings before proceeding. If Docker is unavailable, skip and note it in the hand-back.

## Step 7: Generate the Java test class

Read `references/java-template.md` for the full annotated template. The high-level class structure:

```java
package <detected-package>;

@Testcontainers
class <TopicName>ShadowTrafficTest {

    static final Network network = Network.newNetwork();

    @Container
    static final KafkaContainer kafka =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.7.0"))
            .withNetwork(network)
            .withNetworkAliases("kafka");

    // Only when Schema Registry is needed:
    @Container
    static final GenericContainer<?> schemaRegistry =
        new GenericContainer<>(DockerImageName.parse("confluentinc/cp-schema-registry:7.7.0"))
            .withNetwork(network)
            .withNetworkAliases("schema-registry")
            .dependsOn(kafka)
            .withEnv("SCHEMA_REGISTRY_HOST_NAME", "schema-registry")
            .withEnv("SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS", "kafka:9092")
            .withExposedPorts(8081);

    @Container
    static final GenericContainer<?> shadowTraffic =
        new GenericContainer<>(DockerImageName.parse("shadowtraffic/shadowtraffic:latest"))
            .withNetwork(network)
            .dependsOn(/* kafka, and schemaRegistry if present */)
            .withEnv("LICENSE_ID", System.getenv("LICENSE_ID"))
            .withEnv("LICENSE_EMAIL", System.getenv("LICENSE_EMAIL"))
            .withEnv("LICENSE_ORGANIZATION", System.getenv("LICENSE_ORGANIZATION"))
            .withEnv("LICENSE_EDITION", System.getenv("LICENSE_EDITION"))
            .withEnv("LICENSE_EXPIRATION", System.getenv("LICENSE_EXPIRATION"))
            .withEnv("LICENSE_SIGNATURE", System.getenv("LICENSE_SIGNATURE"))
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("shadowtraffic-config.json"),
                "/home/config.json"
            )
            .withCommand("--config", "/home/config.json");

    @Test
    void shouldReceiveEventsFromShadowTraffic() {
        // Create a Kafka consumer using kafka.getBootstrapServers()
        // Poll until maxEvents events received or timeout
        // Assert event count and spot-check field values
    }
}
```

**Key rules for the generated class** (see `references/java-template.md` for full detail):

1. **License env vars come from `System.getenv()`** — never hardcode them. The test will fail with a clear error if vars are missing.
2. **`dependsOn` order matters**: ShadowTraffic must depend on Kafka (and Schema Registry if present) so containers start in the right order.
3. **The test consumer uses `kafka.getBootstrapServers()`** — this is the external address TestContainers maps; it's different from the internal `kafka:9092` used by ShadowTraffic.
4. **Poll with a timeout**: use a `Duration.ofSeconds(30)` poll timeout. The test should not hang if ShadowTraffic fails to start.
5. **Assert at least `maxEvents` records were received** as the primary assertion.
6. **Spot-check one field** from the value schema to verify the data shape matches the schema (e.g., assert `orderId` is a non-null UUID string).
7. **Class name**: derive from the topic name. `orders.payment.completed` → `OrdersPaymentCompletedShadowTrafficTest`.
8. **`@Container` fields are `static final`**: TestContainers reuses containers across tests in the same class.

Write the class to `src/test/java/<package-path>/<ClassName>.java`.

## Step 8: Update build file with TestContainers dependencies

Consult `references/build-tool-deps.md` for the exact dependency snippets. Only add dependencies that are not already present.

**Required additions**:
- `org.testcontainers:testcontainers` (BOM or explicit version)
- `org.testcontainers:junit-jupiter`
- `org.testcontainers:kafka`
- `confluentinc/cp-kafka` image is pulled at runtime — no Maven dep needed

**If Schema Registry container is used** (Avro / JSON Schema / Protobuf topics):
- No additional TestContainers dependency needed (`GenericContainer` handles it)
- Add Confluent Avro/JSON Schema deserializer dependencies if not present, so the test consumer can deserialize the events

## Step 9: Hand back with run instructions

Final message must include:

1. **Files written**: Java class path, adapted config path, build file changes.

2. **License setup** (required before the test can run):
   ```bash
   export LICENSE_ID=...
   export LICENSE_EMAIL=...
   export LICENSE_ORGANIZATION=...
   export LICENSE_EDITION=...
   export LICENSE_EXPIRATION=...
   export LICENSE_SIGNATURE=...
   ```
   Get a license at https://shadowtraffic.io. Without these env vars the ShadowTraffic container will fail to start.

3. **Run the test**:
   ```bash
   # Maven
   mvn test -Dtest=<ClassName>

   # Gradle
   ./gradlew test --tests "<package>.<ClassName>"
   ```

4. **What the test does**: one-paragraph summary — containers started, events generated, what the assertion checks.

5. **Adapting the assertion**: a note that the generated `@Test` method is a starting point — the user should add domain-specific assertions (field values, ordering, counts) to match their actual consumer logic.

## Success Criteria

### Quantitative

- Triggers on 90% of "TestContainers + ShadowTraffic Java" queries (see `references/test-cases.md`)
- Adapted `shadowtraffic-config.json` passes the linter with zero findings
- Generated Java class compiles without errors on first try
- Test passes end-to-end against a local Docker environment

### Qualitative

- License env vars are never hardcoded — always `System.getenv()`
- Container startup order is correct — Kafka (and Schema Registry) before ShadowTraffic
- The test terminates because `maxEvents` is set in the config
- The user can see clearly what to change to add their own assertions

## Examples

### Example 1: Avro topic (Lenses MCP attached)

User says: *"write a TestContainers Java test for the orders topic using ShadowTraffic"*

Actions:
1. Step 1: `kafka-shadowtraffic` discovers `orders.created` (Avro, 5 fields). Generates base config with `KafkaAvroSerializer`.
2. Step 2: Maven project detected, package `com.example.orders`, Schema Registry required.
3. Step 3: Recap — user confirms.
4. Step 4: Adapt config: `bootstrap.servers → kafka:9092`, `schema.registry.url → http://schema-registry:8081`, `maxEvents → 100`.
5. Steps 5-6: Write to `src/test/resources/shadowtraffic-config.json`, lint passes.
6. Step 7: Generate `OrdersCreatedShadowTrafficTest.java` with Kafka + Schema Registry + ShadowTraffic containers.
7. Step 8: Add `org.testcontainers:junit-jupiter`, `org.testcontainers:kafka` to `pom.xml`.
8. Step 9: Hand back.

Result: `mvn test -Dtest=OrdersCreatedShadowTrafficTest` starts three containers, generates 100 Avro events, consumer asserts all received.

### Example 2: Plain JSON topic, Gradle project

User says: *"I need a Java integration test that seeds my Kafka topic with fake data"*

Actions:
1. Step 1: `kafka-shadowtraffic` discovers `audit.events` (no schema, plain JSON). Base config uses `JsonSerializer`.
2. Step 2: Gradle project, package `io.company.audit`, no Schema Registry.
3. Step 3: Recap — user confirms.
4. Steps 4-7: Adapt config (bootstrap.servers only), lint, generate `AuditEventsShadowTrafficTest.java` with Kafka + ShadowTraffic only (no Schema Registry container).
5. Step 8: Add TestContainers deps to `build.gradle`.

Result: `./gradlew test --tests "io.company.audit.AuditEventsShadowTrafficTest"` runs with two containers.

### Example 3: Existing shadowtraffic-config.json

User says: *"take the ShadowTraffic config we just made and wrap it in a Java test"*

Actions:
1. Step 1: `shadowtraffic-config.json` already exists in the working directory — skip re-running `kafka-shadowtraffic`.
2. Steps 2-9: Proceed with adaptation and scaffolding.

## Troubleshooting

### ShadowTraffic container exits immediately

Cause: License env vars are missing or invalid, or the config has an error.

Solution: Verify all six `LICENSE_*` env vars are exported. Check Docker logs: `docker logs <container-id>`. Re-run the linter (Step 6) to catch config errors.

### Test hangs and never completes

Cause: `maxEvents` is missing from the config — ShadowTraffic runs forever.

Solution: Add `"maxEvents": 100` (or another finite count) to the generator's `localConfigs` in `src/test/resources/shadowtraffic-config.json`. Re-lint before re-running.

### Schema Registry container fails to start

Cause: `SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS` is wrong, or Kafka isn't fully up when Schema Registry tries to connect.

Solution: Confirm `dependsOn(kafka)` is set on the Schema Registry container. Add `.waitingFor(Wait.forHttp("/subjects").forStatusCode(200))` to the Schema Registry container definition so TestContainers waits until it's ready.

### Consumer receives 0 events

Cause: ShadowTraffic started but couldn't reach Kafka (network misconfiguration), or the consumer group offset is wrong.

Solution: Check that both containers have `.withNetwork(network)` and that `bootstrap.servers` in the adapted config is exactly `kafka:9092`. Ensure the consumer uses `AUTO_OFFSET_RESET_CONFIG = "earliest"` so it reads from the beginning of the topic.

### `MountableFile.forClasspathResource` can't find the config

Cause: `shadowtraffic-config.json` is not in `src/test/resources/` or the build hasn't copied it to the classpath.

Solution: Confirm the file was written to `src/test/resources/shadowtraffic-config.json` (Step 5). For Maven, resources in `src/test/resources/` are copied to the test classpath automatically. For Gradle, verify `test.resources.srcDirs` includes `src/test/resources`.
