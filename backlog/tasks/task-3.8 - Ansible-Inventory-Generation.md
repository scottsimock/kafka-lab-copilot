---
id: TASK-3.8
title: Ansible Inventory Generation
status: To Do
assignee: []
created_date: '2026-03-25 19:36'
labels: []
dependencies:
  - TASK-3.6
references:
  - research-task-2.11
parent_task_id: TASK-3
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate Ansible inventory files from Terraform outputs for use in Phase 2. Terraform outputs VM IPs, hostnames, Key Vault URIs. Script or Terraform local_file resource to generate Ansible inventory from TF output. Inventory includes host vars: broker IDs, ZK IDs, cert paths, Key Vault references. Host groups: kafka_broker, zookeeper, control_center, monitoring, jumpbox. Output: infra/ansible/inventory/ (hosts.yml or hosts.ini, group_vars/)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Running terraform output or a generation script produces a valid Ansible inventory
- [ ] #2 Inventory includes all 7 VMs with correct group assignments
- [ ] #3 Host vars include broker IDs, cert paths, and Key Vault URIs
- [ ] #4 ansible-inventory --list parses the inventory without errors
<!-- AC:END -->
