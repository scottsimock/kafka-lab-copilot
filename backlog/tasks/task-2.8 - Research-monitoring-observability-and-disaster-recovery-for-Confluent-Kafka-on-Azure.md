---
id: TASK-2.8
title: >-
  Research monitoring, observability, and disaster recovery for Confluent Kafka
  on Azure
status: To Do
assignee: []
created_date: '2026-03-23 22:27'
labels:
  - research
  - kafka
  - monitoring
  - observability
  - disaster-recovery
dependencies: []
parent_task_id: TASK-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research and document monitoring, alerting, and disaster recovery (DR) strategies for multi-region Confluent Kafka clusters on Azure VMs. Cover: (1) Confluent Control Center metrics and dashboards for multi-region cluster health, (2) JMX metrics export to Azure Monitor, Prometheus, or Grafana, (3) Key broker metrics to alert on (under-replicated partitions, ISR shrinkage, consumer lag, produce/fetch latency), (4) Azure Monitor integration and Log Analytics workspace configuration, (5) Automated DR runbook for region failover — detecting failure, promoting observer replicas, redirecting producers, (6) RPO/RTO targets and how to validate them with chaos testing, (7) Backup and restore strategies for Kafka topic data (Azure Blob Storage sink connector).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Key Kafka metrics and alert thresholds are documented
- [ ] #2 Azure Monitor and Prometheus/Grafana integration approach is documented
- [ ] #3 DR runbook for region-level failover is documented step-by-step
- [ ] #4 RPO/RTO targets and validation approach are specified
- [ ] #5 Kafka topic backup to Azure Blob Storage is documented
<!-- AC:END -->
