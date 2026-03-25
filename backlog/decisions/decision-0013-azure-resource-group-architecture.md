---
id: decision-0013
title: Azure Resource Group Architecture for Multi-Region Kafka Deployment
date: 2026-03-25
status: Accepted
tags: infra, arch, azure, multi-region
linked_task: 
---

## Decision

Implement a dedicated resource group (RG) structure per region for Kafka application infrastructure (kafkaapp), with an additional centralized resource group (law) in the MEX region for Log Analytics. Each kafkaapp RG contains Kafka broker and Confluent platform VMs, networking, and security resources. This architecture ensures regional isolation, failure containment, and centralized observability.

## Architecture Overview

### Resource Group Deployment Structure

```
Azure Subscription
│
├── MEX Region
│   ├── rg-mex-kafkaapp
│   │   ├── VM: klc-vm-broker-prod-mexc (Kafka Broker)
│   │   ├── VM: klc-vm-confluentplat-prod-mexc (Confluent Platform)
│   │   ├── Key Vault: klc-keyvault-prod-mexc
│   │   ├── VNet: klc-vnet-prod-mexc
│   │   │   ├── Subnet: klc-snet-zero-prod-mexc
│   │   │   └── Subnet: klc-snet-one-prod-mexc
│   │   └── Network Security Groups (NSGs)
│   │
│   └── rg-mex-law
│       └── Log Analytics Workspace: klc-loganalytics-prod-mexc
│
├── CANE Region
│   └── rg-cane-kafkaapp
│       ├── VM: klc-vm-broker-prod-cane (Kafka Broker)
│       ├── VM: klc-vm-confluentplat-prod-cane (Confluent Platform)
│       ├── Key Vault: klc-keyvault-prod-cane
│       ├── VNet: klc-vnet-prod-cane
│       │   ├── Subnet: klc-snet-zero-prod-cane
│       │   └── Subnet: klc-snet-one-prod-cane
│       └── Network Security Groups (NSGs)
│
└── SCUS Region
    └── rg-scus-kafkaapp
        ├── VM: klc-vm-broker-prod-scus (Kafka Broker)
        ├── VM: klc-vm-confluentplat-prod-scus (Confluent Platform)
        ├── Key Vault: klc-keyvault-prod-scus
        ├── VNet: klc-vnet-prod-scus
        │   ├── Subnet: klc-snet-zero-prod-scus
        │   └── Subnet: klc-snet-one-prod-scus
        └── Network Security Groups (NSGs)
```

## Resource Component Details

### Per-Region KafkaApp Resource Groups (mex, cane, scus)

**Resource Group Name:** `rg-{region}-kafkaapp`

**Components:**
1. **VMs:**
   - **klc-vm-broker-prod-{region}**: Kafka Broker VM
     - Component Name: `broker`
     - Runs Kafka broker processes
   - **klc-vm-confluentplat-prod-{region}**: Confluent Platform VM
     - Component Name: `confluentplat`
     - Runs Confluent platform services (Confluent Control Center, Schema Registry, etc.)

2. **Networking:**
   - **VNet:** `klc-vnet-prod-{region}`
   - **Subnet 0:** `klc-snet-zero-prod-{region}` - Dedicated subnet for Kafka brokers
   - **Subnet 1:** `klc-snet-one-prod-{region}` - Dedicated subnet for system services and Confluent platform

3. **Security:**
   - **Key Vault:** `klc-keyvault-prod-{region}`
     - Stores secrets, certificates, and encryption keys
     - Manages credentials for broker authentication
   - **Network Security Groups:** Associated with subnets for ingress/egress rules

### Centralized Log Analytics Resource Group (MEX Region Only)

**Resource Group Name:** `rg-mex-law`
- **Component Name:** `law`
- **Resource:** Log Analytics Workspace `klc-loganalytics-prod-mexc`
  - Centralized logging and monitoring for all regions
  - Aggregates logs from all Kafka brokers and platform services
  - Provides unified analytics and alerting

## Naming Convention

Follows decision-0008 (Standardized Azure Resource Naming Convention):

- **Format:** `{customer-prefix}-{component}-{environment}-{region}`
  - Customer Prefix: `klc`
  - Component: `vm-broker`, `vm-confluentplat`, `keyvault`, `vnet`, `snet-zero`, `snet-one`, `loganalytics`
  - Environment: `prod`
  - Region: `mexc`, `cane`, `scus`
- **Examples:**
  - `klc-vm-broker-prod-mexc` (Kafka Broker VM in Mexico Central)
  - `klc-vnet-prod-cane` (Virtual Network in Canada East)
  - `klc-keyvault-prod-scus` (Key Vault in South Central US)
  - `klc-loganalytics-prod-mexc` (Log Analytics in Mexico Central)
  - `klc-snet-zero-prod-cane` (Broker Subnet in Canada East)
  - `klc-snet-one-prod-cane` (System Subnet in Canada East)

## Rationale

**Primary Driver:** Regional resiliency and failure isolation.

**Key Benefits:**
- **Regional Isolation:** Failure in one region does not directly impact other regions
- **Scalability:** Each region independently scales based on demand
- **Security Boundaries:** Separate Key Vaults per region with region-specific access policies
- **Operational Clarity:** Clear resource ownership and billing per region
- **Network Control:** Per-region VNets and subnets for traffic isolation
- **Centralized Observability:** Single MEX-based Log Analytics for monitoring all regions

## Consequences

- **Replication Complexity:** Cross-region Kafka cluster setup requires explicit replication configuration
- **Management Overhead:** Requires automation (Terraform) to consistently deploy across regions
- **Inter-Region Networking:** Requires VNet peering or ExpressRoute for cross-region communication
- **Cost Multiplier:** Resources replicated across 3 regions increases total infrastructure cost
- **Fault Domain:** Regional Azure outage would impact kafkaapp resources in that region (mitigated by multi-region design)

## Implementation Notes

1. **Terraform IaC:**
   - Create modules for RG, VNet, subnets, VMs, and Key Vault
   - Use region variables to deploy identical architecture per region
   - Reference decision-0009 (Terraform + AzAPI provider)

2. **Resource Deployment Order:**
   - Create Resource Groups (kafkaapp per region, law in MEX)
   - Deploy VNets (`klc-vnet-prod-{region}`) and subnets
   - Create Key Vaults (`klc-keyvault-prod-{region}`) with access policies
   - Deploy VMs (`klc-vm-broker-prod-{region}` and `klc-vm-confluentplat-prod-{region}`)
   - Configure Network Security Groups
   - Deploy Log Analytics workspace (`klc-loganalytics-prod-mexc`) in MEX law RG

3. **Networking Setup:**
   - Configure VNet peering between all regions (mex ↔ cane, mex ↔ scus, cane ↔ scus)
   - Establish routing rules for inter-cluster communication
   - Set up private endpoints for Log Analytics if required

4. **Security Configuration:**
   - Implement Managed Identity on VMs for Azure service access
   - Store VM credentials in regional Key Vaults
   - Apply NSG rules for broker-to-broker and platform service communication

5. **Monitoring Integration:**
   - Configure Log Analytics agents on all VMs
   - Create dashboards for per-region Kafka metrics
   - Set up alerts for critical thresholds

## Cost Considerations

- **Compute:** 2 VMs per region × 3 regions = 6 VMs (baseline cost multiplied by regions)
- **Storage:** 3 Key Vaults (minimal cost per vault)
- **Networking:** 3 VNets with 2 subnets each (pay-per-GB for cross-region traffic)
- **Observability:** 1 Log Analytics workspace (ingestion and retention costs)
- **Optimization:** Consider reserved instances for long-term cost reduction

## Related Decisions

- **Decision-0008:** Standardized Azure Resource Naming Convention
- **Decision-0009:** Use Terraform + AzAPI Provider for Infrastructure as Code
- **Decision-0010:** No Public Endpoints
- **Decision-0011:** Use Least Expensive VM SKU
- **Decision-0012:** Centralized Log Analytics for Monitoring
