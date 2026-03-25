---
id: decision-0007
title: Azure regional deployment strategy
date: 2026-03-25
status: Accepted
tags: infrastructure, cloud, deployment, disaster-recovery
linked_task: task-2.3
---

## Rationale

The customer's primary user base is located in Mexico, with secondary usage in the southern United States. To optimize for customer usage patterns and provide disaster recovery capability, we will implement a multi-region Azure deployment strategy:

**Regional distribution:**

| Region | Prefix | Role | Description |
|--------|--------|------|-------------|
| **Mexico Central** | `mexc` | Primary (Active) | Closest to main customer usage; lowest latency for majority of requests |
| **South Central US** | `scus` | Secondary (Active) | Active-active region for secondary usage patterns; provides redundancy and load distribution |
| **Canada East** | `cane` | Disaster Recovery (Standby) | Warm standby for disaster recovery; geographic separation from primary regions for resilience against regional Azure outages |

**Key drivers:**
- **User proximity**: Mexico Central deployment optimizes latency and performance for primary customer base
- **High availability**: Active-active across Mexico Central and South Central US eliminates single points of failure
- **Disaster recovery**: Canada East provides geographic isolation and recovery capacity in case of regional failures
- **No alternatives evaluated**: Customer specified regional requirements based on their infrastructure and usage analysis

## Implementation Notes

### Regional topology

- **Mexico Central (Active)**: Primary production environment; primary data residency
- **South Central US (Active)**: Secondary production environment; full redundancy and load distribution
- **Canada East (Standby)**: Disaster recovery replica with warm standby configuration

### Deployment patterns

- **Active-active deployment**: Both Mexico Central and South Central US run full application stacks simultaneously
- **Load balancing**: Azure Traffic Manager or equivalent routes traffic between Mexico Central and South Central US based on latency and health checks
- **Data replication**: Database and persistent storage replicated between Mexico Central and South Central US for consistency
- **Canada East replication**: Asynchronous replication from primary regions to Canada East for recovery capability

### Failover strategy

- **Automatic failover**: Traffic Manager automatically reroutes to healthy region if Mexico Central or South Central US becomes unavailable
- **Disaster recovery activation**: In case of multi-region failure, manually activate Canada East as the primary region (documented procedure required)
- **RTO/RPO targets**: Define recovery time objective (RTO) and recovery point objective (RPO) based on business requirements (not yet specified)

### Configuration management

- **Infrastructure-as-Code**: Terraform/ARM templates define identical infrastructure in all three regions for rapid deployment
- **Secrets and configuration**: Use Azure Key Vault replicated across regions; application code sources region-specific endpoints from configuration
- **Monitoring**: Azure Monitor tracks health and performance of all three regions; alerting on regional failures
- **DNS**: Azure DNS or Traffic Manager routes requests based on geographic proximity and health status

### Network architecture

- **Virtual networks**: Independent VNets in each region; connected via Azure ExpressRoute or VPN for cross-region communication
- **Security**: Network security groups (NSGs) enforce consistent security policies across all regions
- **DDoS protection**: Azure DDoS Protection enabled in all regions

## Notes

- **Formal RTO/RPO requirements**: Business needs to define acceptable recovery time and data loss objectives
- **Cost implications**: Active-active deployment incurs costs for resources in two primary regions; Canada East standby has lower cost but still incurs storage/replication costs
- **Data residency compliance**: Verify Mexico Central and South Central US meet any customer data residency or regulatory requirements
- **Disaster recovery testing**: Establish regular DR drills to validate Canada East failover procedures
- **Future scaling**: If customer usage patterns shift, revisit this decision for regional rebalancing
