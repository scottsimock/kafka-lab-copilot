---
id: TASK-2.5
title: >-
  Research Azure networking architecture for cross-region and cross-AZ Confluent
  Kafka
status: To Do
assignee: []
created_date: '2026-03-23 22:26'
labels:
  - research
  - azure
  - networking
  - vnet
  - security
dependencies: []
parent_task_id: TASK-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research and document the Azure networking architecture required to support Confluent Kafka clusters spanning multiple regions and availability zones. Cover: (1) VNet design per region and global VNet peering vs Azure Virtual WAN for cross-region broker communication, (2) Private Link and Private Endpoints for secure client connectivity, (3) Network Security Groups (NSGs) and required port rules for Kafka (9092, 9093, 9094) and ZooKeeper (2181, 2888, 3888), (4) DNS resolution across regions using Azure Private DNS Zones, (5) ExpressRoute vs VPN Gateway for on-premises connectivity, (6) Bandwidth and latency SLAs between Azure regions, (7) Azure Load Balancer placement for client-facing bootstrap endpoints.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 VNet peering vs Virtual WAN trade-offs for cross-region Kafka are documented
- [ ] #2 NSG rule sets for Kafka and ZooKeeper/KRaft ports are specified
- [ ] #3 Private DNS zone configuration for cross-region broker discovery is documented
- [ ] #4 Azure Load Balancer design for Kafka bootstrap endpoints is documented
- [ ] #5 Latency expectations between Azure regions and AZs are quantified
<!-- AC:END -->
