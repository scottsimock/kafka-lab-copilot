---
id: decision-0009
title: DevOps Deployments
date: 2026-03-25
status: Accepted
tags: devops, terraform, azapi, ansible, github-actions, ci-cd, iac
linked_task: task-2.11
---

## Context

Kafka-lab infrastructure spans multiple Azure regions (Mexico Central, South Central US, Canada East) as defined in decision-0007. A robust DevOps deployment strategy is required that addresses three distinct concerns:

1. **Infrastructure provisioning** — creating and managing Azure resources (VMs, VNets, storage, etc.)
2. **Application configuration** — installing and configuring Confluent Kafka software on provisioned VMs
3. **CI/CD automation** — orchestrating validation, deployment, and rollback workflows

Research (task-2.11) evaluated Terraform, ARM templates, Azure CLI, and Ansible across multiple criteria. The conclusion is a **three-tool DevOps stack** that provides clear separation of concerns and leverages each tool's strengths.

## Decision

The kafka-lab project adopts a **three-pillar DevOps deployment strategy**:

| Pillar | Tool | Responsibility |
|--------|------|---------------|
| Infrastructure as Code | **Terraform with azapi provider** | Provision and manage all Azure resources |
| Configuration Management | **Ansible** | Install, configure, and manage Confluent Kafka on VMs |
| CI/CD Automation | **GitHub Actions** | Orchestrate validation, deployment pipelines, and approvals |

### Pillar 1: Terraform with azapi Provider — Infrastructure Provisioning

All Azure infrastructure is provisioned and managed using **Terraform with the azapi provider**. Terraform is the single source of truth for all Azure resources.

**What Terraform manages:**
- Resource Groups (per region and environment)
- Virtual Networks, subnets, and network peering
- Network Security Groups and firewall rules
- Virtual Machines (Kafka brokers, ZooKeeper nodes, connect workers)
- Managed disks and storage accounts
- Key Vaults and secrets
- Load balancers and private endpoints
- Monitoring resources (Log Analytics workspaces, diagnostic settings)

**Why azapi over AzureRM:**
- azapi supports **100% of Azure APIs** (GA, preview, and private) without waiting for provider updates
- Lighter-weight and actively maintained by HashiCorp for edge-case resources
- Can coexist with azurerm for data sources where convenient
- Single provider covers all resource types, simplifying dependency management

**Out of scope for Terraform:**
- Azure subscriptions, billing, and tenant-level policies
- Software installation and Kafka configuration (handled by Ansible)
- Pipeline definitions (handled by GitHub Actions)

### Pillar 2: Ansible — Configuration Management and Application Deployment

All software installation and Confluent Kafka configuration is managed using **Ansible playbooks and roles**. Ansible bridges the gap between provisioned infrastructure and running applications.

**What Ansible manages:**
- Operating system preparation (packages, kernel tuning, disk formatting)
- Confluent Platform installation (Kafka brokers, ZooKeeper, Schema Registry, Connect, REST Proxy)
- Kafka cluster configuration (broker properties, replication settings, security)
- Multi-region replication configuration (MRC, observer replicas, replica placement)
- TLS certificate deployment and SASL/SCRAM credential management
- Monitoring agent installation (Prometheus JMX exporter, node exporter)
- Rolling upgrades and configuration changes with zero downtime
- Health checks and post-deployment validation

**Why Ansible:**
- **Agentless architecture** — uses SSH; no client software needed on target VMs
- **Idempotent playbooks** — safe to run repeatedly without side effects
- **YAML simplicity** — human-readable, easy to review in PRs
- **Dual purpose** — handles both OS-level preparation and application-level configuration
- **Excellent for orchestration** — rolling restarts, canary deployments, multi-tier coordination
- **Confluent ecosystem** — Confluent provides official Ansible roles (cp-ansible) as a starting point

**Out of scope for Ansible:**
- Azure resource provisioning (handled by Terraform)
- Pipeline orchestration (handled by GitHub Actions)

### Pillar 3: GitHub Actions — CI/CD Automation

All deployment automation, validation, and approval workflows are orchestrated through **GitHub Actions**. GitHub Actions is the single CI/CD platform for infrastructure and application deployments.

**What GitHub Actions manages:**
- Terraform validation (`fmt`, `validate`, `plan`) on pull requests
- Ansible linting (`ansible-lint`, `--syntax-check`) on pull requests
- Manual approval gates for production deployments
- Terraform `apply` execution with proper Azure credentials
- Ansible playbook execution against target environments
- Post-deployment health checks and smoke tests
- Rollback orchestration on deployment failure
- Scheduled drift detection (`terraform plan` audits)
- Notification and alerting on deployment status

**Why GitHub Actions:**
- **Native GitHub integration** — repository-native; no external CI/CD platform needed
- **Workflow-as-code** — YAML definitions versioned alongside infrastructure and application code
- **Environment protection rules** — built-in approval gates, deployment reviews, and secret scoping
- **Reusable workflows** — shared workflow definitions reduce duplication across environments
- **Matrix strategies** — parallel execution across regions and environments
- **Azure integration** — first-class `azure/login` action and OIDC federation support
- **Cost** — free for public repos; generous free tier for private repos

## Rationale

**Why a three-tool approach over a single tool:**

Research (task-2.11) concluded that no single tool excels at all three concerns. Terraform is best-in-class for infrastructure state management but poor at application configuration. Ansible is best-in-class for configuration management but lacks explicit state tracking for infrastructure. GitHub Actions provides native CI/CD orchestration that neither Terraform nor Ansible provides.

**Alternatives considered:**
- **ARM templates + PowerShell DSC**: Azure-native but verbose, Azure-locked, and limited community
- **Azure CLI scripts**: Imperative, no state tracking, fragile for multi-region deployments
- **Terraform alone (with provisioners)**: Terraform provisioners are discouraged by HashiCorp; poor fit for ongoing configuration management
- **Ansible alone (with azure modules)**: Azure modules lag behind native APIs; no explicit infrastructure state management
- **Azure DevOps Pipelines**: Viable but adds platform dependency outside GitHub; team already uses GitHub

## Implementation Notes

### Repository structure

```
terraform/
├── main.tf                     # Provider config (azapi)
├── variables.tf                # Common variables (customer prefix, regions, environments)
├── outputs.tf                  # Shared outputs (VM IPs, resource IDs for Ansible)
├── versions.tf                 # Provider version constraints
├── terraform.tfvars            # Shared values (customer prefix klc)
├── modules/
│   ├── resource-group/         # Resource group module
│   ├── vnet/                   # Virtual network + subnets + peering
│   ├── nsg/                    # Network security groups
│   ├── vm/                     # Virtual machine module (Kafka, ZK, Connect)
│   ├── storage/                # Storage account + managed disks
│   ├── keyvault/               # Key Vault + secrets
│   ├── load-balancer/          # Internal load balancers
│   └── monitoring/             # Log Analytics + diagnostic settings
├── environments/
│   ├── prod/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf          # Remote state config
│   ├── dev/
│   └── qa/
└── backend/                    # Bootstrap: storage account for remote state

ansible/
├── roles/
│   ├── common/                 # OS prep, packages, kernel tuning
│   ├── kafka-broker/           # Confluent Kafka broker installation + config
│   ├── zookeeper/              # ZooKeeper ensemble installation + config
│   ├── schema-registry/        # Schema Registry deployment
│   ├── kafka-connect/          # Kafka Connect workers
│   ├── control-center/         # Confluent Control Center
│   ├── tls-certs/              # TLS certificate deployment
│   └── monitoring/             # Prometheus exporters, node exporter
├── playbooks/
│   ├── site.yml                # Full deployment (all roles)
│   ├── deploy-brokers.yml      # Broker-only deployment
│   ├── rolling-upgrade.yml     # Zero-downtime upgrade
│   ├── configure-mrc.yml       # Multi-region replication setup
│   └── health-check.yml        # Post-deployment validation
├── inventory/
│   ├── dev/
│   ├── qa/
│   └── prod/
├── group_vars/
│   ├── all.yml                 # Common variables
│   ├── kafka_brokers.yml       # Broker-specific config
│   └── zookeeper.yml           # ZooKeeper-specific config
└── ansible.cfg

.github/
└── workflows/
    ├── terraform-validate.yml  # PR validation: fmt, validate, plan
    ├── terraform-apply.yml     # Merge to main: apply infrastructure
    ├── ansible-lint.yml        # PR validation: lint and syntax check
    ├── deploy-kafka.yml        # Full Kafka deployment pipeline
    ├── rolling-upgrade.yml     # Zero-downtime upgrade pipeline
    └── drift-detection.yml     # Scheduled: terraform plan audit
```

### Terraform azapi provider configuration

```hcl
terraform {
  required_providers {
    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "klc-tfstate-prod-scus"
    storage_account_name = "klctfstateprodscus"
    container_name       = "tfstate"
    key                  = "kafka-lab.tfstate"
  }
}

provider "azapi" {
  subscription_id = var.azure_subscription_id
}
```

### Naming convention integration (decision-0008)

```hcl
resource "azapi_resource" "vm_broker" {
  name      = "${var.customer_prefix}-kafka-${var.environment}-${var.region}-${count.index + 1}"
  # Example: klc-kafka-prod-mexc-1
  type      = "Microsoft.Compute/virtualMachines@2024-07-01"
  location  = var.azure_region
  parent_id = azapi_resource.resource_group.id
  # ...
}
```

### Multi-region module strategy

```hcl
locals {
  regions = {
    primary   = { name = "mexicocentral",  prefix = "mexc" }
    secondary = { name = "southcentralus", prefix = "scus" }
    dr        = { name = "canadaeast",     prefix = "cane" }
  }
}

module "region" {
  for_each      = local.regions
  source        = "./modules/region"
  region_name   = each.value.name
  region_prefix = each.value.prefix
  environment   = var.environment
  # ...
}
```

### Ansible dynamic inventory from Terraform

Terraform outputs VM connection details consumed by Ansible:
```hcl
output "ansible_inventory" {
  value = {
    kafka_brokers = [for vm in azapi_resource.kafka_broker : {
      hostname   = vm.name
      private_ip = vm.output.properties.networkProfile.networkInterfaces[0].properties.ipConfigurations[0].properties.privateIPAddress
      region     = vm.location
    }]
  }
}
```

Ansible inventory script reads Terraform output:
```yaml
# inventory/prod/hosts.yml (generated from terraform output)
all:
  children:
    kafka_brokers:
      hosts:
        klc-kafka-prod-mexc-1:
          ansible_host: 10.1.1.4
          kafka_broker_id: 1
          kafka_rack: mexc
        klc-kafka-prod-scus-1:
          ansible_host: 10.2.1.4
          kafka_broker_id: 2
          kafka_rack: scus
```

### GitHub Actions deployment pipeline

```yaml
name: Deploy Kafka Infrastructure and Platform

on:
  push:
    branches: [main]
    paths: [terraform/**, ansible/**]
  pull_request:
    branches: [main]

jobs:
  # --- Validation (runs on every PR) ---
  validate-terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform fmt -check -recursive
      - run: terraform init -backend=false
      - run: terraform validate
      - name: Terraform Plan
        run: terraform plan -out=plan.tfplan
        env:
          ARM_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  validate-ansible:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ansible ansible-lint
      - run: ansible-lint ansible/playbooks/
      - run: ansible-playbook --syntax-check ansible/playbooks/site.yml

  # --- Infrastructure Deployment (main branch only) ---
  deploy-infrastructure:
    needs: [validate-terraform, validate-ansible]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production    # Requires manual approval
    strategy:
      matrix:
        region: [mexc, scus, cane]
      max-parallel: 1          # Deploy regions sequentially for safety
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: terraform init
      - run: terraform apply -auto-approve -var="target_region=${{ matrix.region }}"

  # --- Application Deployment (after infrastructure) ---
  deploy-kafka:
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: pip install ansible
      - name: Generate inventory from Terraform
        run: terraform output -json ansible_inventory > ansible/inventory/prod/terraform.json
      - name: Deploy Kafka Platform
        run: ansible-playbook -i ansible/inventory/prod ansible/playbooks/site.yml
        env:
          ANSIBLE_HOST_KEY_CHECKING: "false"

  # --- Post-deployment validation ---
  health-check:
    needs: deploy-kafka
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ansible
      - name: Run Health Checks
        run: ansible-playbook -i ansible/inventory/prod ansible/playbooks/health-check.yml
```

### Scheduled drift detection

```yaml
name: Infrastructure Drift Detection

on:
  schedule:
    - cron: '0 6 * * 1-5'    # Weekdays at 6 AM UTC

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Check for drift
        id: plan
        run: |
          terraform init
          terraform plan -detailed-exitcode -out=drift.tfplan 2>&1 | tee plan-output.txt
        continue-on-error: true
      - name: Notify on drift
        if: steps.plan.outputs.exitcode == '2'
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "⚠️ Infrastructure drift detected in kafka-lab. Review: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}
```

### Terraform state management

- **Remote state**: Azure Storage blobs with versioning enabled
- **Locking**: Azure blob leases prevent concurrent modifications
- **Backup**: Storage account replication (GRS) and point-in-time restore
- **Access control**: RBAC-restricted storage account; only CI/CD service principal has write access
- **State per environment**: Separate state files for dev, qa, and prod

### Secrets and credentials

- **Azure authentication**: OIDC federation between GitHub Actions and Azure AD (no stored secrets)
- **Kafka credentials**: Stored in Azure Key Vault; referenced by Terraform and Ansible
- **SSH keys**: Managed via Azure Key Vault; Ansible uses key-based authentication
- **Service principal**: Scoped to minimum required RBAC roles per environment
- **Never commit secrets** to version control

### Deployment workflow integration

The three tools form a sequential pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Orchestrator)             │
│                                                             │
│  PR Opened ──► Validate Terraform ──► Validate Ansible      │
│                                                             │
│  Merge to Main ──► Approval Gate ──► Deploy Infrastructure  │
│                          │                                  │
│                          ▼                                  │
│              Terraform Apply (azapi)                        │
│              ├── Resource Groups                            │
│              ├── VNets + Peering                            │
│              ├── VMs + Disks                                │
│              ├── Key Vault + NSGs                           │
│              └── Output: VM IPs, Resource IDs               │
│                          │                                  │
│                          ▼                                  │
│              Ansible Playbooks                              │
│              ├── OS Preparation                             │
│              ├── Confluent Installation                     │
│              ├── Cluster Configuration                      │
│              ├── MRC Replication Setup                      │
│              └── Health Checks                              │
│                          │                                  │
│                          ▼                                  │
│              Post-Deployment Validation                     │
│              ├── Broker connectivity                        │
│              ├── Topic replication                          │
│              └── Monitoring active                          │
└─────────────────────────────────────────────────────────────┘
```

## Consequences

### What changes

- **Deployment workflow**: All Azure resources via Terraform; all Kafka config via Ansible; all automation via GitHub Actions
- **Change management**: Every change requires a PR with automated validation before merge
- **Separation of concerns**: Infrastructure, configuration, and automation are independently versioned and maintained
- **Version control**: Full git history for infrastructure, application config, and pipeline definitions

### Benefits

- **Repeatability**: Identical infrastructure and configuration across all regions and environments
- **Auditability**: Full git history and GitHub Actions logs for every deployment
- **Disaster recovery**: Terraform + Ansible can rebuild entire stack from code
- **Zero-downtime operations**: Ansible rolling upgrade playbooks for Kafka maintenance
- **Cost tracking**: Resource names follow decision-0008 convention for billing analysis
- **Governance**: PR review gates, environment protection rules, and approval workflows

### Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Terraform state corruption | Azure Storage GRS replication; blob versioning; point-in-time restore |
| Accidental resource deletion | `prevent_destroy` lifecycle rules; environment protection in GitHub Actions |
| Ansible playbook failures mid-run | Idempotent plays; rolling strategy with serial limits; automatic rollback workflows |
| Credential exposure | OIDC federation (no stored secrets); Key Vault references; RBAC least-privilege |
| Drift from declared state | Scheduled drift detection workflow; GitOps enforcement (code is source of truth) |
| Tool version incompatibility | Pin all tool versions (azapi, Ansible, GitHub Actions); test upgrades in dev first |
| Pipeline failures blocking deployments | Manual override procedures documented in runbooks; break-glass access for emergencies |

### Affected areas

- **Infrastructure team**: Owns Terraform modules and state management
- **Platform team**: Owns Ansible roles and Kafka configuration
- **DevOps team**: Owns GitHub Actions workflows and pipeline maintenance
- **Security team**: Reviews OIDC federation, Key Vault access, and RBAC policies
- **All engineers**: Must follow PR-based workflow for any infrastructure or configuration change

## Notes

This decision establishes the canonical DevOps deployment strategy for the kafka-lab project. The three-pillar approach (Terraform azapi + Ansible + GitHub Actions) provides clear separation of concerns while maintaining a unified, automated deployment pipeline. All infrastructure and configuration changes must flow through this workflow to maintain consistency and auditability.

This decision supersedes any earlier interpretation of decision-0009 that was scoped only to Terraform. The expanded scope now covers the full DevOps lifecycle.
