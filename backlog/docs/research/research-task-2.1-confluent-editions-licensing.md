---
id: research-2.1
title: Confluent Editions and Licensing
type: research
created_date: '2026-03-25 12:36'
updated_date: '2026-03-25 12:36'
---
# Research Document: Confluent Platform Editions, Licensing, and Azure Deployment Models
**Task:** TASK-2.1 - Multi-Region Confluent Kafka Research on Azure  
**Date:** 2024  
**Scope:** Confluent Platform editions, licensing implications, and self-managed vs managed deployment trade-offs for Azure  

---

## Executive Summary

This document evaluates Confluent's three primary deployment models—**Confluent Community Edition** (free, open-source), **Confluent Enterprise** (self-managed, paid subscription), and **Confluent Cloud** (fully managed, consumption-based)—and their applicability to multi-region deployments on Azure. For organizations requiring multi-region high-availability with cluster linking and multi-region cluster (MRC) capabilities, **Confluent Enterprise Edition on self-managed VMs** provides the most control, while **Confluent Cloud on Azure** offers operational simplicity at the cost of infrastructure control. This analysis supports decision-making for the Albertsons Kafka Lab's choice of deployment architecture.

---

## 1. Confluent Platform Editions Overview

### 1.1 Community Edition

**Licensing Model:** Open-source (Apache 2.0 License + Confluent Community License)

**Core Components:**
- Apache Kafka (Apache 2.0)
- Apache ZooKeeper (Apache 2.0)
- Confluent Schema Registry, ksqlDB, REST Proxy, and many connectors (Confluent Community License)
- Open-source connectors from the Confluent Hub

**Cost:** Free to use, modify, and redistribute.

**Restrictions:**
- The Confluent Community License prohibits building a competing SaaS or cloud offering based on these components.
- No commercial support from Confluent.
- No guaranteed SLAs or patches for security vulnerabilities.
- Community support only via forums and GitHub issues.

**Multi-Region Capability:**
- Community Edition supports basic multi-region cluster (MRC) features available in Apache Kafka 2.4+ (follower fetching, observer replicas, offset preservation).
- Does **not** support Cluster Linking, which is a Confluent-only feature.
- Suitable for experimental or non-critical multi-region setups but lacks enterprise monitoring and management tools.

**Use Case:** Development, learning, proof-of-concept deployments, or non-production environments where operational overhead is acceptable.

---

### 1.2 Confluent Enterprise Edition

**Licensing Model:** Paid annual subscription (broker/core-count based)

**Core Components:**
- All Community Edition components
- **Control Center:** Enterprise monitoring UI with role-based access control (RBAC), audit logging, and advanced cluster management
- **Cluster Linking:** Native cross-cluster replication and mirroring for disaster recovery and data sharing
- **Tiered Storage:** Infinite retention by offloading data to object storage (AWS S3, Azure Blob, or GCS)
- **Self-Balancing Clusters:** Automatic partition leadership and replica rebalancing
- **Multi-Tenancy & Security:** Encryption at rest/in-transit, RBAC, audit logs, secret management
- **Schema Validation & Governance:** Schema Registry with centralized governance
- **Advanced Connectors:** Premium connectors for enterprise integrations
- **KRaft Mode (CP 8.0+):** Removal of external ZooKeeper dependency for more scalable, simpler deployments

**Cost Structure:**
- Typically **$25,000 to $500,000+ per year** depending on broker count, throughput, and support level.
- Median enterprise contract: approximately **$100,000 per year** for medium-to-large deployments.
- Volume discounts available for larger organizations.
- Support included: 24/7 enterprise support with guaranteed response times.

**Multi-Region Capability:**
- Full support for Cluster Linking (available from CP 6.0+)
- Advanced MRC features with automatic observer promotion and optimized cross-region replication
- Minimum recommended version for production: **Confluent Platform 7.x** (includes all advanced MRC and DR features)
- Supports both active-passive and active-active multi-region architectures

**License Types:**
- **Production License:** Full feature set for production clusters.
- **Trial License:** 30 days, single broker, for evaluation.
- **Developer License:** Single broker, non-production use; annual renewal available.

**Use Case:** Production deployments requiring high availability, disaster recovery, multi-region replication, enterprise security/compliance, and commercial support.

---

### 1.3 Confluent Cloud

**Licensing Model:** Fully managed, consumption-based (CKUs, data transfer, storage)

**Core Components:**
- Fully managed Apache Kafka (no infrastructure management required)
- Managed Schema Registry, Connectors, ksqlDB, and Flink (stream SQL and data engineering)
- Advanced features: Private Link networking, RBAC, audit logging, API tokens
- Multi-cloud: Available on AWS, Azure, and Google Cloud

**Cost Structure:**
- **Tier-Based Pricing:**
  - **Basic:** Free tier (up to 5 GB storage), best for development
  - **Standard:** ~$1,100/month base (for small clusters), scales with usage
  - **Enterprise:** ~$3,300/month base, includes private endpoints, dedicated support, advanced features
- **Usage Charges:**
  - Compute: Measured in CKUs (Confluent Kafka Units); typically $0.30–$0.50 per CKU-hour
  - Data Storage: Per GB per month (varies by region)
  - Data Transfer: Ingress/egress charges (varies by cloud/region)
- **Total monthly cost:** Highly variable; typical mid-size production cluster: $3,000–$15,000/month

**Multi-Region Capability:**
- Full Cluster Linking support for cross-cluster replication and failover
- Multi-AZ high availability within a region (3+ availability zones by default)
- Serverless scaling: Automatic scaling up/down based on traffic
- Managed disaster recovery and backup

**Support:**
- Confluent-managed: 24/7 operational support, automatic patching, upgrades, and scaling
- SLAs: 99.9% uptime (Standard), 99.99% uptime (Enterprise)

**Azure-Specific Features:**
- Native integration with Azure Active Directory (Entra ID) for SSO
- Unified billing through Azure consumption credits
- Quick provisioning via Azure Portal or ARM templates
- Data residency compliance (data stored in selected Azure region)

**Use Case:** Fast time-to-market, minimal operational overhead, dynamic workloads, organizations prioritizing engineering focus over infrastructure control. Strong fit for Azure-first organizations.

---

## 2. Licensing and Commercial Implications

### 2.1 License Scope and Enforcement

**Community Edition:**
- No license key enforcement; relies on open-source community trust
- Redistributable under the Apache 2.0 and Confluent Community License terms
- SaaS restrictions apply: cannot resell Confluent's software as a competing service

**Enterprise Edition:**
- License key required for production use; enforcement via Control Center
- License validity: Tied to subscription term (typically annual)
- License expiration: Production cluster enters read-only mode upon expiration if renewal is delayed
- Multi-broker licensing: Each broker node requires a license; licensing is capacity-based

**Confluent Cloud:**
- No separate license key; entitlement through Confluent Cloud account
- Billing automatic; usage tracked per cluster/connector/feature
- Cancellation: Immediate cessation of service if account is suspended

### 2.2 Support and SLAs

| Edition         | Support Model          | SLA Guarantee    | Response Time      |
|-----------------|------------------------|------------------|--------------------|
| Community       | Community forums only  | None             | Best effort        |
| Enterprise      | 24/7 enterprise team   | Custom (included)| P1: <1 hour        |
| Cloud (Standard)| Confluent support      | 99.9% uptime     | P1: 4 hours        |
| Cloud (Enterprise) | Dedicated + TAM     | 99.99% uptime    | P1: <1 hour        |

---

## 3. Multi-Region and Multi-AZ Support: Feature Minimum Versions

### 3.1 Confluent Enterprise (Self-Managed) Requirements

**Multi-Region Cluster (MRC) Support:**
- **Minimum Version:** Confluent Platform 5.4+ (includes Apache Kafka 2.4+)
- **Recommended Version for Production:** Confluent Platform 7.x or later
- **Key Features by Version:**
  - **CP 5.4+:** Follower fetching, observer replicas, synchronous and asynchronous replication
  - **CP 6.0+:** Cluster Linking for inter-datacenter replication and failover
  - **CP 7.0+:** Enhanced observer promotion, improved disaster recovery automation
  - **CP 8.0+:** KRaft mode (ZooKeeper removal), simplified architecture, modernized security

**Multi-AZ Support:**
- All versions support rack-aware replica placement and multi-AZ deployment
- Configuration via broker and client rack settings
- Azure Availability Zones: Choose zones (e.g., "eastus-1", "eastus-2", "eastus-3") for rack affinity

**Cluster Linking:**
- **Minimum:** Confluent Platform 6.0
- **Enables:** Cross-cluster topic mirroring, data sharing, and active-active deployments
- **Enterprise Only:** Not available in Community Edition

### 3.2 Confluent Cloud Support

- **Full MRC and Cluster Linking support** across all tiers
- **Multi-AZ:** 3+ availability zones per region (managed automatically)
- **Multi-Region:** Cluster Linking available for cross-region failover and data sync
- **No version constraints:** Features automatically available on all Cloud clusters

---

## 4. Self-Managed vs. Confluent Cloud: Trade-Offs for Azure

### 4.1 Operational Complexity

**Self-Managed (Enterprise on Azure VMs):**
- **Full Responsibility:** Installation, patching, scaling, monitoring, backups, disaster recovery, security hardening
- **Expertise Required:** Dedicated Kafka operations team
- **Tooling:** Manual or Infrastructure-as-Code (IaC) via Terraform, ARM templates, or Ansible
- **Benefit:** Maximum control over configuration, security policies, and integrations

**Confluent Cloud on Azure:**
- **Managed Operations:** Confluent handles provisioning, patching, scaling, monitoring, backups
- **Minimal Overhead:** Teams focus on application logic, not infrastructure
- **Azure Integration:** Native Entra ID SSO, unified billing, ARM template support
- **Trade-off:** Limited access to deep system parameters; less customization

**Winner for Operations:** Confluent Cloud wins for organizations prioritizing agility and reduced ops burden.

### 4.2 Scalability and Elasticity

**Self-Managed:**
- Manual scaling: Provision new VMs, add brokers, rebalance partitions (time-consuming, potential downtime)
- Difficult to respond to traffic spikes; requires pre-provisioning
- Cost-inefficient for variable workloads

**Confluent Cloud:**
- Automatic, on-demand scaling in seconds
- Scale-to-zero for low-traffic periods
- Pay only for what you use
- Ideal for variable or unpredictable workloads

**Winner for Elasticity:** Confluent Cloud wins decisively.

### 4.3 Cost Structure

**Self-Managed on Azure VMs:**
- Direct Infrastructure Costs:
  - VMs (D-series, E-series): ~$100–$500/month per broker
  - Storage (Premium SSD, managed disks): ~$50–$200/month per broker
  - Networking (data transfer, private endpoints): ~$20–$100/month
- **Hidden Costs:**
  - Engineering headcount: $150K–$250K+ annually for dedicated Kafka operations
  - Incident response: Unplanned downtime costs far exceed operational overhead
  - Monitoring/logging (Azure Monitor, Log Analytics): ~$500–$2K/month
- **Total: $25K–$100K+ annually for infrastructure + significant ops overhead**

**Confluent Cloud on Azure:**
- **Usage-Based Billing:**
  - Compute: $0.30–$0.50 per CKU-hour
  - Storage & Transfer: ~$0.02–$0.10 per GB
  - Typical mid-size cluster: $3K–$15K/month
- **Operational Savings:** No dedicated ops team required
- **Predictable:** Usage-based costs scale linearly with throughput
- **Advantage:** No incident-driven cost spikes; SLA-backed stability
- **Total: $36K–$180K annually (lower for typical workloads, higher if heavily used)**

**Cost Verdict:** For light-to-moderate workloads, Confluent Cloud is cost-competitive. For very high throughput (>1GB/s sustained), self-managed may offer cost advantages at the expense of operational burden.

### 4.4 Feature Set and Time-to-Value

**Self-Managed:**
- Access to all Confluent Platform features (with Enterprise license)
- Cluster Linking, Schema Registry, ksqlDB, Tiered Storage all available
- **Caveat:** Each component requires separate configuration and management
- New features available only after cluster upgrade (requires planning and downtime)

**Confluent Cloud:**
- Fully managed suite: Kafka, Schema Registry, ksqlDB, Flink, Connectors all pre-integrated
- **Rapid feature deployment:** New capabilities available immediately, no upgrades needed
- Preferred for organizations wanting latest innovations (streaming Flink, AI/ML integrations)

**Winner for Velocity:** Confluent Cloud wins; reduces time-to-market for new features.

### 4.5 Compliance and Data Sovereignty

**Self-Managed:**
- Complete control over data location, encryption, access patterns
- Easier to satisfy strict regulatory requirements (HIPAA, PCI-DSS, GDPR)
- Can implement air-gapped or on-premises deployments
- Responsibility for compliance validation and auditing

**Confluent Cloud on Azure:**
- Data stored in selected Azure region (compliant with data residency requirements)
- Azure compliance certifications: SOC 2, ISO 27001, PCI-DSS
- Azure native encryption and key management
- Less control; rely on Confluent's and Azure's compliance posture
- Better for organizations already using Azure compliance frameworks

**Verdict:** Self-managed wins for highly regulated or air-gapped environments; Cloud is sufficient for most Azure-integrated organizations.

---

## 5. Azure Marketplace Availability and Bring-Your-Own-License (BYOL)

### 5.1 Confluent Platform on Azure Marketplace

**Availability:**
- Confluent Platform VM images are available on the Azure Marketplace
- Offered with two licensing models: Pay-as-You-Go (PAYG) and Bring-Your-Own-License (BYOL)

**BYOL Model (Recommended for Enterprise Deployments):**
- **Purchase Flow:** Buy Confluent Enterprise license directly from Confluent (not through Azure)
- **Deployment:** Use BYOL VM image from Azure Marketplace; license key applied during setup
- **Billing Separation:**
  - Confluent Software License: Billed by Confluent (annual subscription)
  - Azure Infrastructure: Billed by Azure (VMs, storage, networking)
- **Advantages:**
  - Leverages negotiated enterprise rates
  - Avoid double licensing
  - Clearer cost attribution for CapEx/OpEx budgeting
  - Flexibility to move VMs across subscriptions without re-licensing

**BYOL Cost Breakdown (Example for Mid-Size Deployment):**
- **Confluent Enterprise License:** ~$100K–$150K annually (for 5-10 brokers)
- **Azure Infrastructure:**
  - VMs (5× Standard E8s_v3): ~$15K/year
  - Premium SSD Storage: ~$5K/year
  - Data Transfer (internal): ~$2K/year
  - **Total Infrastructure:** ~$22K/year
- **Annual Total:** ~$122K–$172K

**Pay-As-You-Go (PAYG) Model:**
- Confluent software license included in Azure Marketplace price
- Simpler billing (single Azure invoice) but often more expensive
- Less suitable for committed, large-scale deployments

---

### 5.2 Confluent Cloud on Azure Marketplace

**Availability:**
- Confluent Cloud is available directly through Azure Marketplace
- No separate BYOL option; subscription entirely through Azure consumption
- Unified Azure billing

**Benefits:**
- One invoice (Azure)
- Azure cost management and budgeting tools
- Integration with Azure Reservations (if available for Confluent Cloud)
- Seamless provisioning via Azure Portal

---

## 6. Decision Matrix: When to Choose Which

| Criterion                  | Community | Enterprise (Self) | Cloud       |
|----------------------------|-----------|-------------------|-------------|
| **Cost** (low-throughput)  | ✓✓✓       | ✓                 | ✓✓          |
| **Cost** (high-throughput) | ✓         | ✓✓                | ✓           |
| **Operational Burden**     | ✗         | ✗✗                | ✓✓✓         |
| **Control**                | ✓✓        | ✓✓✓               | ✓           |
| **Multi-Region (MRC)**     | ✓         | ✓✓✓               | ✓✓✓         |
| **Cluster Linking**        | ✗         | ✓✓✓               | ✓✓✓         |
| **Time-to-Market**         | ✗         | ✓                 | ✓✓✓         |
| **Compliance/Sovereignty** | ✓✓        | ✓✓✓               | ✓✓          |

---

## 7. Rationale for Self-Managed VMs on Azure (For Albertsons Kafka Lab)

**Enterprise Edition on self-managed Azure VMs is recommended if:**

1. **Operational Expertise:** The organization has a dedicated Kafka operations team capable of managing cluster lifecycle, upgrades, and disaster recovery.

2. **Feature Control:** Full access to Cluster Linking, schema governance, tiered storage, and advanced monitoring is required.

3. **Cost Sensitivity (High Throughput):** At very high throughput (>500 MB/s sustained), self-managed VMs offer lower per-GB costs than Confluent Cloud.

4. **Compliance Constraints:** Strict regulatory requirements or air-gapped network requirements necessitate complete infrastructure control.

5. **Multi-Region Complexity:** Designing intricate active-active or hub-and-spoke topologies across Azure regions requires full architectural control.

**Recommended Configuration for Albertsons Lab:**
- **Platform:** Confluent Enterprise Edition, CP 7.x or 8.x
- **Infrastructure:** Azure VMs (D-series for compute, Premium SSD for storage)
- **Licensing:** BYOL via Azure Marketplace (cleanest cost attribution)
- **Multi-Region Setup:** Deploy clusters in 2–3 Azure regions with Cluster Linking for active-passive failover or active-active data sync
- **High Availability:** Configure within each region using rack-aware replica placement across 3+ availability zones

---

## 8. Key References

1. **Confluent Platform Documentation:** https://docs.confluent.io/platform/current/
2. **Cluster Linking Guide:** https://docs.confluent.io/platform/current/multi-dc-deployments/cluster-linking/index.html
3. **Multi-Region Clusters Configuration:** https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region.html
4. **License Management:** https://docs.confluent.io/platform/current/installation/license.html
5. **Confluent Community License FAQ:** https://www.confluent.io/confluent-community-license-faq/
6. **Azure Marketplace Integration:** https://learn.microsoft.com/en-us/azure/partner-solutions/apache-kafka-confluent-cloud/overview
7. **Confluent Cloud Pricing:** https://www.confluent.io/confluent-cloud/pricing/

---

## 9. Important Findings for Synthesis Document

### Key Takeaways:

1. **Cluster Linking is Enterprise-Only:** Multi-region data replication with guaranteed offset preservation requires Confluent Enterprise or Cloud; Community Edition cannot replicate topics across regions reliably.

2. **Minimum Version for Production MRC:** Confluent Platform 7.x is recommended for production multi-region deployments; it includes all advanced observer promotion and failover automation.

3. **BYOL on Azure Optimizes Cost:** Using BYOL Enterprise Edition on Azure VMs provides the best balance of control and predictable costs for committed, medium-to-large deployments.

4. **Confluent Cloud Strong Alternative:** If operational overhead is a constraint, Confluent Cloud on Azure offers rapid deployment, automatic scaling, and built-in multi-region failover without infrastructure management.

5. **Cost Crossover Point:** For workloads sustaining >500 MB/s, self-managed typically becomes cost-competitive; below that, Confluent Cloud edges ahead when operational costs are factored in.

---

## 10. Next Steps

1. **Determine preferred deployment model** based on organization's operational capacity and cost sensitivity
2. **If choosing self-managed:** Procure Confluent Enterprise BYOL license; validate Azure infrastructure (compute, networking, storage) sizing
3. **If choosing Cloud:** Evaluate Confluent Cloud cost with expected throughput; provision via Azure Portal for SSO/billing integration
4. **Design multi-region topology:** Map Azure regions, availability zones, and Cluster Linking topology
5. **Plan migration or pilot:** Start with a single region, validate operational processes, then expand to multi-region

---

**Document Author:** Kafka Lab Research Team  
**Last Updated:** 2024  
**Status:** Complete
