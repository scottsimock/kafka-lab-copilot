---
id: TASK-2.4
title: Research Azure VM sizing and storage configuration for Confluent Kafka brokers
status: To Do
assignee: []
created_date: '2026-03-23 22:26'
labels:
  - research
  - azure
  - vm-sizing
  - storage
  - performance
dependencies: []
parent_task_id: TASK-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research and document Azure VM series and sizes recommended for Confluent Kafka broker and ZooKeeper/KRaft controller VMs. Cover: (1) Recommended VM families (Lsv3, Esv5, Dsv5) and their disk throughput and IOPS characteristics, (2) Azure Managed Disk types (Premium SSD, Ultra Disk, Premium SSD v2) and best practices for Kafka log directories, (3) Disk striping and RAID-0 configurations for throughput, (4) OS disk vs data disk separation, (5) Ephemeral OS disk considerations, (6) Network bandwidth requirements and accelerated networking, (7) Confluent-specific tuning recommendations for disk flush and retention.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Recommended VM series for brokers and controllers are listed with rationale
- [ ] #2 Managed disk type comparison (Premium SSD vs Ultra Disk) is documented for Kafka workloads
- [ ] #3 Disk attachment and striping best practices are documented
- [ ] #4 Network bandwidth and accelerated networking requirements are documented
- [ ] #5 OS-level tuning parameters for Kafka on Linux are listed
<!-- AC:END -->
