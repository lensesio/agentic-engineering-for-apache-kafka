# Build Tool Dependencies for kafka-shadowtraffic-java

Add only what isn't already present. Check the existing build file before inserting.

---

## Maven (pom.xml)

### TestContainers BOM (add to `<dependencyManagement>`)

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.testcontainers</groupId>
      <artifactId>testcontainers-bom</artifactId>
      <version>1.20.1</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

### Required test dependencies (add to `<dependencies>`)

```xml
<!-- TestContainers core -->
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>testcontainers</artifactId>
  <scope>test</scope>
</dependency>

<!-- JUnit 5 integration -->
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>

<!-- Kafka container (KafkaContainer class) -->
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>kafka</artifactId>
  <scope>test</scope>
</dependency>

<!-- AssertJ for fluent assertions -->
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <version>3.26.3</version>
  <scope>test</scope>
</dependency>
```

### If Avro topics (add only when `KafkaAvroSerializer` is in the config)

```xml
<!-- Confluent Avro deserializer for the test consumer -->
<dependency>
  <groupId>io.confluent</groupId>
  <artifactId>kafka-avro-serializer</artifactId>
  <version>7.7.0</version>
  <scope>test</scope>
</dependency>
```

Also add the Confluent repository if not present:

```xml
<repositories>
  <repository>
    <id>confluent</id>
    <url>https://packages.confluent.io/maven/</url>
  </repository>
</repositories>
```

### If JSON Schema topics

```xml
<dependency>
  <groupId>io.confluent</groupId>
  <artifactId>kafka-json-schema-serializer</artifactId>
  <version>7.7.0</version>
  <scope>test</scope>
</dependency>
```

### If Protobuf topics

```xml
<dependency>
  <groupId>io.confluent</groupId>
  <artifactId>kafka-protobuf-serializer</artifactId>
  <version>7.7.0</version>
  <scope>test</scope>
</dependency>
```

---

## Gradle (build.gradle)

### TestContainers BOM

```groovy
dependencies {
    testImplementation platform('org.testcontainers:testcontainers-bom:1.20.1')
}
```

### Required test dependencies

```groovy
dependencies {
    testImplementation 'org.testcontainers:testcontainers'
    testImplementation 'org.testcontainers:junit-jupiter'
    testImplementation 'org.testcontainers:kafka'
    testImplementation 'org.assertj:assertj-core:3.26.3'
}
```

### If Avro topics

```groovy
dependencies {
    testImplementation 'io.confluent:kafka-avro-serializer:7.7.0'
}
```

Also add the Confluent repository:

```groovy
repositories {
    maven { url 'https://packages.confluent.io/maven/' }
}
```

### If JSON Schema topics

```groovy
testImplementation 'io.confluent:kafka-json-schema-serializer:7.7.0'
```

### If Protobuf topics

```groovy
testImplementation 'io.confluent:kafka-protobuf-serializer:7.7.0'
```

---

## Gradle Kotlin DSL (build.gradle.kts)

### TestContainers BOM

```kotlin
dependencies {
    testImplementation(platform("org.testcontainers:testcontainers-bom:1.20.1"))
}
```

### Required test dependencies

```kotlin
dependencies {
    testImplementation("org.testcontainers:testcontainers")
    testImplementation("org.testcontainers:junit-jupiter")
    testImplementation("org.testcontainers:kafka")
    testImplementation("org.assertj:assertj-core:3.26.3")
}
```

### If Avro topics

```kotlin
dependencies {
    testImplementation("io.confluent:kafka-avro-serializer:7.7.0")
}

repositories {
    maven("https://packages.confluent.io/maven/")
}
```

---

## Notes

- If the project already has a TestContainers BOM entry, do not add another — just add the missing artifact entries.
- Version numbers above are current as of mid-2025. If the project pins Confluent Platform to a different version (e.g. 7.6.x), match the TestContainers Kafka image and serializer versions to that.
- The `GenericContainer` class (used for both Schema Registry and ShadowTraffic) comes from `org.testcontainers:testcontainers` — no extra artifact needed.
