---
id: TASK-3.1
title: Bootstrap Terraform State Backend
status: To Do
assignee: []
created_date: '2026-03-25 19:32'
labels: []
dependencies: []
references:
  - decision-0008
  - research-task-2.11
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create Azure Storage Account + blob container for Terraform remote state with blob-lease locking. This is the one manual terraform apply (chicken-and-egg bootstrap). Follow naming convention from decision-0008 (e.g. klc-tfstate-lab-scus). Output: infra/terraform/state-backend/ (main.tf, variables.tf, outputs.tf, providers.tf)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 terraform init and terraform apply succeed in state-backend/
- [ ] #2 Storage account + blob container exist in Azure
- [ ] #3 Subsequent root modules can configure this as their backend
<!-- AC:END -->
