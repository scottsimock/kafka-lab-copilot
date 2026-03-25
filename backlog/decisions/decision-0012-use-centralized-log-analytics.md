---
id: decision-0012
title: Use Centralized Log Analytics for Kafka Infrastructure Monitoring
date: 2026-03-25
status: Accepted
tags: monitoring, observability, azure
linked_task: researchtask2.10
---

## Decision

Implement a centralized Log Analytics solution for aggregating, monitoring, and analyzing logs and metrics across all Kafka infrastructure deployed in the multi-region Azure environment.

## Rationale

**Primary Driver:** Unified monitoring and observability across all regions and components.

**Key Benefits:**
- **Centralized Visibility:** Single pane of glass for all Kafka brokers, topics, and clients across regions
- **Operational Efficiency:** Reduce time-to-resolution by correlating logs and metrics from all sources
- **Multi-Region Consistency:** Standardized logging and monitoring practices across all deployment regions
- **Compliance & Audit:** Centralized log retention and audit trail for compliance requirements
- **Performance Insights:** Unified analytics for identifying performance bottlenecks and optimization opportunities

## Consequences

- **Integration Effort:** Requires configuration of log shipping from all Kafka components to centralized solution
- **Data Volume & Cost:** Centralized logging increases ingestion and storage costs; requires retention policy tuning
- **Latency:** Slight network overhead for log transmission to central repository
- **Dependency:** System reliability depends on centralized logging platform availability

## Implementation Notes

- Configure Azure Log Analytics workspace in primary region with replication to secondary regions
- Deploy Log Analytics agents or extensions on all Kafka broker VMs
- Configure Kafka brokers to send logs to centralized workspace
- Establish log retention policies based on compliance and cost requirements
- Create standardized queries and dashboards for key metrics (throughput, latency, error rates)
- Set up alerts for critical conditions (broker failures, high latency, disk space)
- Document log schema and retention policies for team reference
