---
id: TASK-3.3
title: Terraform Shared Modules
status: To Do
assignee: []
created_date: '2026-03-25 19:33'
labels: []
dependencies:
  - TASK-3.1
references:
  - decision-0008
  - decision-0011
  - research-task-2.4
  - research-task-2.11
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build reusable Terraform modules for VMs, NSG rules, and Key Vault certificates. modules/vm: Standard VM creation with tags, managed disks, managed identity, parameterized SKU (default Standard_D4s_v5). modules/nsg-rules: Reusable NSG rule definitions for Kafka ports (9092/9093, 2181, 9021, 9999, 9090, 3000). modules/key-vault-cert: Certificate generation and Key Vault storage. All modules follow naming convention from decision-0008 and are parameterized for multi-region reuse. Output: infra/terraform/modules/vm/, infra/terraform/modules/nsg-rules/, infra/terraform/modules/key-vault-cert/
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each module has main.tf, variables.tf, outputs.tf with full variable documentation
- [ ] #2 terraform validate passes for each module
- [ ] #3 Modules are parameterized for reuse in Phase 3 (second region)
<!-- AC:END -->
