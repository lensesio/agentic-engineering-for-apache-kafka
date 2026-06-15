# kafka-shadowtraffic-java Test Cases

## Should trigger

These phrasings should invoke the kafka-shadowtraffic-java skill:

1. "Set up a TestContainers Java test with ShadowTraffic for the orders topic"
2. "Write a Java test that generates Kafka data using ShadowTraffic"
3. "Create a TestContainers test for my Kafka consumer"
4. "I want to test my Kafka consumer with synthetic data in Java"
5. "Scaffold a ShadowTraffic Java integration test"
6. "Set up an in-process Kafka test with ShadowTraffic"
7. "Generate a JUnit test that uses ShadowTraffic to populate Kafka"
8. "I need a TestContainers test that seeds my topic with fake data"
9. "Create a Java TestContainers class for ShadowTraffic"
10. "Write a Java integration test that uses ShadowTraffic to send test events"
11. "I want ShadowTraffic running inside my Java test"
12. "Help me write a TestContainers test with synthetic Kafka data"

## Should NOT trigger

These phrasings should use a different skill:

- "Set up ShadowTraffic with Docker" → kafka-shadowtraffic (standalone config, no Java)
- "Generate a Python Kafka client" → kafka-python-client
- "Review my Kafka schema" → kafka-schema-review
- "Audit my Kafka topics" → kafka-topic-audit
- "I need a Kotlin TestContainers test" → not this skill (Java only)
- "Set up ShadowTraffic for load testing" → kafka-shadowtraffic
