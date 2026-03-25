---
id: decision-0009
title: Use Terraform azapi provider for infrastructure as code
date: 2026-03-25
status: Accepted
tags: infrastructure, terraform, azure, iac
linked_task: task-2.11
---

## Context

Kafka-lab infrastructure is deployed across multiple Azure regions (Mexico Central, South Central US, Canada East) as defined in decision-0007. Managing Azure resources requires consistent, repeatable, and version-controlled infrastructure-as-code (IaC) tooling.

The Terraform azapi provider is a specialized Azure provider that:
- Supports **any** Azure resource type (including preview and private APIs) without waiting for Terraform provider updates
- Enables declarative infrastructure management
- Ensures consistent resource naming per decision-0008 (naming convention)
- Supports multi-region deployments with reusable modules
- Integrates with CI/CD pipelines for automated deployment validation

## Decision

All infrastructure will be provisioned and managed using **Terraform with the azapi provider**. This is the single source of truth for all Azure resources.

**Scope:**
- All production and non-production Azure resources
- All three deployment regions (Mexico Central, South Central US, Canada East)
- Storage accounts, Virtual Networks, Kafka clusters, Event Hubs, Key Vaults, and related resources

**What terraform manages:**
- Resource Groups (per region and environment)
- Virtual Networks and subnets
- Storage accounts and containers
- Kafka/Event Hub resources
- Key Vaults and secrets
- Security groups and network policies
- Monitoring and alerting resources

**Out of scope (managed separately):**
- Azure subscriptions and billing
- Tenant-level policies and RBAC
- Manual post-deployment configuration (if any)

## Rationale

We chose the azapi provider over other approaches because:

**Terraform + azapi advantages:**
- **Complete Azure API coverage**: Supports all Azure resources (GA, preview, private APIs) without provider lag
- **Infrastructure-as-Code best practice**: Version control, code review, and audit trails for all infrastructure changes
- **Multi-region support**: Easily replicate infrastructure across Mexico Central, South Central US, and Canada East
- **Naming convention enforcement**: Variables can enforce decision-0008 naming patterns
- **Team familiarity**: Terraform is industry standard; azapi is straightforward
- **CI/CD integration**: Plan/apply workflows fit naturally into GitHub Actions or similar pipelines

**Alternatives considered:**
- **ARM templates**: Verbose JSON, less version-control friendly, harder to manage across environments
- **Azure CLI scripts**: Imperative approach, difficult to track state, error-prone for multi-region deployments
- **No IaC (manual Azure Portal)**: No audit trail, inconsistent naming, high error rate, not repeatable
- **Terraform AzureRM provider alone**: Limited to GA resources; misses preview and niche APIs; requires waiting for provider updates

**azapi over AzureRM:**
- azapi reaches **100% of Azure APIs** (via REST); AzureRM provider lags behind Azure releases
- azapi is lighter-weight and actively maintained by HashiCorp for edge cases
- azapi can coexist with azurerm for hybrid scenarios (though we standardize on azapi for simplicity)

## Implementation Notes

### Repository structure

```
terraform/
├── main.tf                 # Provider config (azapi, azurerm for data sources)
├── variables.tf            # Common variables (customer prefix, regions, environments)
├── outputs.tf              # Shared outputs
├── versions.tf             # Provider version constraints
├── terraform.tfvars        # Shared values (customer prefix klc, environments)
├── modules/
│   ├── vnet/               # Virtual network module (reusable across regions)
│   ├── storage/            # Storage account module
│   ├── keyvault/           # Key Vault module
│   └── kafka/              # Kafka cluster module (if using Event Hubs)
└── environments/
    ├── prod/               # Production environment configs
    │   ├── main.tf
    │   ├── terraform.tfvars
    │   └── regions/
    │       ├── mexc.tf     # Mexico Central resources
    │       ├── scus.tf     # South Central US resources
    │       └── cane.tf     # Canada East resources
    ├── dev/                # Dev environment configs
    └── qa/                 # QA environment configs
```

### Naming convention integration

All resources use the naming convention from decision-0008:
```hcl
resource "azapi_resource" "storage" {
  name = "${var.customer_prefix}-${var.component}-${var.environment}-${var.region}"
  # Example: klc-storage-prod-mexc
}
```

Variables enforce the pattern:
```hcl
variable "customer_prefix" {
  default = "klc"
  # 3 letters
}

variable "region" {
  type = map(string)
  default = {
    primary   = "mexc"
    secondary = "scus"
    dr        = "cane"
  }
}
```

### Provider configuration

```hcl
terraform {
  required_providers {
    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.0"
    }
  }
}

provider "azapi" {
  subscription_id = var.azure_subscription_id
}
```

### Deployment workflow

1. **Plan**: `terraform plan -var-file=environments/prod/terraform.tfvars` — preview changes
2. **Review**: Code review via GitHub PRs before apply
3. **Apply**: `terraform apply` — deploy to Azure
4. **Verify**: CI/CD validates resource names match decision-0008 pattern
5. **State management**: Remote state stored in Azure Storage (locked with DynamoDB or Blob lease)

### State management

- **Remote state**: Store `.tfstate` in Azure Storage blobs for multi-region deployments
- **Locking**: Use Azure blob leases or DynamoDB to prevent concurrent modifications
- **Backup**: Regular snapshots of state files
- **Access control**: Restrict state file access via RBAC and storage account firewalls

### Multi-region module strategy

Create reusable modules parametrized by region:
```hcl
module "vnet_mexc" {
  source = "./modules/vnet"
  region = var.regions.primary
  region_prefix = "mexc"
}

module "vnet_scus" {
  source = "./modules/vnet"
  region = var.regions.secondary
  region_prefix = "scus"
}
```

### Validation and CI/CD

- **terraform validate**: Syntax checking in CI/CD
- **terraform fmt**: Code formatting standards
- **tflint**: Custom linting rules (e.g., enforce naming patterns)
- **policy as code**: Sentinel or OPA policies to block non-compliant resource names
- **pre-commit hooks**: Validate naming convention before commit

### Secrets and credentials

- Use Azure Key Vault for secrets (referenced in Terraform)
- Service principal authentication via environment variables (`ARM_CLIENT_ID`, etc.)
- GitHub Actions or similar CI/CD manages credentials securely
- Never commit secrets to version control

### Documentation requirements

- Document each module's purpose and inputs/outputs
- Maintain a runbook for common operations (plan, apply, destroy)
- Link Terraform changes to backlog tasks and decisions
- Track infrastructure changes via git commit history

## Consequences

### What changes

- **Deployment workflow**: All Azure resources deployed via Terraform, not manual Portal clicks
- **Change management**: Every infrastructure change requires a Terraform PR and code review
- **Team responsibility**: Infrastructure engineers must maintain Terraform code as application code
- **Version control**: Infrastructure history lives in git alongside application code

### Implementation requirements

- **Repository setup**: Create `terraform/` directory structure as outlined
- **Module development**: Build reusable modules for common resource types
- **CI/CD integration**: Add Terraform plan/apply jobs to GitHub Actions
- **State backend**: Configure Azure Storage for remote state
- **Team training**: Ensure all engineers understand Terraform workflow and azapi provider
- **Documentation**: Write runbooks for deployment, rollback, and disaster recovery
- **Compliance**: Validate that Terraform outputs comply with decision-0008 naming convention

### Benefits

- **Repeatability**: Identical infrastructure provisioned consistently across all regions
- **Auditability**: Full git history of all infrastructure changes
- **Disaster recovery**: Terraform can rebuild entire infrastructure from code in minutes
- **Cost tracking**: Resource names follow decision-0008 convention for billing analysis
- **Governance**: Code review gates ensure compliance before deployment
- **Scalability**: Adding new resources or regions is as simple as adding Terraform code

### Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| State file corruption | Regular backups; use Azure Storage redundancy; lock mechanism to prevent concurrent modifications |
| Accidental resource deletion | Terraform destroy requires explicit approval; critical resources marked with `prevent_destroy` lifecycle rule |
| Provider version incompatibility | Pin azapi provider version in `versions.tf`; test version upgrades in dev first |
| Credential exposure | Use Azure Key Vault and managed identities; never commit credentials; rotate service principal keys regularly |
| Drift from declared state | Regular `terraform plan` audits; enforce GitOps principle (code is source of truth) |

### Affected areas

- **Infrastructure team**: Owns Terraform code maintenance and module updates
- **CI/CD pipelines**: Must support Terraform plan/apply workflows
- **Git workflow**: Require code review for all infrastructure PRs (via GitHub or similar)
- **Azure subscriptions**: Service principal needs appropriate RBAC roles
- **Security team**: Validate remote state backend security; review credential management
- **Monitoring/alerting**: Terraform can provision Azure Monitor resources and dashboards

## Notes

This decision establishes Terraform and azapi as the canonical infrastructure provisioning tools for the kafka-lab project. All infrastructure changes must flow through this IaC workflow to maintain consistency and auditability.
