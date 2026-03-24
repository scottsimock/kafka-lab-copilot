# Multi-Region Confluent Kafka on Azure: Comprehensive Architecture and Deployment Guide

**Document Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production-Ready  
**Epic:** Multi-Region Confluent Kafka Research on Azure (Epic 2)

---

## Executive Summary

This comprehensive architecture and deployment guide synthesizes research from 11 specialized focus areas to provide a definitive reference for designing, deploying, and operating multi-region Confluent Kafka clusters on Microsoft Azure. This document is intended for architects, platform engineers, and operators responsible for building enterprise-grade event streaming infrastructure.

### Design Goals and Rationale

Multi-region Kafka deployments on Azure address several critical business requirements:

- **High Availability:** Survive zone-level and region-level outages with automated or managed failover
- **Disaster Recovery:** Replicate data across geographically distant regions meeting strict RTO/RPO targets
- **Latency Optimization:** Deploy cluster components near data producers and consumers for sub-millisecond latency
- **Regulatory Compliance:** Meet data residency requirements by controlling replication topology across regions
- **Cost Efficiency:** Balance operational complexity against infrastructure utilization in multi-region deployments

### Key Architectural Decisions

1. **Primary Architecture Pattern:** Confluent Multi-Region Clusters (MRC) with role-based replication (leaders, followers, observers) provides optimal balance of latency, consistency, and operational automation
2. **Compute Foundation:** Standard_D16s_v5 Azure VMs (16 vCPU, 64 GB memory) with RAID 10 Premium SSD storage for high-throughput production workloads
3. **Network Connectivity:** Azure ExpressRoute for dedicated inter-region connectivity with VNet peering as secondary failover link
4. **Coordination Service:** 5-node ZooKeeper ensemble distributed across 2 primary + 2 secondary + 1 tertiary regions for multi-region write resilience
5. **Infrastructure Automation:** Terraform for infrastructure provisioning + Ansible for Kafka configuration (hybrid IaC approach)
6. **Security Model:** SASL/SCRAM authentication with TLS in-transit encryption + Azure Disk Encryption at-rest + Azure Key Vault for secrets management
7. **Monitoring Strategy:** JMX/Prometheus metrics collection + Azure Monitor integration + OpenTelemetry distributed tracing

### Audience and Usage

This document serves multiple personas:

- **Solution Architects:** Understand multi-region design patterns and trade-offs to match organizational requirements
- **Platform Engineers:** Follow the step-by-step deployment guide to provision and configure clusters
- **Site Reliability Engineers:** Reference operational procedures, monitoring guidance, and disaster recovery runbooks
- **Security Teams:** Review security configuration sections for compliance validation
- **DevOps/Operators:** Implement CI/CD pipelines using provided Terraform/Ansible templates

---

## 1. Reference Architecture

### 1.1 Multi-Region Topology Overview

The reference architecture deploys a unified Kafka cluster spanning three Azure regions with strategic broker role assignment:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    CONFLUENT MULTI-REGION CLUSTER (MRC)                   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Azure Region 1: East US 2 (Primary)                                  │ │
│  │                                                                       │ │
│  │  Availability Zone 1        Availability Zone 2       Zone 3         │ │
│  │  ┌──────────────────┐      ┌──────────────────┐   ┌──────────────┐  │ │
│  │  │ Broker 1         │      │ Broker 2         │   │ Broker 3     │  │ │
│  │  │ Role: Leader     │      │ Role: Follower   │   │ Role: Leader │  │ │
│  │  │ Replication: 3   │      │ Replication: 3   │   │ Replication: 3   │ │
│  │  └──────────────────┘      └──────────────────┘   └──────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │ ZooKeeper Voting Ensemble (2 nodes)                          │  │ │
│  │  │ ├─ ZK-1 (Voting Member, Primary)                             │  │ │
│  │  │ └─ ZK-2 (Voting Member, Secondary AZ)                        │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                ↕ Sync Replication (ISR)                  │
│                                ↕ (< 5ms latency)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Azure Region 2: West Europe (Secondary)                             │ │
│  │                                                                       │ │
│  │  Availability Zone 1        Availability Zone 2       Zone 3         │ │
│  │  ┌──────────────────┐      ┌──────────────────┐   ┌──────────────┐  │ │
│  │  │ Broker 4         │      │ Broker 5         │   │ Broker 6     │  │ │
│  │  │ Role: Follower   │      │ Role: Observer   │   │ Role: Observer   │ │
│  │  │ Replication: 3   │      │ Replication: 3   │   │ Replication: 3   │ │
│  │  └──────────────────┘      └──────────────────┘   └──────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │ ZooKeeper Voting Ensemble (2 nodes)                          │  │ │
│  │  │ ├─ ZK-3 (Voting Member, Primary)                             │  │ │
│  │  │ └─ ZK-4 (Voting Member, Secondary AZ)                        │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                ↕ Async Replication (Observers)           │
│                                ↕ (< 20ms latency acceptable)             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Azure Region 3: Southeast Asia (Tertiary - Optional)                │ │
│  │                                                                       │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │ ZooKeeper-5 (Voting Member for quorum, Observer Broker Role) │  │ │
│  │  │ Enables write resilience across 3 geographic regions         │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘

Cross-Region Connectivity:
  ExpressRoute (Primary):      50 Gbps dedicated circuit
  VNet Peering (Secondary):    Failover backup connectivity
  Inter-region latency:        < 20ms (adjacent regions)
```

### 1.2 Component Inventory

#### Kafka Brokers

| Component | Quantity per Region | Azure SKU | vCPU | Memory | Storage | Network |
|-----------|-------------------|-----------|------|--------|---------|---------|
| **Broker** | 3 per region (6 total) | Standard_D16s_v5 | 16 | 64 GB | RAID 10, 4×P60 (8 TB usable) | 8 Gbps |
| **Storage** | Per broker | Premium SSD | - | - | 32 TB effective (RAID 10) | - |
| **Network Interface** | 1 per broker | - | - | - | - | Accelerated Networking enabled |

**Total Cluster Capacity:**
- Compute: 12 total brokers (6 primary leaders/followers, 6 secondary followers/observers)
- Storage: 96 TB total raw (RAID 10: ~48 TB effective)
- Throughput: ~20 Gbps aggregate (2 Gbps per broker × 10 brokers with ISR overhead)
- Partition capacity: 2,000-3,000 partitions per broker, 12,000-18,000 total

#### ZooKeeper Ensemble

| Component | Quantity | Azure SKU | vCPU | Memory | Storage | Role |
|-----------|----------|-----------|------|--------|---------|------|
| **ZK Servers** | 5 total | Standard_D8s_v3 | 8 | 32 GB | 512 GB Premium SSD | Voting Ensemble |
| **Distribution** | 2 in East US 2 | - | - | - | - | Primary region (quorum) |
| **Distribution** | 2 in West Europe | - | - | - | - | Secondary region (quorum) |
| **Distribution** | 1 in Southeast Asia | - | - | - | - | Tertiary (tie-breaker vote) |

**Quorum Tolerance:** 5-node ensemble tolerates failure of 2 nodes while maintaining write quorum (3 of 5 voting members)

#### Network Infrastructure

| Component | Primary Region | Secondary Region | Tertiary Region |
|-----------|---|---|---|
| **VNet CIDR** | 10.0.0.0/16 | 10.1.0.0/16 | 10.2.0.0/16 |
| **Broker Subnet** | 10.0.1.0/24 | 10.1.1.0/24 | 10.2.1.0/24 |
| **ZK Subnet** | 10.0.2.0/24 | 10.1.2.0/24 | 10.2.2.0/24 |
| **ExpressRoute Circuit** | 50 Gbps dedicated | Peering endpoints | Peering endpoints |
| **Cross-Region Links** | Primary ↔ Secondary | Primary ↔ Tertiary | Secondary ↔ Tertiary |

### 1.3 Zone and Region Placement Strategy

#### Availability Zone Distribution (Within Each Region)

Each region's 3 Kafka brokers are explicitly placed across 3 availability zones to maximize resilience:

```
East US 2 Region:
  - AZ-1: kafka-broker-01 (10.0.1.10)
  - AZ-2: kafka-broker-02 (10.0.1.20)
  - AZ-3: kafka-broker-03 (10.0.1.30)

West Europe Region:
  - AZ-1: kafka-broker-04 (10.1.1.10)
  - AZ-2: kafka-broker-05 (10.1.1.20)
  - AZ-3: kafka-broker-06 (10.1.1.30)
```

**Rack Awareness Configuration:**
```properties
# Broker configuration
broker.rack=eastus2-az1  # For kafka-broker-01
broker.rack=eastus2-az2  # For kafka-broker-02
broker.rack=eastus2-az3  # For kafka-broker-03
```

Kafka's rack-aware replica assignment ensures no two replicas of a partition reside in the same AZ, providing protection against:
- Zone-level outages (datacenter power loss, network issues)
- Correlated failures (planned maintenance in specific zones)

#### Region Selection Rationale

**East US 2 (Primary Production Region)**
- Low latency hub for North American traffic
- Strong Azure services ecosystem (Log Analytics, App Insights)
- 99.99% availability SLA with 3 AZs
- Paired with Central US for disaster recovery priority

**West Europe (Secondary/DR Region)**
- ~15ms latency from East US 2 (acceptable for asynchronous replication)
- GDPR compliance for EU data residency requirements
- Disaster recovery capability with independent failure domain
- Observer replicas enable local read throughput in Europe

**Southeast Asia (Tertiary - Optional)**
- Completes geographic distribution for true multi-region resilience
- Enables 5-node ZooKeeper quorum across 3 geographic regions
- Survives simultaneous outage of any single region
- ZooKeeper-5 node acts as quorum tie-breaker without broker deployment

### 1.4 Network Architecture Across Regions

#### Cross-Region Connectivity

**Primary: Azure ExpressRoute (Recommended)**

```
┌──────────────┐
│ East US 2    │
│   VNet       │
│ 10.0.0.0/16  │
└──────┬───────┘
       │
  ┌────▼─────────────────────────────┐
  │  Azure ExpressRoute Circuit       │
  │  50 Gbps Premium SKU              │
  │  Peering Location: Washington DC  │
  │  Private Peering Enabled          │
  │  SLA: 99.95% uptime               │
  │  Latency: < 5ms                   │
  └────┬─────────────────────────────┘
       │
┌──────▼───────┐
│ West Europe  │
│   VNet       │
│ 10.1.0.0/16  │
└──────────────┘
```

**Secondary: Global VNet Peering (Failover)**

When ExpressRoute circuit is unavailable, traffic automatically switches to VNet peering:
- Zero egress charges for intra-region traffic
- ~10-20ms latency for cross-region traffic
- Asymmetric bandwidth (subject to Azure resource limits)
- Suitable for short-term failover scenarios (< 24 hours)

**Network Security Groups (NSGs) Configuration:**

```
East US 2 Kafka Broker Subnet NSG:
  Inbound Rules:
    - Port 9092 (SASL_SSL): Allow from Client Subnet + West Europe (10.1.0.0/16)
    - Port 9093 (Inter-Broker): Allow from all Kafka brokers (10.0.1.0/24 + 10.1.1.0/24)
    - Port 22 (SSH): Allow from Management Subnet (10.0.4.0/24) only
    - Port 5671 (JMX): Allow from Management Subnet only

  Egress Rules:
    - All to ZooKeeper subnet (10.0.2.0/24)
    - All to West Europe VNet (10.1.0.0/16)
    - DNS (53) to Azure DNS (168.63.129.16)
```

---

## 2. Component Specifications

### 2.1 Azure VM Sizing and Storage Configuration

#### VM Selection: Standard_D16s_v5

**Rationale:**
- 16 vCPU cores provide sufficient parallelism for Kafka broker thread pools
- 64 GB memory balances JVM heap (16 GB) with OS page cache (40 GB)
- 8 Gbps network bandwidth handles high-throughput replication
- Cost-effective relative to E-series memory-optimized instances
- Accelerated Networking (SR-IOV) available for sub-millisecond latency

**Memory Allocation (64 GB total):**
```
JVM Heap:        16 GB (-Xms16g -Xmx16g)
OS Page Cache:   40 GB (automatically managed by kernel)
System Reserve:  8 GB (kernel, buffers, page tables)
```

**CPU Configuration:**
- 8 dedicated vCPU cores
- Hyper-threading enabled (16 logical cores)
- G1GC garbage collection tuned for 20ms max pause time

#### Storage Configuration: RAID 10

**Topology:**
```
Per Broker: 4 × Premium SSD P60 (8 TB each)
RAID Layout: RAID 10 (Striped + Mirrored)
Effective Capacity: 16 TB raw → 8 TB effective (after mirroring)

Configuration:
  Disk 1 & Disk 2 → Mirrored Pair A
  Disk 3 & Disk 4 → Mirrored Pair B
  Pairs A & B → Striped together
```

**Performance Characteristics:**
- Capacity: 8 TB per broker × 6 brokers = 48 TB effective total
- IOPS: ~9,200 IOPS per broker (4 × P60 @ 2,300 IOPS each)
- Throughput: ~1,000 MB/s per broker (4 × 250 MB/s)
- Redundancy: Single disk failure survivable without data loss
- Availability: 99.99% SLA per disk

**Disk Allocation:**
```
/dev/sda        128 GB (OS disk, Premium SSD P10)
/dev/sdb-sde    8 TB each (Data disks, Premium SSD P60 × 4, RAID 10)
└── Mounted at /var/kafka/data
```

**Sizing Formula (Data Retention):**
```
Required Capacity = (Daily Ingestion Rate GB × Retention Days) × 1.2 Safety Margin

Example:
  Ingestion Rate: 100 GB/day
  Retention: 7 days
  Replication Factor: 3
  Capacity = (100 × 7) × 1.2 × 3 = 2,520 GB = 2.5 TB per broker
  Recommendation: 8 TB per broker (3.2× buffer for headroom)
```

### 2.2 Confluent Edition Selection

#### Confluent Platform Enterprise

**Rationale for Enterprise Edition:**

- **Multi-Region Clusters (MRC):** Core feature enabling stretched deployments with role-based replication
- **Observer Replicas:** Asynchronous replication without ISR latency penalty
- **Cluster Linking:** Bi-directional topic replication across independent clusters
- **Tiered Storage:** Archive old log segments to Azure Blob Storage for cost reduction
- **Enhanced Security:** SASL/OAuth2, mTLS, Encryption at Rest
- **Monitoring:** Confluent Control Center for centralized cluster management

**Licensing Model:**
- Per-broker monthly subscription (~$3,000-5,000 per broker)
- Optional: Extended support SLA (24/7 responses)
- Free tier unavailable for production multi-region deployments

**Alternatives Considered (Not Recommended):**
- **Apache Kafka OSS:** Missing MRC and observer replicas; requires custom replication logic
- **Confluent Cloud:** Managed service; limited control over infrastructure; higher per-GB costs for high-throughput workloads
- **Confluent Community Edition:** No production SLA; limited to 3-broker clusters

### 2.3 ZooKeeper Ensemble Design

#### 5-Node Ensemble Topology

**Ensemble Configuration:**
```
server.1=zk-east-us-1.azure.internal:2888:3888      (East US 2, Voting)
server.2=zk-east-us-2.azure.internal:2888:3888      (East US 2, Voting)
server.3=zk-west-europe-1.azure.internal:2888:3888  (West Europe, Voting)
server.4=zk-west-europe-2.azure.internal:2888:3888  (West Europe, Voting)
server.5=zk-southeast-asia-1.azure.internal:2888:3888 (Southeast Asia, Voting)
```

**Quorum Calculation:**
- Ensemble size: 5 nodes
- Quorum required: 3 nodes (5/2 + 1)
- Fault tolerance: 2 simultaneous node failures
- Failure scenarios:
  - Single region failure: Still achieves quorum (3 voting members survive)
  - Single zone failure: No impact (voting members distributed across AZs)
  - Dual region failure: Lost (only 1-2 voting members remain)

**Performance Tuning:**

```properties
# zoo.cfg configuration
tickTime=2000
dataDir=/var/lib/zookeeper
clientPort=2181

# Snapshot and log settings
snapCount=100000
autopurge.snapRetainCount=5
autopurge.purgeInterval=24

# Session timeout
minSessionTimeout=4000
maxSessionTimeout=40000

# Performance optimization
forceSync=no
jute.maxbuffer=4194304
```

**JVM Configuration:**

```bash
export SERVER_JVMFLAGS="
  -Xms4G -Xmx4G
  -XX:+UseG1GC
  -XX:MaxGCPauseMillis=20
  -XX:+ParallelRefProcEnabled
  -Djute.maxbuffer=4194304
"
```

**Scaling Considerations:**
- 5 nodes sufficient for 6-broker Kafka cluster
- Add observer nodes (non-voting) if additional read capacity needed
- Do not exceed 7-9 voting nodes (latency impact on writes becomes significant)

### 2.4 Networking Configuration

#### Virtual Network Design

**Primary Region (East US 2): 10.0.0.0/16**

| Subnet | CIDR | Purpose | Size |
|--------|------|---------|------|
| Kafka Brokers | 10.0.1.0/24 | Broker VMs | 250 usable IPs |
| ZooKeeper | 10.0.2.0/24 | ZK ensemble | 250 usable IPs |
| Clients | 10.0.3.0/24 | Producer/Consumer apps | 250 usable IPs |
| Management | 10.0.4.0/24 | Admin, monitoring | 250 usable IPs |
| Gateway | 10.0.5.0/27 | ExpressRoute/VPN | 30 usable IPs |

**Secondary Region (West Europe): 10.1.0.0/16**

Mirror structure with updated CIDRs (10.1.x.0/24 for each subnet)

#### Accelerated Networking

**Enable on All Kafka Broker NICs:**

```bash
# Azure CLI command
az network nic create \
  --resource-group kafka-rg \
  --name kafka-broker-01-nic \
  --vnet-name kafka-vnet-eastus \
  --subnet kafka-brokers \
  --accelerated-networking true \
  --network-security-group kafka-nsg
```

**Benefits:**
- Latency reduction: 40-50% improvement (from ~50µs to ~10µs)
- SR-IOV bypass of Hyper-V virtual switch
- Minimum latency for broker-to-broker replication
- Prerequisite: D-series v3 or newer

#### ExpressRoute Configuration

**Circuit Specification:**
```
SKU:                Premium (supports Global Reach)
Bandwidth:          50 Gbps
Peering Type:       Private (for VNet connectivity)
Provider:           Equinix/Megaport
Redundancy:         Dual circuits recommended for production
BGP:                Enabled for dynamic routing
Session Timeout:    3 seconds
```

**Implementation Checklist:**
- [ ] Create ExpressRoute circuit in East US location
- [ ] Provision gateway subnet (10.0.5.0/27) in East US VNet
- [ ] Create VPN Gateway (VpnGw3AZ SKU for redundancy)
- [ ] Link ExpressRoute circuit to gateway
- [ ] Establish peering with West Europe VNet via global VNet peering
- [ ] Test failover from ExpressRoute to VNet peering

---

## 3. Multi-Region Strategy

### 3.1 Architecture Pattern Selection

#### Confluent Multi-Region Clusters (MRC): Recommended Pattern

**Decision Rationale:**

| Requirement | Active-Active | Active-Passive | MRC (Selected) |
|-------------|---|---|---|
| Write Latency | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Global Ordering | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Automatic Failover | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Operational Simplicity | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Cost Efficiency | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

MRC provides superior balance across all dimensions for Albertsons use case.

#### MRC Architecture Benefits

1. **Single Logical Cluster:** All brokers operate as unified cluster; simplifies operational model
2. **Automatic Failover:** Leader election happens automatically across regions; no client reconnection required
3. **Flexible Replication:** Role-based placement (leaders, followers, observers) optimizes per-partition
4. **Read Locality:** Observer replicas in remote regions enable low-latency reads without ISR delay
5. **Write Resilience:** Synchronous replication (ISR) ensures durability; observers provide async replication for latency

### 3.2 Replication Configuration

#### Leader and Follower Placement

**Partition-Level Replication Policy (JSON):**

```json
{
  "version": 2,
  "replicas": [
    {
      "count": 2,
      "constraints": {
        "rack": "eastus2-*"
      }
    },
    {
      "count": 1,
      "constraints": {
        "rack": "westeurope-*"
      }
    }
  ],
  "observers": [
    {
      "count": 1,
      "constraints": {
        "rack": "westeurope-*"
      }
    }
  ],
  "observerPromotionPolicy": "under-min-isr"
}
```

**Interpretation:**
- **2 replicas in East US 2:** Leader + 1 Follower (ISR members, synchronous replication)
- **1 replica in West Europe:** Follower or Observer depending on promotion policy
- **1 observer in West Europe:** Asynchronous replica for read locality
- **Total replication factor:** 4 (2 ISR members + 1 follower + 1 observer)

**Write Durability (acks=all):**
```
Producer sends message to Leader (East US 2)
    ↓
Leader appends to local log
    ↓
Leader replicates to Follower (East US 2, same AZ)
    ↓
Leader replicates to Follower (West Europe)
    ↓
All three followers acknowledge
    ↓
Producer receives ACK
    ↓
Observer asynchronously replicates in background (no ACK impact)
```

**Latency Impact:**
- Intra-region replication (Follower in East US 2): < 1ms additional latency
- Cross-region replication (Follower in West Europe): + 15-20ms latency
- Observer replication (background): Not counted toward ACK latency

#### min.insync.replicas Configuration

```properties
# Topic-level configuration
min.insync.replicas=2
```

**Semantics:**
- Producer must receive acknowledgment from leader + 1 in-sync replica before write commits
- In 4-replica setup: Leader + 1 Follower (same region) = quorum
- West Europe follower acknowledgment not required (faster writes)
- If West Europe follower falls behind, it's removed from ISR; writes still proceed with 2 (leader + East US Follower)

**RPO (Recovery Point Objective):**
```
With min.insync.replicas=2 and cross-region followers:
- RTO: < 5 seconds (automatic leader election)
- RPO: 0 messages (fully replicated before ACK)
- Trade-off: +15-20ms write latency for durability
```

### 3.3 Azure Region Pairs and Topology

#### Recommended Region Pair: East US 2 ↔ West Europe

**Justification:**
1. **Latency:** ~15ms inter-region latency (optimal for synchronous replication)
2. **Geographic Diversity:** Separated by Atlantic Ocean; low correlation of outages
3. **Azure Paired Region:** Official pairing per Microsoft documentation
4. **Compliance:** Data stays within US/EU boundaries
5. **Services Ecosystem:** Both regions have comprehensive Azure services

**Tertiary Region: Southeast Asia (Optional but Recommended)**

Adds third geographic region for true multi-region resilience:
```
Primary write location:     East US 2 (Americas)
Secondary read location:    West Europe (EMEA)
Tertiary quorum location:   Southeast Asia (APAC)

ZooKeeper benefits:
  - 5-node ensemble survives any single region failure
  - Quorum maintained even if 2 regions simultaneously fail
  - Write operations continue from minority region with 1 survivor

Trade-off:
  - Additional infrastructure cost (~$1.5K/month for ZK-5 + tertiary region replication)
  - Worth cost for mission-critical deployments
```

#### Failover Scenarios and Recovery

**Scenario 1: Zone Failure Within Region**

```
Failure: kafka-broker-03 in East US 2 AZ-3 fails

Before:
  Partition-0 Replicas: [broker-01 (AZ-1), broker-02 (AZ-2), broker-03 (AZ-3)]
  ISR: [broker-01, broker-02]

Immediately (Kafka auto-recovery):
  ISR: [broker-01, broker-02]  (broker-03 removed)
  Partition remains available (2 ISR members > min.insync.replicas=2)

Recovery (within 5 minutes):
  Broker-03 VM replaced in same AZ
  Kafka auto-rebalances replicas
  ISR restored to 3 members
```

**Scenario 2: Region Failure (East US 2 down)**

```
Failure: All brokers in East US 2 unreachable (region outage)

Immediately (< 5 seconds):
  Kafka cluster detects partitions with leader in failed region
  Leader election initiated for affected partitions
  Leader promotion: Brokers in West Europe promoted to leader
  
Result:
  - Partitions with observers in West Europe become available (read-only data + local writes)
  - Partitions with full replicas in West Europe fully recoverable
  - Write latency increases 15-20ms due to cross-region leader

Recovery (1-4 hours):
  - East US 2 region recovers
  - Brokers rejoin cluster
  - Leaders optionally migrate back to East US 2 (can be managed)
  - Replication catchup (1-2 hours depending on volume)
```

**Scenario 3: Multi-Region Failure (East US 2 + West Europe both fail)**

```
This scenario requires Southeast Asia tertiary region:

Failure: East US 2 and West Europe both unreachable

With 3-region architecture:
  - ZooKeeper quorum survives (Southeast Asia ZK-5 + 2 others survive)
  - Brokers in Southeast Asia operational (if deployed)
  - Manual failover: Redirect applications to Southeast Asia cluster

Recovery:
  - Restore from snapshots when primary regions recover
  - Or wait for regions to recover and gradual reintegration

RPO: Up to 4 hours (backup RTO met)
```

### 3.4 Producer Patterns for Multi-Region

#### Recommended: Active-Passive with Local Write Preference

```
┌─────────────────────────────────────────┐
│ Producer Application (North American)    │
│                                          │
│ Configuration:                           │
│   primary: kafka-broker-01.eastus2.azure │
│   secondary: kafka-broker-04.westeurope  │
└─────────────────────────────────────────┘
        │
        ├─ Primary write attempt (East US 2)
        │  ├─ Success → Return ACK
        │  └─ Failure (after 10s timeout)
        │
        ├─ Failover write attempt (West Europe)
        │  ├─ Success → Return ACK, log failover event
        │  └─ Failure → Return error to application
        │
        └─ Auto-recovery: Periodically test primary cluster health
           ├─ If recovered → Resume primary writes
           └─ Backoff if still failing
```

**Implementation Pattern (Python):**

```python
class MultiRegionProducer:
    def __init__(self, primary_servers, secondary_servers):
        self.primary_producer = KafkaProducer(
            bootstrap_servers=primary_servers,
            client_id='producer-primary'
        )
        self.secondary_producer = KafkaProducer(
            bootstrap_servers=secondary_servers,
            client_id='producer-secondary'
        )
        self.use_primary = True
        self.health_check_thread = Thread(target=self._health_check)
        self.health_check_thread.start()
    
    def send(self, topic, key, value):
        """Send with automatic failover."""
        producer = self.primary_producer if self.use_primary else self.secondary_producer
        try:
            future = producer.send(
                topic=topic,
                key=key,
                value=value,
                timeout_ms=10000
            )
            future.get(timeout=5)  # Wait for response
            return {'success': True, 'region': 'primary' if self.use_primary else 'secondary'}
        except Exception as e:
            if self.use_primary:
                self.use_primary = False  # Failover to secondary
                return self.send(topic, key, value)  # Retry on secondary
            else:
                raise  # Give up after secondary fails
    
    def _health_check(self):
        """Periodically check primary cluster health."""
        while True:
            time.sleep(30)  # Check every 30 seconds
            try:
                self.primary_producer.partitions_for('__healthcheck__')
                self.use_primary = True
            except:
                self.use_primary = False
```

---

## 4. Step-by-Step Deployment Guide

### 4.1 Infrastructure Provisioning

#### Prerequisites

```bash
# 1. Install required tools
brew install terraform ansible azure-cli

# 2. Authenticate to Azure
az login
az account set --subscription "<subscription-id>"

# 3. Create resource group
az group create \
  --name kafka-rg-prod \
  --location eastus2
```

#### Terraform Infrastructure Provisioning

**Directory Structure:**

```
kafka-infrastructure/
├── terraform/
│   ├── main.tf                 # Primary configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values (IPs, FQDNs)
│   ├── terraform.tfvars        # Environment-specific values
│   ├── modules/
│   │   ├── networking/         # VNets, NSGs, peering
│   │   ├── compute/            # VMs, disks, NICs
│   │   └── monitoring/         # Log Analytics, monitoring
│   └── environments/
│       └── production/         # Production workspace
└── README.md
```

**Key Terraform Modules:**

```hcl
# main.tf - Primary configuration

module "primary_region_network" {
  source = "./modules/networking"
  
  region               = "eastus2"
  resource_group_name  = "kafka-rg-prod"
  vnet_cidr           = "10.0.0.0/16"
  
  subnets = {
    kafka_brokers    = "10.0.1.0/24"
    zookeeper        = "10.0.2.0/24"
    clients          = "10.0.3.0/24"
    management       = "10.0.4.0/24"
    gateway          = "10.0.5.0/27"
  }
}

module "primary_region_compute" {
  source = "./modules/compute"
  
  resource_group_name  = "kafka-rg-prod"
  region              = "eastus2"
  broker_count        = 3
  broker_vm_size      = "Standard_D16s_v5"
  
  broker_config = {
    disk_type           = "Premium_LRS"
    disk_count          = 4
    disk_size_gb        = 1024
    accelerated_networking = true
  }
}

module "secondary_region_network" {
  source = "./modules/networking"
  
  region               = "westeurope"
  resource_group_name  = "kafka-rg-prod"
  vnet_cidr           = "10.1.0.0/16"
  
  # Similar subnet configuration for secondary region
}

# VNet Peering
resource "azurerm_virtual_network_peering" "primary_to_secondary" {
  name                      = "primary-to-secondary-peering"
  resource_group_name       = "kafka-rg-prod"
  virtual_network_name      = module.primary_region_network.vnet_name
  remote_virtual_network_id = module.secondary_region_network.vnet_id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
}
```

**Terraform Apply Process:**

```bash
# 1. Initialize Terraform
terraform init

# 2. Validate configuration
terraform validate

# 3. Create plan (review changes)
terraform plan -out=tfplan

# 4. Apply infrastructure
terraform apply tfplan

# 5. Export outputs (save IPs, FQDNs for Ansible)
terraform output -json > outputs.json
```

### 4.2 Confluent Platform Installation

#### Ansible Playbook Structure

```yaml
# deploy-kafka.yml

---
- name: Deploy Confluent Kafka Cluster
  hosts: kafka_brokers
  serial: 1  # Rolling deployment
  tasks:
    - name: Pre-deployment checks
      include: roles/kafka-broker/tasks/pre-flight.yml
    
    - name: Install Java runtime
      include: roles/kafka-broker/tasks/install-java.yml
    
    - name: Download Confluent Platform
      include: roles/kafka-broker/tasks/download-confluent.yml
    
    - name: Configure broker
      template:
        src: server.properties.j2
        dest: /etc/kafka/server.properties
        owner: kafka
        group: kafka
        mode: 0644
      notify: Restart Kafka broker
    
    - name: Configure broker rack awareness
      lineinfile:
        path: /etc/kafka/server.properties
        line: "broker.rack={{ broker_rack }}"
    
    - name: Start Kafka broker
      systemd:
        name: confluent-kafka
        state: started
        enabled: yes
    
    - name: Health check
      include: roles/kafka-broker/tasks/health-check.yml

- name: Configure Multi-Region Replication
  hosts: localhost
  tasks:
    - name: Create multi-region cluster configuration
      include: roles/kafka-cluster/tasks/mrc-config.yml
    
    - name: Create topics with MRC policies
      include: roles/kafka-cluster/tasks/create-topics.yml
```

**Broker Configuration Template (server.properties.j2):**

```properties
# Broker Identity
broker.id={{ broker_id }}
broker.rack={{ broker_rack }}  # eastus2-az1, westeurope-az1, etc.

# Network Configuration
listeners=SASL_SSL://0.0.0.0:9092,PLAINTEXT://localhost:29092
advertised.listeners=SASL_SSL://{{ advertised_hostname }}:9092
inter.broker.listener.name=SASL_SSL
security.inter.broker.protocol=SASL_SSL

# Authentication
sasl.enabled.mechanisms=SCRAM-SHA-256
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-256

# SSL/TLS
ssl.keystore.location=/etc/kafka/secrets/kafka.broker.keystore.jks
ssl.keystore.password={{ keystore_password }}
ssl.key.password={{ key_password }}
ssl.truststore.location=/etc/kafka/secrets/kafka.broker.truststore.jks
ssl.truststore.password={{ truststore_password }}

# Log Configuration
log.dirs=/var/kafka/data
log.segment.bytes=1073741824
log.retention.hours=168
log.cleanup.policy=retention

# Replication
min.insync.replicas=2
default.replication.factor=3

# Performance
num.network.threads=8
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# JMX Metrics
metrics.num.samples=100
metrics.sample.window.ms=30000
```

### 4.3 ZooKeeper Ensemble Setup

#### ZooKeeper Installation Playbook

```yaml
# deploy-zookeeper.yml

---
- name: Deploy ZooKeeper Ensemble
  hosts: zookeeper_servers
  tasks:
    - name: Install Java runtime
      apt:
        name: openjdk-11-jre-headless
        state: present
    
    - name: Create zookeeper user
      user:
        name: zookeeper
        state: present
        shell: /bin/bash
    
    - name: Download ZooKeeper
      get_url:
        url: "https://archive.apache.org/dist/zookeeper/zookeeper-3.8.1/apache-zookeeper-3.8.1-bin.tar.gz"
        dest: /tmp/zookeeper.tar.gz
    
    - name: Extract ZooKeeper
      unarchive:
        src: /tmp/zookeeper.tar.gz
        dest: /opt
        remote_src: yes
        owner: zookeeper
        group: zookeeper
    
    - name: Create ZooKeeper config
      template:
        src: zoo.cfg.j2
        dest: /opt/apache-zookeeper-3.8.1/conf/zoo.cfg
        owner: zookeeper
    
    - name: Create myid file
      copy:
        content: "{{ zookeeper_id }}"
        dest: "{{ zookeeper_data_dir }}/myid"
        owner: zookeeper
        group: zookeeper
    
    - name: Start ZooKeeper
      systemd:
        name: zookeeper
        state: started
        enabled: yes
    
    - name: Verify ensemble health
      shell: |
        echo ruok | nc localhost 2181
      register: ruok_result
      until: ruok_result.stdout == "imok"
      retries: 5
      delay: 10
```

**zoo.cfg Configuration:**

```properties
# zoo.cfg - ZooKeeper ensemble configuration

tickTime=2000
dataDir=/var/lib/zookeeper
clientPort=2181

# Multi-region ensemble
server.1=zk-eastus2-1.azure.internal:2888:3888
server.2=zk-eastus2-2.azure.internal:2888:3888
server.3=zk-westeurope-1.azure.internal:2888:3888
server.4=zk-westeurope-2.azure.internal:2888:3888
server.5=zk-southeastasia-1.azure.internal:2888:3888

# Performance tuning
snapCount=100000
autopurge.snapRetainCount=5
autopurge.purgeInterval=24
forceSync=no
jute.maxbuffer=4194304

# Session timeouts
minSessionTimeout=4000
maxSessionTimeout=40000
```

### 4.4 Broker Configuration and Cluster Initialization

#### Cluster Bootstrap

```bash
# 1. Wait for all brokers to start and form cluster
# Monitor: kafka-broker-api-versions.sh
kafka-broker-api-versions.sh \
  --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092

# 2. Verify broker cluster formation
kafka-metadata.sh \
  --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
  --describe

# Expected output: All 6 brokers listed (3 primary + 3 secondary)

# 3. Create system topics
kafka-topics.sh \
  --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
  --create \
  --topic __consumer_offsets \
  --partitions 50 \
  --replication-factor 3

# 4. Verify cluster leader election
kafka-topics.sh \
  --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
  --describe
```

### 4.5 Multi-Region Replication Setup

#### Cluster Linking Configuration (Bi-directional)

```yaml
# configure-cluster-linking.yml

---
- name: Configure Cluster Linking for Multi-Region Replication
  hosts: kafka-control-host
  tasks:
    - name: Create cluster link from primary to secondary
      shell: |
        kafka-cluster-links --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
          --create \
          --link primary-to-secondary \
          --config bootstrap.servers=kafka-broker-04.westeurope.azure.internal:9092 \
          --config security.protocol=SASL_SSL \
          --config sasl.mechanism=SCRAM-SHA-256 \
          --config sasl.username=cluster-link-user \
          --config sasl.password=<password-from-keyvault>
    
    - name: Configure mirror topics for replication
      shell: |
        kafka-mirrors --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
          --create \
          --mirror-topic ".*" \
          --link primary-to-secondary \
          --consumer-group-ids=".*" \
          --consumer-group-ids-pattern \
          --checkpoint-interval-seconds=60
    
    - name: Verify mirror status
      shell: |
        kafka-mirrors --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
          --describe \
          --link primary-to-secondary
```

#### Observer Replica Promotion Policy

```bash
# Set observer promotion policy on critical topics
kafka-configs.sh \
  --bootstrap-server kafka-broker-01.eastus2.azure.internal:9092 \
  --alter \
  --entity-type topics \
  --entity-name "critical-events" \
  --add-config min.insync.replicas=2,observer.promotion.policy=under-min-isr
```

### 4.6 Security Configuration

#### TLS Certificate Setup

```bash
# 1. Generate CA key pair
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 3650 -key ca-key.pem -out ca-cert.pem \
  -subj "/CN=kafka-ca/O=Organization/C=US"

# 2. Generate broker key pairs (for each broker)
for i in {1..6}; do
  openssl genrsa -out broker-${i}-key.pem 4096
  openssl req -new -key broker-${i}-key.pem -out broker-${i}.csr \
    -subj "/CN=kafka-broker-${i}/O=Organization/C=US"
  
  # Sign with CA
  openssl x509 -req -days 365 -in broker-${i}.csr \
    -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
    -out broker-${i}-cert.pem \
    -extfile <(printf "subjectAltName=DNS:kafka-broker-${i}.azure.internal,DNS:kafka-broker-${i}.eastus2.azure.com")
done

# 3. Create keystores and truststores
for i in {1..6}; do
  # Broker keystore
  openssl pkcs12 -export -in broker-${i}-cert.pem -inkey broker-${i}-key.pem \
    -out kafka.broker-${i}.keystore.p12 -name kafka-broker-${i} \
    -CAfile ca-cert.pem -password pass:keystore_password
  
  # Truststore (same for all)
  keytool -import -file ca-cert.pem -alias ca \
    -keystore kafka.truststore.jks -storepass truststore_password -noprompt
done

# 4. Upload certificates to Azure Key Vault
for i in {1..6}; do
  az keyvault certificate import \
    --vault-name kafka-keyvault-prod \
    --name kafka-broker-${i}-cert \
    --file kafka.broker-${i}.keystore.p12 \
    --password keystore_password
done
```

#### SASL User Creation

```bash
# Create SCRAM credentials for brokers
kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter --add-config 'SCRAM-SHA-256=[password=broker-secret]' \
  --entity-type users --entity-name broker-user \
  --command-config admin.properties

# Create credentials for client applications
kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter --add-config 'SCRAM-SHA-256=[password=client-secret]' \
  --entity-type users --entity-name application-producer \
  --command-config admin.properties

kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter --add-config 'SCRAM-SHA-256=[password=consumer-secret]' \
  --entity-type users --entity-name application-consumer \
  --command-config admin.properties
```

#### ACL Configuration

```bash
# Producer permissions
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:application-producer \
  --operation Write --topic "^app-.*" \
  --command-config admin.properties

# Consumer permissions
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:application-consumer \
  --operation Read --topic "^app-.*" \
  --group "application-consumer-group" \
  --command-config admin.properties

# Cluster admin permissions
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:kafka-admin \
  --operation All --cluster \
  --command-config admin.properties
```

---

## 5. Security Configuration

### 5.1 Authentication Framework

#### SASL/SCRAM (Recommended for Azure VMs)

```properties
# Broker Configuration
sasl.enabled.mechanisms=SCRAM-SHA-256
listeners=SASL_SSL://0.0.0.0:9092
advertised.listeners=SASL_SSL://kafka-broker-01.eastus2.azure.com:9092
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-256

# Client Configuration
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-256
sasl.username=producer-app
sasl.password=<stored-in-azure-key-vault>
ssl.truststore.location=/etc/kafka/secrets/truststore.jks
ssl.truststore.password=<truststore-password>
```

**Credential Management:**
- Store all SASL passwords in Azure Key Vault
- Reference via Managed Identity (no credential files)
- Rotate passwords every 90 days
- Audit all password changes via Azure Activity Log

#### OAuth2 (For Service-to-Service)

```properties
# Broker Configuration
sasl.enabled.mechanisms=OAUTHBEARER
listeners=SASL_SSL://0.0.0.0:9092
oauth.token.endpoint.uri=https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token
oauth.client.id=<kafka-broker-app-id>
oauth.client.secret=${OAUTH_CLIENT_SECRET}
oauth.scope=kafka/.default

# Client Configuration
security.protocol=SASL_SSL
sasl.mechanism=OAUTHBEARER
sasl.oauthbearer.token.endpoint.url=https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token
sasl.oauthbearer.client.id=<producer-app-id>
sasl.oauthbearer.client.secret=${OAUTH_CLIENT_SECRET}
sasl.oauthbearer.scope=kafka/.default
```

**Advantages:**
- Centralized identity via Azure AD
- Token-based authentication (no passwords shared)
- Automatic token refresh
- Audit trail via Azure AD logs

### 5.2 Encryption Strategies

#### In-Transit: TLS 1.2+

```properties
# Broker-side TLS configuration
ssl.protocol=TLSv1.2
ssl.enabled.protocols=TLSv1.2,TLSv1.3
ssl.cipher.suites=TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

# Client-side verification
ssl.truststore.location=/etc/kafka/secrets/ca-cert.jks
ssl.truststore.password=<truststore-password>
ssl.truststore.type=JKS
```

**Verification:**
```bash
# Test TLS connection
openssl s_client -connect kafka-broker-01.eastus2.azure.com:9092 \
  -cert client-cert.pem \
  -key client-key.pem \
  -CAfile ca-cert.pem

# Verify cipher suite
echo "Q" | openssl s_client -connect kafka-broker-01:9092 2>/dev/null | grep "Cipher"
```

#### At-Rest: Azure Disk Encryption

```bash
# Enable encryption on all Kafka broker VMs
az vm encryption enable \
  --resource-group kafka-rg-prod \
  --name kafka-broker-01 \
  --disk-encryption-keyvault /subscriptions/{sub-id}/resourceGroups/kafka-rg-prod/providers/Microsoft.KeyVault/vaults/kafka-keyvault

# Verify encryption status
az vm encryption show \
  --resource-group kafka-rg-prod \
  --name kafka-broker-01
```

**Encryption Key Rotation:**
```bash
# Create new key version
az keyvault key create \
  --vault-name kafka-keyvault \
  --name kafka-disk-encryption-key \
  --ops encrypt decrypt \
  --kty RSA

# Azure automatically rotates VM disks with new key
```

### 5.3 Azure Key Vault Integration

#### Secrets Management

```bash
# Store SASL passwords
az keyvault secret set \
  --vault-name kafka-keyvault-prod \
  --name sasl-broker-password \
  --value "<generated-secure-password>"

az keyvault secret set \
  --vault-name kafka-keyvault-prod \
  --name sasl-producer-password \
  --value "<application-secure-password>"

# Retrieve secrets (with Managed Identity)
az keyvault secret show \
  --vault-name kafka-keyvault-prod \
  --name sasl-broker-password \
  --query value -o tsv
```

#### Certificate Management

```bash
# Import certificate
az keyvault certificate import \
  --vault-name kafka-keyvault-prod \
  --name kafka-broker-cert \
  --file kafka.broker.keystore.p12 \
  --password <keystore-password>

# Auto-renewal policy (optional)
az keyvault certificate create \
  --vault-name kafka-keyvault-prod \
  --name kafka-broker-auto-renew \
  --policy @certificate-policy.json
```

**Certificate Policy (certificate-policy.json):**
```json
{
  "x509_props": {
    "subject": "CN=kafka-broker/O=Organization/C=US",
    "validity_months": 12,
    "key_type": "RSA",
    "key_size": 4096
  },
  "lifetime_actions": [
    {
      "trigger": {
        "lifetime_percentage": 80
      },
      "action": {
        "action_type": "AutoRenew"
      }
    }
  ]
}
```

### 5.4 Network Security (NSGs and Firewalls)

#### Network Security Group Rules

```bash
# Kafka broker inbound rules
az network nsg rule create \
  --resource-group kafka-rg-prod \
  --nsg-name kafka-brokers-nsg \
  --name allow-client-kafka \
  --priority 1000 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes "10.0.3.0/24" "10.1.3.0/24" \
  --destination-port-ranges "9092" "9093"

# Deny public access to Kafka
az network nsg rule create \
  --resource-group kafka-rg-prod \
  --nsg-name kafka-brokers-nsg \
  --name deny-public-kafka \
  --priority 1001 \
  --direction Inbound \
  --access Deny \
  --protocol Tcp \
  --source-address-prefixes "*" \
  --destination-port-ranges "9092" "9093"

# SSH access (management only)
az network nsg rule create \
  --resource-group kafka-rg-prod \
  --nsg-name kafka-brokers-nsg \
  --name allow-ssh-management \
  --priority 2000 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes "10.0.4.0/24" \
  --destination-port-ranges "22"
```

#### Azure Firewall (Optional for enhanced monitoring)

```bash
# Create Azure Firewall in hub VNet
az network firewall create \
  --resource-group kafka-rg-prod \
  --name kafka-firewall \
  --location eastus2

# Create firewall policy rules for Kafka traffic
az network firewall policy rule-collection-group create \
  --resource-group kafka-rg-prod \
  --policy-name kafka-policy \
  --rcg-name kafka-rules \
  --priority 100
```

---

## 6. Monitoring and Observability

### 6.1 Key Metrics Collection

#### JMX Metrics (Via Prometheus)

```yaml
# JMX Exporter Configuration
lowercaseOutputName: true
lowercaseOutputLabelNames: true
whitelistObjectNames:
  - "kafka.broker:*"
  - "kafka.controller:*"
  - "kafka.server:*"
  - "kafka.network:*"
  - "kafka.log:*"
```

**Critical Metrics to Monitor:**

```
Broker Health:
  - kafka_controller_active_controller_count (should be 1)
  - kafka_broker_replica_lag_max
  - kafka_broker_under_replicated_partitions
  - kafka_broker_offline_partitions_count

Replication:
  - kafka_server_replication_latency_ms
  - kafka_server_isr_shrink_rate
  - kafka_server_isr_expand_rate
  - kafka_server_in_sync_replicas_count

Performance:
  - kafka_server_produce_local_time_ms
  - kafka_server_fetch_consumer_total_time_ms
  - kafka_network_request_queue_size
  - kafka_broker_bytes_in_per_sec
  - kafka_broker_bytes_out_per_sec
```

### 6.2 Azure Monitor Integration

```yaml
# Prometheus configuration for Azure Monitor
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-broker-01:9099', 'kafka-broker-02:9099', 'kafka-broker-03:9099']

# Azure Monitor Agent configuration
azure_monitor:
  enabled: true
  workspace_id: "{{ azure_workspace_id }}"
  shared_key: "{{ azure_shared_key }}"
```

#### Critical Alert Rules (KQL - Kusto Query Language)

```kusto
// Alert: Broker Offline
Perf
| where ObjectName == "kafka.broker"
| where CounterName == "ActiveControllerCount"
| where CounterValue == 0
| project Computer, AlertSeverity="Critical", AlertName="Broker Offline"

// Alert: Under-Replicated Partitions
KafkaMetrics
| where metric_name == "UnderReplicatedPartitions"
| where metric_value > 0
| summarize max_lag=max(metric_value) by broker_id
| where max_lag > 10
| project broker_id, AlertSeverity="High", AlertName="Under-Replicated Partitions"

// Alert: Replication Latency Spike
KafkaMetrics
| where metric_name == "ReplicationLatencyMs"
| summarize p99_latency=percentile(metric_value, 99) by bin(TimeGenerated, 5m)
| where p99_latency > 10000
| project TimeGenerated, AlertSeverity="High", AlertName="Replication Latency High"

// Alert: Consumer Lag Spike
KafkaMetrics
| where metric_name == "ConsumerLag"
| summarize current_lag=avg(metric_value), max_lag=max(metric_value) by consumer_group, bin(TimeGenerated, 1m)
| where max_lag > 1000000
| project consumer_group, max_lag, AlertSeverity="Warning"
```

### 6.3 Alerting Thresholds and Actions

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| Broker Down | No response 60s | Critical | PagerDuty escalation + SMS to on-call |
| Under-Replicated Partitions | > 10 partitions | High | Email to platform team, Slack notification |
| Replication Latency | > 10 seconds | High | Email + investigation trigger |
| Consumer Lag Spike | > 1M messages | Warning | Slack notification, internal ticket |
| Disk Space Critical | < 10% free | Critical | PagerDuty + automated cleanup attempt |

### 6.4 Logging and Distributed Tracing

#### Structured Logging

```bash
# Enable debug logging (selective, not on all brokers)
log4j.logger.kafka=DEBUG
log4j.logger.kafka.controller=INFO

# Log aggregation via Fluent Bit
[INPUT]
    Name tail
    Path /var/log/kafka/*.log
    Parser json
    Tag kafka.*

[OUTPUT]
    Name azure_monitor
    Match kafka.*
    workspace_id ${AZURE_WORKSPACE_ID}
    shared_key ${AZURE_SHARED_KEY}
```

#### Distributed Tracing with OpenTelemetry

```java
// Producer instrumentation
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Tracer;

Tracer tracer = GlobalOpenTelemetry.getTracer("kafka-producer");

Span span = tracer.spanBuilder("send-message").startSpan();
try (Scope scope = span.makeCurrent()) {
    producer.send(topic, key, value, (metadata, exception) -> {
        span.setAllAttributes(Attributes.of(
            AttributeKey.stringKey("topic"), metadata.topic(),
            AttributeKey.longKey("partition"), metadata.partition(),
            AttributeKey.longKey("offset"), metadata.offset()
        ));
    });
} finally {
    span.end();
}
```

---

## 7. Disaster Recovery Runbook

### 7.1 RTO/RPO Targets

| Failure Scenario | RTO | RPO | Detection | Mitigation |
|---|---|---|---|---|
| **Single Broker Failure** | 5 min | 0 messages | ISR shrink alert | Automated replacement |
| **Single Zone Failure** | 2 min | 0 messages | Multiple broker alerts | Kafka auto-rebalance |
| **Single Region Failure** | 30 min | < 1 hour | All brokers unreachable | Manual failover |
| **Multi-Region Failure** | 2-4 hours | < 4 hours | Complete cluster loss | Restore from backups |

### 7.2 Backup Strategy

#### Cluster Metadata Backup

```bash
# Daily backup of broker configuration
#!/bin/bash
BACKUP_DIR="/backups/kafka-metadata"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Export broker configuration
for broker in {1..6}; do
  kafka-configs.sh \
    --bootstrap-server kafka-broker-${broker}:9092 \
    --describe \
    --entity-type brokers \
    --entity-name ${broker} > $BACKUP_DIR/broker-${broker}-config-${TIMESTAMP}.json
done

# Export topic configuration
kafka-topics.sh \
  --bootstrap-server kafka-broker-01:9092 \
  --describe > $BACKUP_DIR/topics-${TIMESTAMP}.json

# Upload to Azure Blob Storage
az storage blob upload-batch \
  --account-name kafkabackupsa \
  --account-key "${AZURE_STORAGE_KEY}" \
  --source $BACKUP_DIR \
  --destination-path "metadata-backups/${TIMESTAMP}"
```

#### Topic Data Snapshot

```bash
# Continuous replication via MirrorMaker 2 to backup cluster
# + daily snapshot to Azure Data Lake for long-term retention

python3 << 'EOF'
from confluent_kafka import Consumer, KafkaException
import json
from datetime import datetime
from azure.storage.blob import BlobClient

def backup_topics_to_adls(topics, backup_date=None):
    if not backup_date:
        backup_date = datetime.now().strftime("%Y-%m-%d")
    
    for topic in topics:
        consumer = Consumer({
            'bootstrap.servers': 'kafka-broker-01.eastus2.azure.internal:9092',
            'group.id': f'backup-consumer-{backup_date}',
            'auto.offset.reset': 'earliest',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'SCRAM-SHA-256',
            'sasl.username': 'backup-user',
            'sasl.password': os.getenv('BACKUP_USER_PASSWORD')
        })
        
        consumer.subscribe([topic])
        messages = []
        
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                break
            if msg.error():
                continue
            messages.append({
                'topic': msg.topic(),
                'partition': msg.partition(),
                'offset': msg.offset(),
                'key': msg.key().decode() if msg.key() else None,
                'value': msg.value().decode() if msg.value() else None,
                'timestamp': msg.timestamp()
            })
        
        # Upload to Azure Data Lake
        blob_name = f"kafka-backups/{backup_date}/{topic}.jsonl"
        blob_client = BlobClient.from_connection_string(
            os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
            container_name='kafka-backups',
            blob_name=blob_name
        )
        
        with open(f'/tmp/{topic}-{backup_date}.jsonl', 'w') as f:
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
        
        with open(f'/tmp/{topic}-{backup_date}.jsonl', 'rb') as f:
            blob_client.upload_blob(f, overwrite=True)
        
        consumer.close()

# Daily backup job
backup_topics_to_adls(['critical-events', 'orders', 'customer-events'])
EOF
```

### 7.3 Recovery Procedures

#### Scenario 1: Single Broker Failure (RTO: 5 min, RPO: 0)

```bash
#!/bin/bash
# Automated broker replacement script

FAILED_BROKER_ID=1
FAILED_BROKER_NAME="kafka-broker-01"
FAILED_BROKER_IP="10.0.1.10"

# 1. Detect failure
echo "[$(date)] Detecting broker failure..."
if ! timeout 5 bash -c "echo ruok | nc ${FAILED_BROKER_IP} 9092" 2>/dev/null; then
    echo "[$(date)] Broker ${FAILED_BROKER_NAME} is unresponsive"
    
    # 2. Terminate failed VM
    echo "[$(date)] Terminating failed VM..."
    az vm delete -g kafka-rg-prod -n ${FAILED_BROKER_NAME} --yes
    
    # 3. Provision replacement VM (via Terraform)
    echo "[$(date)] Provisioning replacement broker..."
    terraform apply -auto-approve -var "replace_broker_id=${FAILED_BROKER_ID}"
    
    # 4. Configure via Ansible
    sleep 30  # Wait for VM to boot
    ansible-playbook \
        -i "kafka-broker-01-new," \
        playbooks/deploy-kafka.yml \
        --extra-vars "broker_id=${FAILED_BROKER_ID} broker_rack=eastus2-az1"
    
    # 5. Health check
    sleep 30  # Wait for broker startup
    echo "[$(date)] Verifying broker health..."
    kafka-broker-api-versions.sh \
        --bootstrap-server kafka-broker-01-new:9092 \
        --bootstrap-server kafka-broker-02:9092
    
    # 6. Verify replication recovery
    for i in {1..30}; do
        under_replicated=$(kafka-topics.sh \
            --bootstrap-server kafka-broker-02:9092 \
            --describe | grep -c "Isr")
        if [ "$under_replicated" -eq 0 ]; then
            echo "[$(date)] All partitions fully replicated"
            break
        fi
        echo "[$(date)] Waiting for replication recovery... ($i/30)"
        sleep 10
    done
    
    echo "[$(date)] Broker replacement complete"
fi
```

#### Scenario 2: Regional Failure (RTO: 30 min, RPO: < 1 hour)

```bash
#!/bin/bash
# Manual regional failover procedure

PRIMARY_REGION="eastus2"
SECONDARY_REGION="westeurope"

echo "[$(date)] ===== REGIONAL FAILOVER PROCEDURE ====="

# 1. Verify primary region is truly down (not just network latency)
echo "[$(date)] Verifying primary region status..."
HEALTH_CHECK_ATTEMPTS=0
while [ $HEALTH_CHECK_ATTEMPTS -lt 5 ]; do
    if timeout 10 bash -c "curl -s https://kafka-broker-01.eastus2.azure.com:9092/health" > /dev/null 2>&1; then
        echo "[$(date)] Primary region responding - aborting failover"
        exit 1
    fi
    HEALTH_CHECK_ATTEMPTS=$((HEALTH_CHECK_ATTEMPTS + 1))
    sleep 60
done

echo "[$(date)] Primary region confirmed down after 5 minutes"

# 2. Verify secondary cluster health
echo "[$(date)] Verifying secondary cluster health..."
kafka-topics.sh \
    --bootstrap-server kafka-broker-04.westeurope.azure.internal:9092 \
    --describe

# 3. Check replication lag
echo "[$(date)] Checking replication lag..."
REPLICATION_LAG=$(kafka-mirrors \
    --bootstrap-server kafka-broker-04.westeurope.azure.internal:9092 \
    --describe | grep -o "lag: [0-9]*" | awk '{print $2}')

if [ "$REPLICATION_LAG" -gt 3600 ]; then  # 1 hour in seconds
    echo "[WARNING] Replication lag: ${REPLICATION_LAG} seconds - Data loss possible"
    read -p "Proceed with failover? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        exit 1
    fi
fi

# 4. Promote secondary cluster (stop mirrors, allow writes)
echo "[$(date)] Promoting secondary cluster..."
kafka-mirrors \
    --bootstrap-server kafka-broker-04.westeurope.azure.internal:9092 \
    --alter \
    --link primary-to-secondary \
    --stop

echo "[$(date)] Secondary cluster now accepting writes"

# 5. Update client configurations
echo "[$(date)] Updating producer/consumer configurations..."
# This should trigger automatic client failover via health checks
# Or manual update if automatic failover not configured

# 6. Monitor secondary cluster stability
echo "[$(date)] Monitoring secondary cluster stability for 5 minutes..."
for i in {1..30}; do
    kafka-broker-api-versions.sh \
        --bootstrap-server kafka-broker-04.westeurope.azure.internal:9092 \
        --bootstrap-server kafka-broker-05.westeurope.azure.internal:9092 \
        --bootstrap-server kafka-broker-06.westeurope.azure.internal:9092
    
    echo "[$(date)] Health check $i/30 - Secondary cluster stable"
    sleep 10
done

echo "[$(date)] ===== FAILOVER COMPLETE ====="
echo "[$(date)] All traffic now routing to West Europe"
echo "[$(date)] Action items:"
echo "  1. Update DNS records to point to secondary cluster"
echo "  2. Notify stakeholders of failover event"
echo "  3. Investigate primary region outage"
echo "  4. Begin recovery process when primary available"
```

#### Scenario 3: Cluster-Wide Restoration

```bash
#!/bin/bash
# Full cluster restoration from backups

BACKUP_DATE="2024-01-15"
BACKUP_CONTAINER="kafka-backups"

echo "[$(date)] ===== CLUSTER RESTORATION FROM BACKUP ====="

# 1. Provision new cluster infrastructure via Terraform
echo "[$(date)] Provisioning new cluster infrastructure..."
terraform apply -auto-approve

# 2. Wait for all VMs to boot
echo "[$(date)] Waiting for VMs to boot..."
sleep 120

# 3. Deploy Kafka software stack
echo "[$(date)] Deploying Kafka software..."
ansible-playbook playbooks/deploy-kafka.yml

# 4. Restore cluster metadata
echo "[$(date)] Restoring cluster metadata..."
az storage blob download-batch \
    --account-name kafkabackupsa \
    --source "metadata-backups/${BACKUP_DATE}" \
    --destination "./metadata-backups"

for broker_config in metadata-backups/broker-*-config-*.json; do
    # Parse and apply configuration to brokers
    BROKER_ID=$(echo $broker_config | grep -oP 'broker-\K[0-9]+')
    kafka-configs.sh \
        --bootstrap-server kafka-broker-${BROKER_ID}:9092 \
        --alter \
        --entity-type brokers \
        --entity-name ${BROKER_ID} \
        --from-file ${broker_config}
done

# 5. Restore topics from snapshot
echo "[$(date)] Restoring topics from backup..."
python3 << 'EOF'
import json
from datetime import datetime
from azure.storage.blob import ContainerClient

container = ContainerClient.from_connection_string(
    os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
    container_name='kafka-backups'
)

# List all topic backups from date
for blob in container.list_blobs(name_starts_with=f"kafka-backups/{BACKUP_DATE}"):
    if blob.name.endswith('.jsonl'):
        print(f"Restoring {blob.name}...")
        # Download and replay messages
        # (implementation details omitted for brevity)
EOF

# 6. Verify cluster health
echo "[$(date)] Verifying cluster health..."
kafka-topics.sh \
    --bootstrap-server kafka-broker-01:9092 \
    --describe

# 7. Run validation tests
echo "[$(date)] Running validation tests..."
ansible-playbook playbooks/validate-cluster.yml

echo "[$(date)] ===== RESTORATION COMPLETE ====="
```

---

## 8. Infrastructure as Code

### 8.1 Terraform + Ansible Hybrid Approach

**Rationale:** Terraform provisions Azure infrastructure (VMs, networking) while Ansible configures Kafka software (brokers, ZooKeeper, clients). This separation of concerns enables:

- Infrastructure repeatability (Terraform state)
- Configuration management (Ansible playbooks)
- Independent scaling of infrastructure vs. application
- Clear audit trails for infrastructure changes

### 8.2 Repository Structure

```
kafka-infrastructure/
├── terraform/
│   ├── main.tf                    # Primary configuration
│   ├── variables.tf               # Input variables
│   ├── outputs.tf                 # Outputs (IPs, FQDNs, etc.)
│   ├── terraform.tfvars           # Environment-specific values
│   ├── modules/
│   │   ├── networking/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── compute/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── monitoring/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   ├── backends/
│   │   └── remote-state.tf        # Azure Storage for state
│   └── .gitignore
├── ansible/
│   ├── playbooks/
│   │   ├── deploy-kafka.yml
│   │   ├── configure-replication.yml
│   │   ├── deploy-zookeeper.yml
│   │   └── validate-cluster.yml
│   ├── roles/
│   │   ├── kafka-broker/
│   │   │   ├── tasks/
│   │   │   ├── templates/
│   │   │   ├── handlers/
│   │   │   └── defaults/
│   │   ├── zookeeper/
│   │   └── monitoring/
│   ├── inventory/
│   │   ├── production
│   │   ├── staging
│   │   └── group_vars/
│   └── ansible.cfg
├── .github/workflows/
│   ├── deploy-infrastructure.yml
│   └── validate-code.yml
└── README.md
```

### 8.3 Implementation Approach

#### Phase 1: Foundation (Weeks 1-2)

1. Initialize Terraform project structure
2. Create core Azure modules (VNets, NSGs, VMs)
3. Set up remote state in Azure Storage
4. Create Ansible roles for Kafka broker setup
5. Test single-region deployment

#### Phase 2: Multi-Region (Weeks 3-4)

1. Extend Terraform modules for multi-region
2. Configure ExpressRoute and VNet peering
3. Create Ansible playbooks for MRC configuration
4. Test cross-region replication
5. Implement failover testing

#### Phase 3: Automation (Weeks 5-6)

1. Build GitHub Actions CI/CD pipeline
2. Implement automated testing
3. Add monitoring and alerting setup (Terraform-managed)
4. Create disaster recovery automation scripts
5. Security hardening and compliance validation

### 8.4 CI/CD Pipeline

```yaml
# .github/workflows/deploy-infrastructure.yml

name: Deploy Kafka Infrastructure

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'
      - 'ansible/**'
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Terraform Format Check
        run: terraform fmt -check -recursive
      
      - name: Terraform Validate
        working-directory: terraform
        run: terraform validate
      
      - name: TFLint
        uses: terraform-linters/setup-tflint@v3
      
      - name: Ansible Lint
        run: |
          pip install ansible-lint
          ansible-lint ansible/playbooks/

  plan:
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Terraform Plan
        working-directory: terraform
        run: |
          terraform init
          terraform plan -out=tfplan
      
      - name: Comment PR with Plan
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('terraform/tfplan', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '```\n' + plan.substring(0, 3000) + '\n```'
            });

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Terraform Apply
        working-directory: terraform
        run: |
          terraform init
          terraform apply -auto-approve
          terraform output -json > outputs.json
      
      - name: Deploy Kafka via Ansible
        run: |
          ansible-playbook \
            -i terraform/outputs.json \
            ansible/playbooks/deploy-kafka.yml \
            --vault-password-file vault.key
      
      - name: Run Post-Deployment Tests
        run: |
          ansible-playbook \
            ansible/playbooks/validate-cluster.yml
```

---

## 9. Operational Guidance

### 9.1 Capacity Planning

#### Sizing Formula

```
Cluster Throughput Capacity = Number of Brokers × Throughput per Broker

With Standard_D16s_v5 brokers on RAID 10:
  - Per-broker throughput: 1,000 MB/s (saturated)
  - 6-broker cluster: 6 GB/s aggregate

For typical workload:
  - Peak throughput: 200-500 MB/s
  - Headroom multiplier: 3-5×
  - Recommended cluster: 3-6 brokers
```

#### Scaling Procedures

**Vertical Scaling (Single Broker):**
1. Upgrade VM to larger size (Standard_E8s_v5)
2. Restart broker (controlled leadership transfer)
3. Monitor replication recovery
4. Repeat for each broker sequentially

**Horizontal Scaling (Add Brokers):**
1. Provision new broker VM via Terraform
2. Deploy Kafka software via Ansible
3. Broker auto-joins cluster
4. Rebalance partitions (optional, automated)
5. Monitor reassignment progress

```bash
# Trigger partition reassignment to new broker
kafka-reassign-partitions.sh \
    --bootstrap-server kafka-broker-01:9092 \
    --topics ".*" \
    --brokers "1,2,3,4,5,6,7" \
    --generate > reassignment.json

kafka-reassign-partitions.sh \
    --bootstrap-server kafka-broker-01:9092 \
    --reassignment-json-file reassignment.json \
    --execute
```

### 9.2 Maintenance Windows

#### Planned Maintenance Schedule

```
Window: Sunday 2:00-4:00 UTC (Off-peak window)
Duration: 2 hours (sufficient for rolling updates)

Process:
1. Notify stakeholders 1 week in advance
2. Perform maintenance on secondary region brokers first
3. Perform maintenance on primary region brokers
4. Run validation tests
5. Monitor metrics for 1 hour post-maintenance
```

#### Broker Rolling Restart

```bash
#!/bin/bash
# Graceful rolling restart for all brokers

for broker_id in {1..6}; do
    echo "Stopping broker $broker_id..."
    
    # Transfer leadership away from this broker
    kafka-broker-api-versions.sh \
        --bootstrap-server kafka-broker-${broker_id}:9092 \
        --describe
    
    # Stop broker
    systemctl stop confluent-kafka
    
    # Wait for leadership to stabilize
    sleep 30
    
    # Perform maintenance (update, config change, etc.)
    apt-get update && apt-get upgrade -y
    
    # Start broker
    systemctl start confluent-kafka
    
    # Wait for replication recovery
    while true; do
        isr=$(kafka-topics.sh \
            --bootstrap-server kafka-broker-$((broker_id % 6 + 1)):9092 \
            --describe | grep -c "Isr")
        if [ "$isr" -eq 0 ]; then
            break
        fi
        sleep 10
    done
    
    echo "Broker $broker_id restarted and recovered"
done

echo "Rolling restart complete"
```

### 9.3 Performance Tuning

#### JVM Tuning (For broker with 64 GB memory)

```bash
export KAFKA_HEAP_OPTS="-Xms16g -Xmx16g"
export KAFKA_JVM_PERFORMANCE_OPTS="
  -XX:+UseG1GC
  -XX:MaxGCPauseMillis=20
  -XX:InitiatingHeapOccupancyPercent=35
  -XX:G1NewCollectionThreads=8
  -XX:G1ReservedPercentage=10
  -Djava.awt.headless=true
  -XX:+DisableExplicitGC
"
```

#### OS-Level Tuning

```bash
# File descriptor limits
ulimit -n 100000

# TCP tuning
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.tcp.rmem='4096 87380 67108864'
sysctl -w net.tcp.wmem='4096 65536 67108864'

# Connection tuning
sysctl -w net.ipv4.tcp_max_syn_backlog=65536
sysctl -w net.core.netdev_max_backlog=65536

# Disk I/O tuning
sysctl -w vm.dirty_ratio=10
sysctl -w vm.dirty_background_ratio=5
```

### 9.4 Troubleshooting Guide

#### Symptom: High Producer Latency

**Investigation:**
```bash
# Check broker CPU/memory
top -p $(pgrep -f kafka.Kafka)

# Check disk I/O
iostat -x 1 10

# Check network saturation
iftop -p -i eth0

# Check replication lag
kafka-topics.sh --bootstrap-server kafka-broker-01:9092 --describe
```

**Common Causes & Fixes:**
- High CPU → Upgrade VM size or increase broker count
- High disk I/O → Enable SSD burst, check log compaction
- Network saturation → Upgrade ExpressRoute, enable compression

#### Symptom: Consumer Lag Growing

**Investigation:**
```bash
# Check consumer lag
kafka-consumer-groups.sh \
    --bootstrap-server kafka-broker-01:9092 \
    --group my-app-group \
    --describe

# Check broker throughput
jconsole localhost:9099  # JMX connection
# Look at BytesInPerSec, BytesOutPerSec

# Check for broker issues
kafka-broker-api-versions.sh --bootstrap-server kafka-broker-01:9092
```

**Common Causes & Fixes:**
- Consumer too slow → Increase consumers, optimize processing
- Broker bottleneck → Add brokers, upgrade storage
- Message size too large → Check message serialization

---

## 10. Conclusion

### Critical Success Factors

1. **Pre-Deployment Planning:** Understand requirements, design architecture before provisioning
2. **Testing:** Thoroughly test multi-region failover and recovery procedures
3. **Monitoring:** Implement comprehensive monitoring before going to production
4. **Documentation:** Maintain accurate runbooks and operational procedures
5. **Training:** Ensure operations team understands multi-region architecture and failure modes

### Recommended Next Steps

1. **Immediate:** Deploy to development environment, validate design
2. **Month 1:** Implement in staging with production-like workloads
3. **Month 2:** Deploy to production, enable monitoring/alerting
4. **Month 3-6:** Execute disaster recovery drills monthly, refine procedures

### Key Takeaways

- **MRC provides optimal balance** of latency, consistency, and operational automation for multi-region deployments
- **Role-based replication** (leaders, followers, observers) enables efficient use of remote regions
- **Terraform + Ansible** provides clear separation between infrastructure and application configuration
- **Comprehensive monitoring** is essential for operational confidence
- **Regular disaster recovery testing** validates procedures and builds team competency

This architecture and deployment guide provides a production-ready foundation for building enterprise-grade, multi-region Confluent Kafka clusters on Microsoft Azure. Success requires disciplined execution, continuous testing, and vigilant monitoring.

---

## Appendix: References and Resources

### Confluent Documentation
- [Confluent Platform Multi-Region Clusters](https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region.html)
- [Confluent Cloud on Azure](https://docs.confluent.io/cloud/current/clouds/azure.html)
- [Kafka Best Practices](https://docs.confluent.io/kafka/operations-tools/)

### Apache Kafka Documentation
- [Kafka Configuration Reference](https://kafka.apache.org/documentation/#configuration)
- [Rack-Aware Replica Placement](https://kafka.apache.org/documentation/#brokerconfigs_broker.rack)

### Microsoft Azure Documentation
- [Azure Virtual Machines Sizing](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/sizes)
- [Azure ExpressRoute Documentation](https://docs.microsoft.com/en-us/azure/expressroute/)
- [Azure Reliability - Regions and AZs](https://learn.microsoft.com/en-us/azure/reliability/)

### Tools and Technologies
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/)
- [Ansible Azure Modules](https://docs.ansible.com/ansible/latest/collections/azure/azcollection/)
- [Prometheus JMX Exporter](https://github.com/prometheus/jmx_exporter)

---

**Document Generated:** 2024  
**Status:** Production-Ready  
**Version:** 1.0  
**Maintainer:** Platform Engineering Team
