---
id: TASK-3.4
title: Network Infrastructure
status: To Do
assignee: []
created_date: '2026-03-25 19:33'
labels: []
dependencies:
  - TASK-3.3
references:
  - decision-0007
  - decision-0010
  - decision-0013
  - research-task-2.5
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provision the full network topology in South Central US (SCUS) with multi-subnet design, NSGs, and Azure Bastion. VNet in SCUS with address space planned for future multi-region peering. Subnets: broker, zookeeper, management/control-center, monitoring, bastion (AzureBastionSubnet). NSGs per subnet with explicit allow rules for required ports. No public IPs on any resource (per decision-0010). Azure Bastion subnet + Bastion host for secure access. Uses modules/nsg-rules for NSG rule definitions. Output: infra/terraform/network/ (main.tf, variables.tf, outputs.tf, providers.tf, backend.tf)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 VNet, all subnets, and NSGs created in SCUS
- [ ] #2 NSG rules allow only expected ports per subnet
- [ ] #3 Azure Bastion deployed and functional
- [ ] #4 No public IPs assigned to any subnet (except Bastion required public IP)
- [ ] #5 terraform plan shows clean output
<!-- AC:END -->
