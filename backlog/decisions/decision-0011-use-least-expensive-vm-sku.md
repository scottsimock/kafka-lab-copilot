---
id: decision-0011
title: Use Least Expensive VM SKU for Kafka Infrastructure on Azure
date: 2026-03-25
status: Accepted
tags: infra, cost-optimization, azure
linked_task: 
---

## Decision

Based on research findings, adopt the least expensive Azure VM SKU that meets performance requirements for Kafka broker infrastructure in the multi-region deployment.

## Rationale

**Primary Driver:** Cost optimization is critical for the lab environment and production deployments. Selecting the least expensive VM SKU that satisfies throughput and latency requirements reduces infrastructure costs without compromising functionality.

**Key Benefits:**
- Lower operational expenditure across multi-region deployments
- Reduced per-instance licensing and compute costs
- Maintains adequate performance for Kafka workloads while optimizing budget allocation

## Alternatives Considered

1. **Premium/High-Performance VMs** - Rejected due to unnecessary cost overhead for lab and testing purposes
2. **Mixed SKU Strategy** - Considered but adds operational complexity
3. **Reserved Instances** - Complementary to this decision; can be applied on top of SKU selection

## Consequences

- **Cost Benefit:** Significant reduction in monthly compute spend across all regions
- **Performance Trade-off:** Must validate minimum performance characteristics meet throughput SLAs
- **Scalability:** May require more instances horizontally to achieve performance targets
- **Future Consideration:** As workloads grow, re-evaluation may be needed if performance becomes limiting

## Implementation Notes

- Research and benchmark available Azure VM SKUs (B-series, D-series, E-series) for Kafka workloads
- Document selected SKU with performance validation results
- Update IaC templates (Terraform) to use selected SKU across all regions
- Establish monitoring and alerting for resource utilization and performance metrics
