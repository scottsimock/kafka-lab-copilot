---
id: decision-0008
title: Implement standardized Azure resource naming convention
date: 2026-03-25
status: Accepted
tags: azure, infrastructure, naming-convention, governance
linked_task: task-2.3
---

## Context

Azure resource naming needs standardization across all environments to:
- Enable consistent billing and cost tracking by customer/project
- Support role-based access control (RBAC) aligned with resource hierarchy
- Facilitate resource discovery and automation
- Maintain clarity when viewing resources across multiple subscriptions and resource groups
- Reduce operational confusion and naming conflicts

## Decision

All Azure resources will follow this standardized naming convention:

```
{customer-prefix}-{component}-{environment}-{region}
```

**Pattern breakdown:**

| Component | Format | Example | Notes |
|-----------|--------|---------|-------|
| **Customer Prefix** | 3 letters (lowercase) | `klc` | Uniquely identifies the customer or internal project |
| **Component** | 5–10 characters (lowercase, alphanumeric + hyphens) | `kafka`, `storage`, `vnet` | Describes the Azure resource type/purpose |
| **Environment** | Hierarchical parent (if applicable) | `prod`, `dev` | Identifies the environment or parent resource; omit if not applicable |
| **Region** | Azure region code (lowercase) | `mexc`, `scus`, `cane` | Deployment region (see Azure region abbreviations) |

**Examples:**

- Storage Account (production, Mexico Central): `klcstorageprodinmexc`
- Kafka Cluster (dev, South Central US): `klc-kafka-dev-scus`
- Virtual Network (prod, Canada East): `klc-vnet-prod-cane`
- Event Hub Namespace (dr, Canada East): `klc-eventhub-dr-cane`
- Key Vault (prod, Mexico Central): `klc-keyvault-prod-mexc`

- **Tenant, Subscription, and Resource Group naming** are excluded from this convention—they follow Azure organization practices at the tenant and subscription level.

## Consequences

### Implementation Requirements

- **New resources**: All future Azure resource deployments must follow this convention
- **Resource naming in IaC**: Terraform/ARM templates use this pattern in variable defaults
- **Documentation**: Update all infrastructure-as-code templates with naming variables
- **Automation**: Validation scripts can enforce this pattern (e.g., in CI/CD pipelines)
- **Exceptions**: Any deviation requires explicit approval and a documented reason in the resource tags or comments

### Affected Areas

- **Cloud infrastructure team**: Must validate all resource naming during deployment reviews
- **Terraform/ARM templates**: Update naming variables to enforce the pattern
- **CI/CD pipelines**: Add pre-deployment validation to ensure compliance
- **Azure Policy**: Optional—can be configured to prevent non-compliant resource creation
- **Cost tracking**: Use customer prefix in billing alerts and chargeback models
- **RBAC/Access Control**: Align role assignments with the resource naming hierarchy

### Benefits

- **Governance**: Consistent naming reduces confusion and supports compliance audits
- **Scalability**: Easy to onboard new customers/projects with the same pattern
- **Automation**: Scripts can parse resource names to determine environment, location, and purpose
- **Cost management**: Customer prefix enables accurate billing and cost allocation
- **Operational clarity**: Teams can quickly identify resource relationships and purposes

## Notes

This decision establishes a critical governance foundation for all Azure infrastructure management and should be enforced at the Infrastructure-as-Code level via Terraform validation and CI/CD enforcement.
