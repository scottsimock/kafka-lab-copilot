---
id: TASK-3.5
title: Security Infrastructure
status: To Do
assignee: []
created_date: '2026-03-25 19:35'
labels: []
dependencies:
  - TASK-3.3
  - TASK-3.4
references:
  - decision-0010
  - research-task-2.7
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provision Azure Key Vault with self-signed CA, broker/ZK/CC certificates, SCRAM credentials, and managed identities. Azure Key Vault in SCUS. Self-signed CA certificate generation stored in Key Vault. Broker certificates: one per broker with SANs for hostnames. ZooKeeper certificate. Control Center certificate. SCRAM credential secrets stored in Key Vault. Managed identity for VMs to access Key Vault. Uses modules/key-vault-cert for cert generation. Output: infra/terraform/security/ (main.tf, variables.tf, outputs.tf, providers.tf, backend.tf)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Key Vault exists in SCUS with correct access policies
- [ ] #2 CA cert, 3 broker certs, ZK cert, CC cert stored in Key Vault
- [ ] #3 SCRAM secrets stored in Key Vault
- [ ] #4 Managed identity can read secrets/certs from Key Vault
<!-- AC:END -->
