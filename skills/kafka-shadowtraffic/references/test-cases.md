# kafka-shadowtraffic Test Cases

## Should trigger

These phrasings should invoke the kafka-shadowtraffic skill:

1. "Set up ShadowTraffic for the orders topic"
2. "Populate my Kafka topic with test data"
3. "Generate synthetic events into the payments topic"
4. "I need fake data flowing into my Kafka topic"
5. "Seed the transactions topic with realistic data"
6. "Create a ShadowTraffic config for topic user-events"
7. "I want to mock data for my Kafka topic"
8. "Use ShadowTraffic to send data to orders.created"
9. "Generate load on my Kafka topic for testing"
10. "Set up synthetic data generation for the inventory topic"
11. "I need to populate Kafka with fake orders so I can test my consumer"
12. "Can you help me configure ShadowTraffic?"
13. "Generate test events for Kafka"
14. "I want to simulate traffic on my Kafka topic"
15. "Send synthetic data to the audit-log topic"

## Should NOT trigger

These phrasings should use a different skill:

- "Review my schema changes" → kafka-schema-review
- "Build a Python consumer for the orders topic" → kafka-python-client
- "Audit my Kafka topics" → kafka-topic-audit
- "Check consumer lag on the payments group" → kafka-consumer-lag
- "Set up a Kafka connector" → kafka-connector-review
- "Create a new Kafka topic" → topic management, not this skill
