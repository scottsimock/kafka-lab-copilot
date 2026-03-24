# Azure Networking Architecture for Multi-Region Confluent Kafka

**Research Document** | **TASK-2.5**  
**Focus:** VNet Design, Cross-Region Connectivity, Security, and Latency Optimization

---

## 1. VNet Architecture and Subnet Design

### 1.1 Multi-Region VNet Strategy

For a multi-region Confluent Kafka deployment on Azure, each region requires its own Virtual Network (VNet) with carefully designed subnets to ensure proper traffic isolation, security, and scalability.

#### Core Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Multi-Region Setup                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐            ┌──────────────────────┐ │
│  │  East US (Primary)  │            │  West Europe (DR)    │ │
│  │     VNet 1          │            │     VNet 2           │ │
│  │   10.0.0.0/16       │            │   10.1.0.0/16        │ │
│  └─────────────────────┘            └──────────────────────┘ │
│           │                                    │              │
│           └────────────────────────────────────┘              │
│           Global Peering / ExpressRoute                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Subnet Design for Kafka Cluster

Each regional VNet should implement the following subnet structure:

**Primary Region (East US - 10.0.0.0/16)**
- **Kafka Broker Subnet:** 10.0.1.0/24 (Hosts: 250 usable IPs)
- **Zookeeper Subnet:** 10.0.2.0/24 (High availability)
- **Client Subnet:** 10.0.3.0/24 (Producers/Consumers)
- **Management Subnet:** 10.0.4.0/24 (Confluent Control Plane, monitoring)
- **Gateway Subnet:** 10.0.5.0/27 (VPN/ExpressRoute gateway)

**Secondary Region (West Europe - 10.1.0.0/16)**
- Same structure with equivalent subnets for disaster recovery

### 1.3 Availability Zone Distribution

Within each region, deploy Kafka brokers across multiple Availability Zones (AZs):

```
East US Region (3 AZs)
├── AZ-1: Broker 1 (10.0.1.10)
├── AZ-2: Broker 2 (10.0.1.20)
└── AZ-3: Broker 3 (10.0.1.30)

West Europe Region (3 AZs)
├── AZ-1: Broker 4 (10.1.1.10)
├── AZ-2: Broker 5 (10.1.1.20)
└── AZ-3: Broker 6 (10.1.1.30)
```

This ensures that Kafka cluster resilience spans both physical and logical separation across availability zones, protecting against datacenter-level failures.

---

## 2. Cross-Region Connectivity Options

### 2.1 ExpressRoute (Recommended for Production)

**Azure ExpressRoute** provides dedicated, private connectivity with predictable performance and reliability.

**Advantages:**
- Dedicated bandwidth (1 Gbps to 100 Gbps)
- Low latency (typically <5ms between peered regions)
- Private connections—no internet exposure
- SLA-backed reliability (99.95% uptime)
- BGP dynamic routing support

**Configuration for Multi-Region Kafka:**

```yaml
ExpressRoute Circuit (Primary):
  Peering:
    - Private Peering: Enable
    - MS Peering: Disable (for this use case)
  Bandwidth: 50 Gbps
  SKU: Premium
  Provider: Equinix/Megaport
  
ExpressRoute Direct (Optional):
  - Direct port-based connectivity
  - Suitable for 10+ Gbps sustained Kafka throughput
  - Redundant circuits across different ExpressRoute locations
```

**Latency Profile:**
- Intra-region (same AZ): <1ms
- Cross-AZ (same region): 1-2ms
- Cross-region via ExpressRoute: 5-15ms (East US to West Europe)

### 2.2 VNet Peering (Global VNet Peering)

**Use Case:** Lower-cost alternative for non-critical Kafka mirror clusters or for development/test environments.

```
Primary VNet (10.0.0.0/16)
    ↓
Global VNet Peering
    ↓
Secondary VNet (10.1.0.0/16)

Characteristics:
- No bandwidth charges (intra-region transfers only charged)
- Cross-region peering charged per GB
- Transitive routing not supported natively
- ~10-20ms cross-region latency
```

**Benefits for Kafka:**
- Zero-bandwidth charges for intra-region traffic
- Simple configuration
- Built-in Azure redundancy

**Limitations:**
- User-defined routes (UDRs) required for complex topologies
- VPN failover not as robust as ExpressRoute

### 2.3 Site-to-Site VPN Gateway

**Use Case:** Cost-effective backup connectivity; suitable for failover scenarios or non-production environments.

```yaml
VPN Gateway Configuration:
  Type: RouteBased (recommended for high throughput)
  SKU: VpnGw3AZ (most reliable for Kafka)
  Throughput: 1.25 Gbps per tunnel
  Active-Active: Yes (dual redundancy)
  Custom IPsec Policy:
    IKEVersion: IKEv2
    EncryptionAlgorithm: AES256
    IntegrityAlgorithm: SHA256
    DHGroup: DHGroup14
    PFSGroup: PFS2048
```

**Latency Impact:** 15-30ms cross-region (variable due to encryption overhead)

**Note:** VPN is typically used as a backup to ExpressRoute, as it has higher latency and lower throughput than dedicated circuits.

### 2.3 Connectivity Decision Matrix

| Scenario | ExpressRoute | VNet Peering | VPN |
|----------|-------------|-------------|-----|
| Production Multi-Region | ✅ Yes | ⚠️ Optional | ❌ No |
| Latency Requirement (<10ms) | ✅ Best | ⚠️ Marginal | ❌ Poor |
| High Throughput (>500 Mbps) | ✅ Excellent | ✅ Good | ⚠️ Limited |
| Cost (for 10 TB/month transfer) | $$ High | $ Low | $ Moderate |
| Failover Capability | ✅ Excellent | ✅ Good | ✅ Good |
| Implementation Complexity | ⚠️ Moderate | ✅ Simple | ⚠️ Moderate |

---

## 3. Network Security Setup

### 3.1 Network Security Groups (NSGs)

Define ingress/egress rules per subnet:

**Kafka Broker Subnet NSG:**
```
Ingress Rules:
  - Port 9092 (Kafka plaintext): Allow from Client Subnet (10.0.3.0/24)
  - Port 9093 (Kafka TLS): Allow from Client Subnet, Peered VNets
  - Port 2181 (Zookeeper): Allow from Zookeeper Subnet (10.0.2.0/24)
  - Port 2888 (Zookeeper leader election): Allow from Zookeeper Subnet
  - Port 3888 (Zookeeper peer sync): Allow from Zookeeper Subnet
  - Port 22 (SSH): Allow from Management Subnet (10.0.4.0/24) only
  - Port 5671 (JMX): Allow from Management Subnet only

Egress Rules:
  - All traffic to Zookeeper Subnet (10.0.2.0/24)
  - All traffic to Client Subnet (10.0.3.0/24)
  - Allow DNS (53) to Azure DNS (168.63.129.16)
  - Allow HTTPS (443) for Azure services (updates, logs)
```

**Client Subnet NSG:**
```
Ingress Rules:
  - Port 9092/9093 (Kafka): Allow from Kafka Broker Subnet
  - Port 8086 (REST API): Allow from API Consumers
  - Port 22 (SSH): Allow from Management Subnet

Egress Rules:
  - Port 9092/9093: Allow to Kafka Broker Subnet (10.0.1.0/24)
  - Port 443 (HTTPS): Allow for schema registry, monitoring, logging
```

**Cross-Region Peering NSG:**
```
Ingress Rules:
  - Port 9092/9093: Allow from Peered VNet CIDR (10.1.0.0/16)
  - Port 2181, 2888, 3888: Allow Zookeeper replication from secondary region
  
Egress Rules:
  - All to secondary VNet (10.1.0.0/16) for bidirectional replication
```

### 3.2 Azure Firewall Deployment

For centralized, policy-based traffic inspection:

```
┌─────────────────────────────────────────────────┐
│         Azure Firewall (Premium SKU)             │
│  Threat Intelligence: On                         │
│  IDS/IPS Mode: Alert + Deny (High threat)        │
└─────────────────────────────────────────────────┘
         ↓                           ↓
┌──────────────────┐        ┌──────────────────┐
│  Kafka Brokers   │        │ External Network │
│  (Port 9092/93)  │        │   (via peering)  │
└──────────────────┘        └──────────────────┘

Firewall Rules:
  - Application Rules: FQDN filtering for external APIs
  - Network Rules: Kafka inter-broker (9092/9093)
  - NAT Rules: If exposing REST API externally (port 8086)
```

### 3.3 DDoS Protection

Enable Azure DDoS Protection Standard on public-facing endpoints:

```yaml
DDoS Protection Standard:
  Enabled: Yes
  Telemetry: On (Monitor attacks)
  Alerting: Yes
  Protected Resources:
    - Public IPs for VPN Gateway
    - Public IPs for REST API Gateway (if exposed)
  
  Mitigation Levels:
    - Layer 3/4: Automatic
    - Layer 7: Application Gateway WAF rules
```

### 3.4 Encryption in Transit

**TLS Configuration for Kafka:**
- Require TLS 1.2+ for all inter-broker communication
- Mutual TLS (mTLS) for broker authentication
- Certificate authority: Azure Key Vault or third-party CA

**IPsec for Cross-Region Traffic:**
- If using VNet Peering without ExpressRoute, enforce IPsec encryption
- Azure VPN gateway provides transparent encryption for site-to-site traffic

### 3.5 Private Endpoints (Optional but Recommended)

For schema registry, monitoring, and administrative access:

```
Private Link Service
    ↓
Schema Registry Private Endpoint (10.0.4.50)
Monitoring Private Endpoint (10.0.4.51)
    ↓
Direct DNS resolution to private IPs (no internet exposure)
```

---

## 4. Latency Optimization Strategies

### 4.1 Kafka Producer/Consumer Optimization

**Batching Configuration:**
```properties
# Producer (batch-before-sending reduces latency)
batch.size=32768
linger.ms=100  # Wait up to 100ms for batch

# Consumer (fetch batching)
fetch.min.bytes=1024
fetch.max.wait.ms=500
```

### 4.2 Network Path Optimization

**Route Traffic via Closest Peering Point:**
```
Use Azure Route Table with User-Defined Routes (UDRs):

Destination: 10.1.0.0/16 (Secondary VNet)
Next Hop Type: VirtualNetworkPeering
Next Hop: [Primary peering connection]
Priority: High
```

**Accelerated Networking (SR-IOV):**
- Enable on all VM NICs running Kafka brokers
- Reduces latency by bypassing Hyper-V virtual switch
- Supported VM sizes: D-series (v3+), E-series (v3+)
- Expected latency reduction: 40-50%

### 4.3 VM Placement Strategy

**Proximity Placement Groups (PPG):**
- Deploy Kafka brokers within the same PPG to minimize inter-broker latency
- Physical co-location in Azure datacenters reduces latency to <0.5ms

```yaml
Kafka Broker Deployment:
  Region: East US
  AvailabilityZone: 1, 2, 3
  ProximityPlacementGroup: kafka-ppg-east
  EnableAcceleratedNetworking: true
  VM SKU: Standard_D8s_v3 (8 vCPU, 32 GB RAM minimum)
```

### 4.4 Monitoring and Tuning

**Key Metrics to Monitor:**

| Metric | Target | Tool |
|--------|--------|------|
| End-to-end Latency (p99) | <50ms | Confluent Control Center |
| Network RTT (inter-broker) | <5ms | Azure Network Watcher |
| Packet Loss | <0.1% | Network Watcher, tcpdump |
| Jitter (latency variance) | <10ms | Application Performance Monitor |
| Throughput (inter-broker) | >900 Mbps | Network Performance Monitor |

**Remediation Actions:**
- If latency spikes: Check Azure capacity limits; scale to higher VM sizes
- If packet loss occurs: Verify NSG rules, check for MTU fragmentation (set to 1500)
- If throughput degraded: Enable jumbo frames (9000 MTU) on supported VMs

### 4.5 Azure ExpressRoute Circuit Quality

**For optimal latency, select circuits with:**
- Lowest hop count to reach peered regions
- Redundancy across multiple peering locations
- Consistent throughput (monitor via Azure Monitor)

**Example Circuit Configuration:**
```
Peering Location: Washington DC (for East US)
Bandwidth Guarantee: 50 Gbps reserved
Redundant Circuit Location: New York (failover location)
BGP Community Tags: Enable for traffic engineering
```

---

## 5. Recommended Architecture Summary

**Production Multi-Region Kafka on Azure:**

1. **Primary Region (East US):** 3-node Kafka cluster across 3 AZs, 10.0.0.0/16 VNet
2. **Secondary Region (West Europe):** 3-node mirror cluster, 10.1.0.0/16 VNet
3. **Connectivity:** ExpressRoute Premium (50 Gbps) with Global VNet Peering as backup
4. **Security:** NSGs + Azure Firewall + Private Endpoints; TLS for all inter-broker traffic
5. **Optimization:** Accelerated Networking + Proximity Placement Groups + SR-IOV NICs
6. **Monitoring:** Continuous latency/throughput tracking via Azure Monitor + Confluent Control Center

**Expected Performance:**
- Intra-region latency: <2ms (p99)
- Cross-region latency: <15ms (p99)
- Throughput: >8 Gbps aggregate
- Availability: 99.99% uptime SLA

---

## 6. Cost Considerations

| Component | Monthly Cost (Est.) | Notes |
|-----------|-------------------|-------|
| VMs (6 brokers, D8s_v3) | $1,440 | Per region |
| ExpressRoute (50 Gbps) | $2,200 | Dedicated circuit |
| Outbound Data Transfer | $500-2000 | Per 10 TB transferred cross-region |
| DDoS Protection Std | $3,000 | Annual; per VNet |
| **Total (Multi-Region)** | **~$7,000-9,000/month** | Scalable with broker count |

Use Azure Cost Calculator for precise estimates based on workload characteristics.

---

## References

- [Azure Virtual Network Documentation](https://learn.microsoft.com/en-us/azure/virtual-network/)
- [ExpressRoute Best Practices](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-best-practices)
- [Kafka Best Practices on Cloud](https://docs.confluent.io/kafka/operations-tools/)
- [Azure Firewall Policy Rules](https://learn.microsoft.com/en-us/azure/firewall/firewall-policy)
- [Azure Network Watcher Monitoring](https://learn.microsoft.com/en-us/azure/network-watcher/)

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Status:** Research Complete
