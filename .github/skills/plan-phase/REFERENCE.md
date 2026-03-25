# Plan Phase — Reference

Detailed phase definitions, task breakdowns, decision mappings, and research cross-references for the Confluent Kafka on Azure implementation roadmap.

## Roadmap Decisions (Grill-Me Session Outputs)

These 25 decisions were made during roadmap planning and govern all phases:

| # | Decision | Choice |
|---|----------|--------|
| 1 | Approach | Lab-first, single-region, then scale up |
| 2 | Initial region | South Central US (scus) |
| 3 | Lab VM SKU | Standard_D4s_v5 (4 vCPU, 16GB) |
| 4 | Broker count (lab) | 3 brokers |
| 5 | Metadata management | ZooKeeper (proven, matches research) |
| 6 | ZK nodes (lab) | 1 node (minimal cost, validates deployment) |
| 7 | IaC toolchain | Terraform + Ansible |
| 8 | Terraform state | Azure Storage Account with blob locking |
| 9 | Lab Phase 1 components | Brokers + ZK + Control Center |
| 10 | Network topology | Full production topology (multi-subnet, bastion) |
| 11 | Access method | Azure Bastion + jumpbox VM |
| 12 | Security | Full TLS + SASL/SCRAM from day one |
| 13 | Certificate management | Azure Key Vault + self-signed CA |
| 14 | Monitoring | Full stack: JMX Exporter + Prometheus + Grafana + Log Analytics |
| 15 | Phase count | 4 phases |
| 16 | CI/CD timing | From Phase 1 — all infra changes through pipelines |
| 17 | Azure subscription | Already set up |
| 18 | Terraform structure | Multi-root with shared modules |
| 19 | Ansible approach | Confluent cp-ansible + custom extension roles |
| 20 | Cluster validation | Python producer/consumer test scripts |
| 21 | Cost management | Daily Terraform destroy/apply |
| 22 | Data persistence | Ephemeral — topics recreated via automation |
| 23 | Repo structure | Structured infra/terraform + infra/ansible + tests/ |
| 24 | Pipeline workflow | PR plan + merge apply with manual approval gates |
| 25 | Confluent license | 30-day developer trial (time-boxed constraint) |

## Repository Structure

All implementation work follows this directory layout:

```
kafka-lab-copilot/
├── infra/
│   ├── terraform/
│   │   ├── modules/          # Shared reusable modules
│   │   ├── state-backend/    # Storage account for TF state (bootstrap)
│   │   ├── network/          # VNet, subnets, NSGs, Bastion, peering
│   │   ├── compute/          # VMs, disks, availability sets
│   │   ├── security/         # Key Vault, certs, managed identities
│   │   └── monitoring/       # Log Analytics, Prometheus VM, Grafana
│   └── ansible/
│       ├── inventory/        # Host inventories (generated from TF output)
│       ├── playbooks/        # Orchestration playbooks
│       └── roles/            # Custom roles extending cp-ansible
├── .github/
│   └── workflows/            # GitHub Actions CI/CD pipelines
├── tests/
│   ├── producer/             # Python Kafka producer test scripts
│   └── consumer/             # Python Kafka consumer test scripts
└── backlog/
    └── docs/                 # Spike retrospectives, research, architecture guide
```

---

## Phase 1: Foundation — Azure Infrastructure + CI/CD Pipeline

### Goal

Provision all Azure infrastructure and establish CI/CD pipeline. No Kafka software yet.

### Constraint

30-day Confluent trial starts when Phase 2 begins — complete Phase 1 fully before activating the trial.

### Prior-Phase Debt

None (first phase).

### Implementation Tasks

#### Bootstrap Terraform State Backend
- Create Azure Storage Account + blob container for Terraform state
- Configure state locking via Azure Blob lease
- This is the one manual `terraform apply` (chicken-and-egg for bootstrapping)
- **Output:** `infra/terraform/state-backend/`
- **ADRs:** decision-0008 (naming convention)
- **Research:** research-task-2.11 (IaC provisioning)

#### GitHub Actions CI/CD Pipeline
- Create workflow: PR triggers `terraform validate` + `terraform plan`
- Plan output posted as PR comment
- Merge to `main` triggers `terraform apply` with GitHub Environment manual approval gate
- Configure service principal credentials as GitHub Secrets
- Add Ansible execution step (post-TF apply) with separate approval gate
- Branch protection rules: require PR review + passing plan
- **Output:** `.github/workflows/infra-plan.yml`, `.github/workflows/infra-apply.yml`
- **ADRs:** decision-0009 (DevOps deployments)
- **Research:** research-task-2.11 (IaC provisioning)

#### Terraform Shared Modules
- `modules/vm` — standard VM creation with tags, disks, managed identity
- `modules/nsg-rules` — reusable NSG rule definitions for Kafka ports
- `modules/key-vault-cert` — certificate generation and Key Vault storage
- **Output:** `infra/terraform/modules/`
- **ADRs:** decision-0008 (naming convention), decision-0011 (VM SKU)
- **Research:** research-task-2.4 (VM sizing), research-task-2.11 (IaC)

#### Network Infrastructure
- VNet in SCUS region (address space planning for future multi-region peering)
- Subnets: broker, zookeeper, management/control-center, monitoring, bastion
- NSGs per subnet with explicit allow rules (Kafka: 9092/9093, ZK: 2181, CC: 9021, JMX: 9999, Prometheus: 9090, Grafana: 3000)
- No public IPs on any resource
- Azure Bastion subnet + Bastion host
- **Output:** `infra/terraform/network/`
- **ADRs:** decision-0007 (regional strategy), decision-0010 (no public endpoints), decision-0013 (resource group architecture)
- **Research:** research-task-2.5 (Azure networking)

#### Security Infrastructure
- Azure Key Vault in SCUS region
- Self-signed CA certificate generation (stored in Key Vault)
- Broker certificates (one per broker, SANs for hostnames)
- ZooKeeper certificate
- Control Center certificate
- SCRAM credential secrets stored in Key Vault
- Managed identity for VMs to access Key Vault
- **Output:** `infra/terraform/security/`
- **ADRs:** decision-0010 (no public endpoints)
- **Research:** research-task-2.7 (Kafka security)

#### Compute Infrastructure
- 3× Standard_D4s_v5 VMs for Kafka brokers (spread across availability zones)
- 1× Standard_D4s_v5 VM for ZooKeeper
- 1× Standard_D2s_v5 VM for jumpbox (management)
- 1× Standard_D4s_v5 VM for Control Center
- 1× Standard_D4s_v5 VM for monitoring (Prometheus + Grafana)
- Premium SSD managed disks for broker log dirs
- All VMs tagged for identification (`environment=lab`, `component=kafka|zk|cc|monitoring|jumpbox`)
- **Output:** `infra/terraform/compute/`
- **ADRs:** decision-0008 (naming), decision-0011 (VM SKU), decision-0013 (resource groups)
- **Research:** research-task-2.4 (VM sizing/storage), research-task-2.3 (Azure regions/AZs)

#### Monitoring Infrastructure
- Azure Log Analytics workspace in SCUS
- Azure Monitor agent configuration for all VMs
- Prometheus VM provisioning (software installed in Phase 2 via Ansible)
- Grafana VM provisioning (software installed in Phase 2 via Ansible)
- **Output:** `infra/terraform/monitoring/`
- **ADRs:** decision-0012 (centralized Log Analytics)
- **Research:** research-task-2.8 (monitoring/observability)

#### Ansible Inventory Generation
- Terraform outputs VM IPs, hostnames, Key Vault URIs
- Script or Terraform `local_file` to generate Ansible inventory from TF output
- Inventory includes host vars (broker IDs, ZK IDs, cert paths)
- **Output:** `infra/ansible/inventory/`
- **Research:** research-task-2.11 (IaC provisioning)

### Testing Tasks

#### Terraform Validation Suite
- `terraform validate` passes for all root modules
- `terraform plan` produces clean plan with no errors
- Idempotency test: `apply` → `plan` shows no changes
- Destroy/recreate cycle: `destroy` → `apply` produces identical infrastructure
- Validate all NSG rules allow expected ports and deny everything else
- Validate Key Vault contains expected certificates and secrets
- Validate Bastion connectivity: SSH to jumpbox, then to all private VMs
- Validate Log Analytics workspace receives VM heartbeat metrics

### Acceptance Criteria (Phase-Level)

- `terraform plan` runs clean with zero errors from GitHub Actions
- `terraform apply` creates all resources in SCUS
- Azure Bastion provides SSH access to jumpbox
- From jumpbox, can SSH to all broker/ZK/CC/monitoring VMs
- Key Vault contains CA cert, broker certs, and SCRAM credentials
- Log Analytics workspace receives VM-level metrics
- `terraform destroy` cleanly removes all resources
- `terraform apply` after destroy recreates identical environment (idempotency)
- GitHub Actions pipeline works end-to-end (PR plan → approval → apply)

---

## Phase 2: Core Cluster — Confluent Kafka Deployment

### Goal

Deploy and configure a working 3-broker Kafka cluster with full security, monitoring, and Control Center.

### Constraint

30-day Confluent trial clock starts now. Target Phase 2 completion within 10 days.

### Prior-Phase Debt

Review `backlog/docs/spike-phase-1.md` and incorporate remediations.

### Implementation Tasks

#### Ansible Base Configuration
- Install and configure Confluent cp-ansible collection
- Create host group mappings: `kafka_broker`, `zookeeper`, `control_center`
- Configure cp-ansible variables for TLS + SASL/SCRAM
- Custom role: `azure-keyvault-certs` — pull certs from Key Vault to VMs
- Custom role: `jmx-exporter` — deploy JMX Exporter on broker/ZK VMs
- **Output:** `infra/ansible/playbooks/`, `infra/ansible/roles/`
- **ADRs:** decision-0006 (Confluent Enterprise)
- **Research:** research-task-2.1 (Confluent editions), research-task-2.11 (IaC)

#### ZooKeeper Deployment
- Deploy ZooKeeper on 1 VM via cp-ansible
- Configure TLS for client connections
- Configure SASL authentication
- Verify ZK is healthy: `ruok` → `imok`
- **Output:** Running ZooKeeper instance
- **Research:** research-task-2.10 (ZooKeeper ensemble design)

#### Kafka Broker Deployment
- Deploy 3 Kafka brokers via cp-ansible
- Configure broker properties:
  - `listeners=SASL_SSL://:9093`
  - `security.inter.broker.protocol=SASL_SSL`
  - `ssl.keystore.*` and `ssl.truststore.*` from Key Vault certs
  - `sasl.mechanism.inter.broker.protocol=SCRAM-SHA-256`
  - `default.replication.factor=3`
  - `min.insync.replicas=2`
  - `num.partitions=6` (2 per broker for lab)
  - Broker IDs: 1, 2, 3
- Verify: brokers register with ZK, ISR is healthy
- **Output:** Running 3-broker cluster
- **ADRs:** decision-0006 (Confluent Enterprise), decision-0010 (no public endpoints)
- **Research:** research-task-2.1 (editions), research-task-2.6 (MRC config), research-task-2.7 (security)

#### Control Center Deployment
- Deploy Confluent Control Center via cp-ansible
- Configure HTTPS access (TLS cert from Key Vault)
- Configure SASL authentication to connect to brokers
- Accessible from jumpbox via browser (SSH tunnel or port forward through Bastion)
- Verify: Control Center UI shows 3 healthy brokers
- **Output:** Running Control Center
- **ADRs:** decision-0006 (Confluent Enterprise)
- **Research:** research-task-2.1 (editions/licensing)

#### Monitoring Stack Deployment
- Deploy JMX Exporter on all broker + ZK VMs (Ansible role)
- Deploy Prometheus on monitoring VM:
  - Scrape targets: broker JMX exporters, ZK JMX exporter
  - Retention: 7 days (lab)
- Deploy Grafana on monitoring VM:
  - Confluent Kafka dashboard (pre-built)
  - Data source: Prometheus
  - Accessible from jumpbox
- Configure Azure Monitor agent on all VMs → Log Analytics
- Verify: Grafana shows broker metrics, Log Analytics receives logs
- **Output:** Full monitoring stack operational
- **ADRs:** decision-0012 (centralized Log Analytics)
- **Research:** research-task-2.8 (monitoring/observability/DR)

#### Topic Provisioning Automation
- Ansible playbook or script to create standard test topics:
  - `test-topic-1`: 6 partitions, RF=3, min.insync.replicas=2
  - `test-topic-2`: 3 partitions, RF=3, min.insync.replicas=2
- Idempotent — safe to run on every deployment
- **Output:** `infra/ansible/playbooks/provision-topics.yml`
- **Research:** research-task-2.6 (MRC configuration/replication)

#### Python Test Producer/Consumer
- Producer script:
  - Connects via SASL_SSL
  - Produces timestamped JSON messages to `test-topic-1`
  - Configurable throughput (messages/sec)
  - Logs produce latency and delivery confirmations
- Consumer script:
  - Connects via SASL_SSL
  - Consumes from `test-topic-1`
  - Validates message ordering within partitions
  - Logs end-to-end latency (produce timestamp → consume timestamp)
- Both scripts use `confluent-kafka` Python client
- **Output:** `tests/producer/`, `tests/consumer/`
- **Research:** research-task-2.12 (multi-region producer client patterns)

### Testing Tasks

#### Ansible Playbook Validation
- Ansible syntax check and dry-run (`--check` mode) for all playbooks
- Idempotency test: run playbooks twice, second run makes zero changes
- cp-ansible health checks pass for all components

#### Cluster Functional Tests
- Run producer → verify messages appear in Control Center
- Run consumer → verify all messages consumed in order
- Validate message ordering within partitions
- Validate produce/consume latency is within acceptable range
- Verify SASL_SSL authentication prevents unauthorized access

#### Resilience Tests
- Simulate broker failure (stop 1 broker) → verify cluster remains available with 2 brokers
- Verify monitoring: Grafana shows under-replicated partitions during broker failure
- Verify recovery: restart broker → ISR returns to full replication
- Daily destroy/apply cycle test: full environment torn down and rebuilt cleanly

### Acceptance Criteria (Phase-Level)

- 3 brokers + 1 ZK + Control Center running with TLS + SASL/SCRAM
- All inter-broker communication encrypted (SASL_SSL)
- Control Center accessible and showing healthy cluster
- Prometheus scraping all JMX metrics; Grafana dashboards operational
- Log Analytics receiving VM and application logs
- Python producer/consumer successfully send/receive messages over SASL_SSL
- Cluster survives single broker failure (RF=3, min.insync=2)
- Full destroy/apply cycle completes successfully with automated topic provisioning
- All automation (Terraform + Ansible) runs through GitHub Actions pipeline

---

## Phase 3: Multi-Region — Expand to Active-Active

### Goal

Add a second region and configure Confluent Multi-Region Clusters (MRC) with observer replicas.

### Constraint

Requires Phase 2 cluster operational. Confluent trial must still be active.

### Prior-Phase Debt

Review `backlog/docs/spike-phase-2.md` and incorporate remediations.

### Implementation Tasks

#### Second Region Infrastructure
- Replicate Phase 1 network/compute/security in Mexico Central (mexc)
- Reuse Terraform shared modules from Phase 1 (parameterized for region)
- VNet peering between SCUS and MEXC (global peering)
- Cross-region NSG rules for Kafka replication traffic (ports 9093, 2181)
- Key Vault in MEXC with broker certs for that region
- 3 brokers + 1 ZK node in MEXC
- **Output:** `infra/terraform/network/`, `infra/terraform/compute/`, `infra/terraform/security/` (MEXC additions)
- **ADRs:** decision-0007 (regional strategy), decision-0008 (naming), decision-0010 (no public endpoints), decision-0013 (resource groups)
- **Research:** research-task-2.3 (Azure regions/AZs), research-task-2.5 (Azure networking)

#### ZooKeeper Multi-Node Ensemble
- Expand from 1 ZK node to 3 ZK nodes (2 in SCUS, 1 in MEXC) for proper quorum
- Update cp-ansible inventory for multi-node ZK ensemble
- Configure ZK cross-region communication with TLS
- Verify quorum: `stat` command shows leader + followers
- **Output:** 3-node ZK ensemble operational
- **Research:** research-task-2.10 (ZooKeeper ensemble design)

#### MRC Broker Configuration
- Configure replica placement constraints:
  - SCUS brokers: `broker.rack=scus`
  - MEXC brokers: `broker.rack=mexc`
- Configure observer replicas in MEXC region
- Topic configuration: `confluent.placement.constraints` for multi-region replication
- Verify: observers in MEXC asynchronously replicate from SCUS leaders
- **Output:** MRC-enabled 6-broker cluster
- **ADRs:** decision-0007 (regional strategy)
- **Research:** research-task-2.2 (multi-region patterns), research-task-2.6 (Confluent MRC)

#### Cross-Region Monitoring
- Prometheus federation or centralized Prometheus scraping cross-region targets
- Grafana dashboards for cross-region replication lag
- Log Analytics receiving logs from both regions (already centralized per ADR-0012)
- Alerts: cross-region replication latency > threshold, observer lag > threshold
- **Output:** Updated Grafana dashboards and Prometheus config
- **ADRs:** decision-0012 (centralized Log Analytics)
- **Research:** research-task-2.8 (monitoring/observability/DR)

### Testing Tasks

#### Cross-Region Connectivity Tests
- Verify VNet peering is operational (ping/SSH between regions)
- Verify NSG rules allow replication traffic and block everything else
- Verify ZK ensemble quorum across regions
- Verify all 6 brokers visible in Control Center

#### MRC Replication Tests
- Producer in SCUS → consumer in MEXC (via observer replicas)
- Measure cross-region replication latency (document actual vs. expected)
- Verify observer replicas are receiving data asynchronously
- Verify `confluent.placement.constraints` are enforced

#### Multi-Region Resilience Tests
- Simulate SCUS broker failure → verify SCUS cluster continues with 2 brokers
- Simulate full SCUS region failure → verify MEXC observers can be promoted to leaders
- Validate failover time (actual RTO vs. architecture guide targets)
- Validate recovery: SCUS comes back → re-joins cluster, ISR catches up
- Update DR runbooks with actual observed metrics

### Acceptance Criteria (Phase-Level)

- 6 brokers total (3 SCUS + 3 MEXC) operating as single MRC cluster
- ZooKeeper ensemble with proper quorum across regions
- Observer replicas in MEXC receiving data from SCUS leaders
- Cross-region replication latency measured and documented
- Region failover tested and recovery procedures validated
- Monitoring covers both regions with cross-region alerting
- VNet peering operational with appropriate NSG rules

---

## Phase 4: Production Hardening

### Goal

Add remaining Confluent components, production operational procedures, and prepare for handoff.

### Constraint

Final phase before production readiness assessment. All technical debt from prior phases must be audited.

### Prior-Phase Debt

Review `backlog/docs/spike-phase-3.md` and incorporate remediations. Additionally, audit `spike-phase-1.md` and `spike-phase-2.md` for any deferred items that remain unresolved.

### Implementation Tasks

#### Schema Registry Deployment
- Deploy Schema Registry via cp-ansible (SCUS primary, MEXC secondary)
- Configure Avro/JSON schema validation
- Update Python test scripts to use schemas
- **Output:** Running Schema Registry (multi-region)
- **ADRs:** decision-0006 (Confluent Enterprise)
- **Research:** research-task-2.1 (editions), research-task-2.6 (MRC config)

#### Kafka Connect Deployment
- Deploy Kafka Connect workers via cp-ansible
- Configure at least one reference connector (e.g., Azure Blob Storage sink)
- **Output:** Running Kafka Connect cluster with reference connector
- **ADRs:** decision-0006 (Confluent Enterprise)
- **Research:** research-task-2.1 (editions)

#### DR Region (Canada East)
- Add warm standby region per ADR-0007
- Deploy infrastructure using Phase 1 Terraform modules (parameterized for CANE)
- Cluster Linking from SCUS/MEXC → CANE
- DR failover testing and documentation
- **Output:** CANE region with Cluster Linking operational
- **ADRs:** decision-0007 (regional strategy), decision-0013 (resource groups)
- **Research:** research-task-2.2 (multi-region patterns), research-task-2.8 (DR)

#### Backup Automation
- Cluster metadata backup to Azure Blob Storage
- Topic configuration snapshots
- Automated backup schedule (Azure Automation or cron)
- **Output:** Backup scripts and schedule
- **Research:** research-task-2.8 (monitoring/observability/DR)

#### Production VM Sizing
- Upgrade Terraform variables to production SKUs (Standard_D16s_v5)
- Update disk configuration for production workloads (RAID 10, Premium SSD P60)
- Capacity testing with realistic message volumes
- **Output:** Updated Terraform variables, capacity test results
- **ADRs:** decision-0011 (VM SKU)
- **Research:** research-task-2.4 (VM sizing/storage)

#### Security Hardening
- Replace self-signed CA with enterprise CA (if available)
- Kafka ACLs: per-topic producer/consumer permissions
- Network security audit of all NSG rules across all regions
- Azure Policy compliance validation
- **Output:** Updated security config, audit report
- **ADRs:** decision-0010 (no public endpoints)
- **Research:** research-task-2.7 (security/auth/authz)

### Testing Tasks

#### Component Integration Tests
- Schema Registry: register schema, produce with schema, consume and validate
- Kafka Connect: verify reference connector writes to Azure Blob Storage
- DR: verify Cluster Linking replicates topics to CANE

#### Production Readiness Tests
- Capacity test: sustained throughput at production message volumes
- Latency test: end-to-end produce-to-consume latency under load
- DR failover test: simulate primary region failure, promote CANE, verify RTO/RPO
- Backup/restore test: restore cluster metadata from backup
- Security test: verify ACLs enforce expected permissions, unauthorized access denied

#### Technical Debt Audit
- Review all spike retrospectives (phases 1–3)
- Verify all deferred remediations have been addressed or formally accepted
- Document any remaining debt with justification

### Acceptance Criteria (Phase-Level)

- Schema Registry operational with schema validation
- Kafka Connect deployed with reference connector
- DR region (CANE) operational with Cluster Linking
- Automated backups running on schedule
- Production VM sizing validated under load
- All operational runbooks complete and tested
- Security audit passed
- All prior-phase technical debt audited and resolved or formally accepted

---

## ADR Cross-Reference Index

| ADR | Title | Phases |
|-----|-------|--------|
| decision-0006 | Use Confluent Enterprise for Kafka | 2, 4 |
| decision-0007 | Azure Regional Deployment Strategy | 1, 3, 4 |
| decision-0008 | Standardized Azure Resource Naming Convention | 1, 3 |
| decision-0009 | DevOps Deployments | 1 |
| decision-0010 | No Public Endpoints | 1, 2, 4 |
| decision-0011 | Use Least Expensive VM SKU | 1, 4 |
| decision-0012 | Centralized Log Analytics | 1, 2, 3 |
| decision-0013 | Azure Resource Group Architecture | 1, 3, 4 |

## Research Cross-Reference Index

| Research | Title | Phases |
|----------|-------|--------|
| research-task-2.1 | Confluent Platform editions, licensing | 2, 4 |
| research-task-2.2 | Multi-region architecture patterns | 3, 4 |
| research-task-2.3 | Azure regions and AZ topology | 1, 3 |
| research-task-2.4 | Azure VM sizing and storage | 1, 4 |
| research-task-2.5 | Azure networking architecture | 1, 3 |
| research-task-2.6 | Confluent MRC configuration | 2, 3, 4 |
| research-task-2.7 | Kafka security, auth, authz | 1, 2, 4 |
| research-task-2.8 | Monitoring, observability, DR | 1, 2, 3, 4 |
| research-task-2.10 | ZooKeeper ensemble design | 2, 3 |
| research-task-2.11 | Infrastructure-as-Code provisioning | 1, 2 |
| research-task-2.12 | Multi-region producer client patterns | 2 |

## Architecture Guide

The comprehensive architecture guide is located at:
`backlog/docs/research/ARCHITECTURE-GUIDE-multi-region-confluent-kafka-azure.md`

Reference specific sections when implementing architecture patterns (e.g., "Section 4: Multi-Region Topology" for Phase 3 MRC configuration).
