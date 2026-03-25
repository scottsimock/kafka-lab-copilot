---
id: decision-0010
title: No public endpoints
date: 2026-03-25
status: Accepted
tags: security, networking, infrastructure
linked_task: 
---

## Context

Kafka-lab infrastructure requires network access controls to ensure secure operation. A critical architectural question is whether Kafka brokers, ZooKeeper, and other components should be accessible via public internet endpoints or remain isolated to private networks.

## Decision

All Kafka infrastructure components will operate **without public endpoints**. All services will be:
- Deployed on private subnets within Azure Virtual Networks
- Accessible only via private IP addresses
- Connected to client applications through private network connectivity (e.g., VNet peering, ExpressRoute, site-to-site VPN, or private endpoints)

**Scope:**
- Kafka brokers
- ZooKeeper ensembles
- Confluent Control Center
- Schema Registry
- Kafka Connect instances
- Monitoring and management interfaces
- All administrative dashboards

## Rationale

This decision is driven by **security** requirements:

1. **Attack Surface Reduction**: Eliminating public endpoints prevents direct internet-based attacks on Kafka infrastructure. By limiting network exposure to private networks only, we significantly reduce the attack surface.

2. **Compliance and Regulatory**: Many regulatory frameworks (PCI-DSS, HIPAA, SOC 2) require sensitive infrastructure like message brokers to be on private networks with controlled access.

3. **Data Protection**: Kafka clusters often process sensitive business data. Public endpoints increase the risk of unauthorized data exposure, eavesdropping, or interception.

4. **DDoS Mitigation**: Private infrastructure is inherently protected from public DDoS attacks, as the services cannot be reached from the internet.

5. **Access Control**: By restricting access to private networks, we can enforce more granular identity-based access controls at the application and network layer without exposing authentication to the internet.

6. **Azure Best Practices**: Azure security guidance recommends keeping sensitive services on private networks and using Azure Private Endpoints, VPN gateways, or ExpressRoute for client connectivity.

## Implementation Notes

### Network Architecture

All Kafka components will be deployed in isolated subnets within Virtual Networks:

```
Azure Subscription
├── Resource Group (per region)
│   ├── VNet (private network)
│   │   ├── Subnet: Kafka Brokers (private)
│   │   ├── Subnet: ZooKeeper (private)
│   │   ├── Subnet: Confluent Control Center (private)
│   │   └── Subnet: Monitoring (private)
│   ├── VPN Gateway or ExpressRoute (for client access)
│   └── Private Endpoint (for Azure services)
```

### Client Connectivity Options

Applications and administrators will access Kafka through private connectivity channels:

1. **VNet Peering**: For clients in other Azure VNets (same region or cross-region)
2. **ExpressRoute**: For on-premises or hybrid cloud clients requiring dedicated private connectivity
3. **Site-to-Site VPN**: For secure remote client access
4. **Private Endpoints**: For Azure services accessing Kafka from private networks
5. **Bastion Hosts**: For administrative SSH/RDP access to management VMs

### Network Security Groups (NSGs)

NSG rules will enforce:
- Inbound rules: Only allow traffic from authorized private IP ranges (client VNets, VPN clients)
- Outbound rules: Restrict outbound traffic to necessary services only (e.g., Azure Storage, Key Vault)
- No rules accepting traffic from 0.0.0.0/0 (public internet)

### Load Balancing

- Internal load balancers only (no public load balancers)
- Traffic routed via private IP addresses
- Health checks via private network

### Monitoring and Observability

- Azure Monitor and Log Analytics remain private (no public dashboard URLs)
- Grafana and Prometheus (if used) deployed on private infrastructure
- Admin access via VPN or Bastion Host only

### Terraform Implementation

Using decision-0009 (Terraform azapi provider), network isolation will be enforced:

```hcl
# Example: Kafka broker in private subnet
resource "azapi_resource" "kafka_nic" {
  name                = "klc-kafka-nic-prod-${var.region}"
  parent_id           = azapi_resource.resource_group.id
  type                = "Microsoft.Network/networkInterfaces"
  
  body = jsonencode({
    properties = {
      ipConfigurations = [{
        name = "ipconfig1"
        properties = {
          subnet = {
            id = azapi_resource.private_subnet.id  # Private subnet only
          }
          privateIPAllocationMethod = "Dynamic"
          # NOTE: No public IP address
        }
      }]
    }
  })
}
```

### Documentation Requirements

- Maintain network diagrams showing private network topology
- Document VPN/ExpressRoute connectivity procedures
- Create runbooks for client onboarding (VNet peering, VPN setup)
- Maintain access control matrix (who can access Kafka via which channel)

## Consequences

### What Changes

- **No direct internet access**: Kafka brokers cannot be accessed from the public internet
- **Connectivity model shifts**: Clients must establish private network connectivity (VPN, VNet peering, ExpressRoute)
- **Operational complexity**: Initial setup requires VPN/ExpressRoute infrastructure
- **Administrative access**: Admins must use VPN or Bastion Host to manage Kafka clusters

### Benefits

- **Enhanced Security**: Significant reduction in attack surface and vulnerability exposure
- **Compliance**: Supports regulatory compliance requirements (PCI-DSS, HIPAA, SOC 2, etc.)
- **Privacy**: Sensitive data remains isolated to private networks
- **DDoS Immunity**: No public endpoints means protection from internet-based DDoS attacks
- **Controlled Access**: All access is logged and can be audited via Azure Network Watcher

### Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Client connectivity complexity | Provide clear documentation and runbooks for VPN/VNet peering setup |
| Increased operational burden | Automate VPN and VNet peering provisioning via Terraform |
| Latency from VPN/ExpressRoute | Use Azure ExpressRoute for performance-critical clients; use same-region VNet peering for low-latency access |
| Single point of failure (VPN gateway) | Deploy redundant VPN gateways; use Azure VPN High Availability configuration |
| Harder to troubleshoot | Leverage Azure Network Watcher, NSG flow logs, and diagnostic tools |
| Third-party integrations requiring internet access | Use Azure Application Gateway or API Gateway as intermediary |

### Affected Areas

- **Network/Infrastructure Team**: Owns VNet design, NSG rules, VPN/ExpressRoute configuration
- **Security Team**: Reviews network policies and access controls
- **Application Teams**: Must integrate with VPN/VNet peering for Kafka access
- **DevOps/CI-CD**: Must support private network deployments; integrate VPN connectivity into deployment pipelines
- **Monitoring/Observability**: All monitoring infrastructure must be private

## Notes

This decision establishes a **private-by-default** architecture for all Kafka infrastructure. Combined with decision-0007 (multi-region deployment) and decision-0009 (Terraform IaC), this creates a secure, compliant, and repeatable infrastructure model for the kafka-lab project.

All future infrastructure decisions should assume private networks unless explicitly approved otherwise.
