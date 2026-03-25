---
id: TASK-3.7
title: Monitoring Infrastructure
status: To Do
assignee: []
created_date: '2026-03-25 19:36'
labels: []
dependencies:
  - TASK-3.4
  - TASK-3.6
references:
  - decision-0012
  - research-task-2.8
parent_task_id: TASK-3
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provision Azure Log Analytics workspace and configure Azure Monitor agent for all VMs. Azure Log Analytics workspace in SCUS. Azure Monitor agent configuration for all VMs. Prometheus and Grafana VMs are provisioned in task-3.6; this task configures Log Analytics + Monitor agent. Output: infra/terraform/monitoring/ (main.tf, variables.tf, outputs.tf, providers.tf, backend.tf)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Log Analytics workspace exists in SCUS
- [ ] #2 Azure Monitor agent installed and reporting on all VMs
- [ ] #3 VM heartbeat metrics visible in Log Analytics
<!-- AC:END -->
