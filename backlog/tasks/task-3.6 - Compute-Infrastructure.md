---
id: TASK-3.6
title: Compute Infrastructure
status: To Do
assignee: []
created_date: '2026-03-25 19:35'
labels: []
dependencies:
  - TASK-3.3
  - TASK-3.4
  - TASK-3.5
references:
  - decision-0008
  - decision-0011
  - decision-0013
  - research-task-2.4
  - research-task-2.3
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provision all VMs for brokers, ZooKeeper, jumpbox, Control Center, and monitoring. 3x Standard_D4s_v5 VMs for Kafka brokers (spread across availability zones). 1x Standard_D4s_v5 VM for ZooKeeper. 1x Standard_D2s_v5 VM for jumpbox (management). 1x Standard_D4s_v5 VM for Control Center. 1x Standard_D4s_v5 VM for monitoring (Prometheus + Grafana). Premium SSD managed disks for broker log dirs. All VMs tagged: environment=lab, component=kafka|zk|cc|monitoring|jumpbox. Uses modules/vm for VM creation. Output: infra/terraform/compute/ (main.tf, variables.tf, outputs.tf, providers.tf, backend.tf)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 7 VMs deployed in correct subnets
- [ ] #2 Brokers spread across availability zones
- [ ] #3 Premium SSD disks attached to broker VMs
- [ ] #4 All VMs tagged correctly for identification
- [ ] #5 VMs have managed identity assigned for Key Vault access
<!-- AC:END -->
