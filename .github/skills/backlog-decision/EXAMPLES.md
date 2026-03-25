# Backlog Decision - Examples

## Example 1: Technology Choice

**Input**: "Use PostgreSQL for persistent storage"

**Generated file**: `decision-0006-use-postgresql-for-persistent-storage.md`

```markdown
---
id: decision-0006
title: Use PostgreSQL for persistent storage
date: 2026-03-25
status: Accepted
tags: database, backend, persistence
linked_task: task-2.3
---

## Rationale

PostgreSQL was selected because:
- ACID compliance required for financial transaction data
- JSON support enables semi-structured event logging
- Team has existing expertise; reduces onboarding time
- Open source; no licensing cost
- Proven at scale in similar workloads

### Alternatives Considered

- MySQL: Lacks robust JSON support
- DynamoDB: Cost prohibitive at scale; vendor lock-in
- MongoDB: Insufficient ACID guarantees for transactional requirements

## Implementation Notes

- Use connection pooling (pgBouncer) for high-concurrency workloads
- Enable replication for disaster recovery
- Index strategy for event queries: btree on timestamp, hash on event_type
- Schema versioning with Flyway migrations

## Consequences

- Operational overhead: postgres cluster management required
- Follow-on task: Set up automated backups and recovery procedures

## Cost Implications

- Compute: 2x db.t3.large instances (prod, replica) ≈ $500/month
- Storage: 100GB provisioned SSD ≈ $40/month
- Total: ~$540/month

## Security Considerations

- Enable SSL/TLS for all client connections
- Use IAM roles for application authentication (if on AWS)
- Implement row-level security for multi-tenant data
- Regular security patching via managed service updates

## Tags

database, backend, persistence

## Linked Task

task-2.3: Evaluate persistent storage options
```

---

## Example 2: Architectural Pattern

**Input**: "Implement event-driven architecture"

**Generated file**: `decision-0007-implement-event-driven-architecture.md`

```markdown
---
id: decision-0007
title: Implement event-driven architecture
date: 2026-03-25
status: Proposed
tags: architecture, messaging, scalability
linked_task: 
---

## Rationale

Event-driven architecture decouples services, enabling:
- Independent scaling of producers and consumers
- Asynchronous processing reduces latency on critical paths
- Event audit trail for compliance and debugging
- Kafka acts as the central nervous system for all domain events

## Alternatives Considered

- Request-response (REST): Tight coupling; synchronous bottlenecks
- RabbitMQ: Lacks event persistence; not suitable for audit trail

## Implementation Notes

- Use Kafka topics for domain events: `user.created`, `order.placed`, `payment.processed`
- Each service owns its topic(s)
- Consumer groups enable parallel processing
- Schema Registry enforces event structure

## Consequences

- Operational complexity: Kafka cluster management
- Developer learning curve: asynchronous patterns
- Follow-on: CDC (Change Data Capture) for existing databases

## Security Considerations

- Use mTLS for broker-to-broker and client-to-broker communication
- RBAC on topics per service
- Audit logging of all topic access

## Tags

architecture, messaging, scalability

## Linked Task

(none)
```

---

## Example 3: Rejected Decision

**Input**: "Migrate to microservices immediately"

**Generated file**: `decision-0008-migrate-to-microservices-immediately.md`

```markdown
---
id: decision-0008
title: Migrate to microservices immediately
date: 2026-03-25
status: Rejected
tags: architecture, deployment, scope
linked_task: task-1.5
---

## Rationale

Initial proposal to migrate entire monolith to microservices in Q2 2026.

## Alternatives Considered

- Immediate full migration: High risk, expensive, unknown timeline
- Gradual strangler pattern: Incrementally extract services; reduces risk
- Monolith optimization: Improve performance without architectural change

## Decision

**Rejected** in favor of strangler pattern approach.

## Consequences

- Extends timeline to Q4 2026
- Reduces operational risk and cost
- Allows team to learn microservices patterns incrementally
- Maintains ability to revert if approach doesn't work

## Notes

This decision was superseded by decision-0009 (Adopt strangler fig pattern). See decision-0009 for approved approach.

## Tags

architecture, deployment, scope

## Linked Task

task-1.5: Evaluate migration strategies
```
