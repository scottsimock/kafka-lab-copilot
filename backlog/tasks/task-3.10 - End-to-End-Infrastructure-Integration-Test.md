---
id: TASK-3.10
title: End-to-End Infrastructure Integration Test
status: To Do
assignee: []
created_date: '2026-03-25 19:37'
labels: []
dependencies:
  - TASK-3.2
  - TASK-3.9
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Validate the complete infrastructure works end-to-end: Bastion connectivity, SSH access, Log Analytics, and CI/CD pipeline. Validate Bastion connectivity: SSH to jumpbox via Azure Bastion. From jumpbox, SSH to all private VMs (brokers, ZK, CC, monitoring). Validate Log Analytics workspace receives VM heartbeat metrics. Validate GitHub Actions pipeline works end-to-end (PR plan to approval to apply). Validate terraform destroy cleanly removes all resources. Validate terraform apply after destroy recreates identical environment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bastion SSH to jumpbox succeeds
- [ ] #2 From jumpbox, SSH to all broker/ZK/CC/monitoring VMs succeeds
- [ ] #3 Log Analytics receives VM heartbeat data
- [ ] #4 GitHub Actions pipeline runs end-to-end successfully
- [ ] #5 terraform destroy cleanly removes all resources
- [ ] #6 terraform apply after destroy recreates identical environment
<!-- AC:END -->
