---
id: decision-0006
title: Use Confluent Enterprise for Kafka
date: 2026-03-25
status: Accepted
tags: infrastructure, messaging
linked_task: task-2.1
---

## Rationale

The customer is currently using Confluent Enterprise in their production environment. To align with their existing infrastructure and minimize operational friction, we will adopt Confluent Enterprise as our Kafka platform rather than evaluating alternative implementations.

**Key drivers:**
- **Alignment with customer environment**: Customer already operates Confluent Enterprise; using the same platform reduces integration complexity and operational surprises
- **Operational continuity**: Familiar tooling, processes, and expertise already exist in the customer organization
- **Reduced risk**: No need to migrate data or train teams on different Kafka distributions

**No alternatives were evaluated** because customer standardization was the primary driver of this decision.

## Implementation Notes

- **Kafka cluster topology**: Confluent Enterprise cluster deployed in customer environment
- **Client library**: Applications use Confluent's Kafka client libraries and SDKs
- **Configuration**: Cluster configuration and authentication managed per Confluent Enterprise standards
- **Security**: Follow Confluent RBAC (role-based access control) for authentication and authorization
- **Monitoring**: Use Confluent Control Center for cluster monitoring and management
- **Schema registry**: Confluent Schema Registry for schema management (if needed for data contracts)
- **Code integration**: Applications communicate with Confluent brokers using standard Kafka producer/consumer APIs
- **Dependencies**: Add Confluent client libraries to project dependencies

## Notes

- This decision enables seamless integration with customer's existing Kafka infrastructure
- Future evaluations of Kafka alternatives should revisit this decision if customer requirements change or if self-managed options become beneficial
