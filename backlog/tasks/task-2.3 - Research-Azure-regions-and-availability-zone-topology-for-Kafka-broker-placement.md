---
id: TASK-2.3
title: >-
  Research Azure regions and availability zone topology for Kafka broker
  placement
status: To Do
assignee: []
created_date: '2026-03-23 22:25'
labels:
  - research
  - azure
  - availability-zones
  - topology
dependencies: []
parent_task_id: TASK-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research Azure region and availability zone (AZ) topology as it pertains to distributing Confluent Kafka brokers and ZooKeeper/KRaft controllers. Document: (1) How Azure AZs map to physical fault domains and latency expectations between zones, (2) Minimum broker counts per zone for replication factor 3, (3) Recommended region pairs for disaster recovery in Azure, (4) Proximity placement groups and their impact on intra-cluster latency, (5) How to spread brokers across AZs using Azure VM Scale Sets or individual VMs to ensure no single AZ failure takes down the cluster.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Azure AZ latency characteristics between zones and across regions are documented
- [ ] #2 Recommended Azure region pairs for multi-region Kafka are listed
- [ ] #3 Broker placement strategy across 3 AZs with rack awareness configuration is documented
- [ ] #4 Proximity placement group guidance is included
- [ ] #5 Minimum broker count recommendations per AZ and per region are specified
<!-- AC:END -->
