---
id: TASK-3
title: 'Phase 1: Foundation - Azure Infrastructure + CI/CD Pipeline'
status: To Do
assignee: []
created_date: '2026-03-25 19:32'
labels: []
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provision all Azure infrastructure and establish CI/CD pipeline. No Kafka software yet. 30-day Confluent trial starts when Phase 2 begins - complete Phase 1 fully before activating the trial.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 terraform plan runs clean with zero errors from GitHub Actions
- [ ] #2 terraform apply creates all resources in SCUS
- [ ] #3 Azure Bastion provides SSH access to jumpbox
- [ ] #4 From jumpbox, can SSH to all broker/ZK/CC/monitoring VMs
- [ ] #5 Key Vault contains CA cert, broker certs, and SCRAM credentials
- [ ] #6 Log Analytics workspace receives VM-level metrics
- [ ] #7 terraform destroy cleanly removes all resources
- [ ] #8 terraform apply after destroy recreates identical environment (idempotency)
- [ ] #9 GitHub Actions pipeline works end-to-end (PR plan to approval to apply)
<!-- AC:END -->
