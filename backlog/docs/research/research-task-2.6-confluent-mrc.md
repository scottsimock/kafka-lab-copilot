---
id: research-2.6
title: Confluent Multi-Region Clusters
type: research
created_date: '2026-03-25 12:36'
updated_date: '2026-03-25 12:36'
---
# Research Document: Confluent Multi-Region Clusters (MRC)

**Task ID:** TASK-2.6  
**Topic:** Confluent Multi-Region Clusters Configuration, Replication, and Observer Replicas  
**Date:** 2025

---

## Executive Summary

Confluent Multi-Region Clusters (MRC) enable organizations to stretch a single Kafka cluster across multiple geographic regions or data centers, providing enhanced availability, disaster recovery capabilities, and optimized data locality. MRC introduces the concept of observer replicas alongside traditional leaders and followers, enabling asynchronous replication without sacrificing write performance or durability guarantees. This research document covers MRC architecture, replication strategies, cluster linking, and operational best practices for Azure-based deployments.

---

## 1. MRC Architecture and Components

### 1.1 Overview

Multi-Region Clusters extend a single Kafka cluster across physical boundaries, allowing brokers in different regions to coordinate and replicate data while maintaining a unified cluster view. This architecture enables organizations to deploy applications closer to their data and consumers, reducing latency and cross-region bandwidth costs.

### 1.2 Broker Roles in MRC

MRC introduces three distinct broker roles that work together to enable multi-region deployment:

#### Leaders
- Handle all write operations and coordinate with replicas
- Maintain authoritative state for assigned partitions
- Responsible for acknowledging producer writes based on ISR configuration
- Typically placed in the primary or nearest region to producers

#### Followers (In-Sync Replicas)
- Part of the In-Sync Replica (ISR) set
- Keep up with leader in near real-time, acknowledging writes
- Eligible for automatic failover and leader election
- Must maintain synchronization to remain in ISR
- Suitable for critical partitions requiring durability

#### Observer Replicas
- Unique to Confluent Platform MRC
- Replicate data asynchronously without participating in ISR by default
- Do not acknowledge producer writes or delay write acknowledgments
- Can be automatically promoted to ISR during failover scenarios
- Ideal for remote regions where low write latency is critical
- Allow local consumers to read from nearby replicas, reducing cross-region traffic

### 1.3 Replica Placement Strategy

Typical MRC deployments follow this pattern:

```
Topic: critical-events (Replication Factor: 4)
├── Region 1 (US-East)
│   ├── Leader (Broker 1)
│   └── Follower (Broker 2)
├── Region 2 (US-West)
│   ├── Observer (Broker 3)
│   └── Observer (Broker 4)
```

This configuration ensures:
- Strong write durability within Region 1 (primary region)
- Read locality in Region 2 through observer replicas
- Data is asynchronously replicated to Region 2
- Minimal impact on write latency for cross-region deployments
- Rapid failover capability without sacrificing consistency

### 1.4 Network and Infrastructure Requirements

- **Regional Connectivity:** Low-latency, high-throughput network links between regions
- **Broker-to-Broker Communication:** All brokers must communicate with each other for cluster coordination
- **Zookeeper/KRaft Coordination:** Distributed coordination service must be accessible across all regions
- **DNS Resolution:** Consistent DNS across regions enabling broker discovery
- **Firewall Rules:** Allow inter-broker communication on configured ports (typically 9092 for clients, 9093 for inter-broker)

---

## 2. Replication Policies and Observer Replicas

### 2.1 Replication Models

#### Synchronous Replication (RPO = 0)
- Producers set `acks=all` to receive acknowledgment only when all followers acknowledge
- Messages are only committed after reaching quorum across regions
- Provides zero data loss guarantee (RPO = 0)
- Best for mission-critical topics
- Trade-off: Increased write latency due to cross-region round trips
- Configuration: `min.insync.replicas` set appropriately for multi-region quorum

#### Asynchronous Replication (with Observers)
- Producers can use `acks=1` or `acks=leader_and_isr`
- Messages committed to leader before followers acknowledge
- Data flows to observers without delaying acknowledgments
- Reduced write latency and network congestion
- Accepts minimal data loss risk during regional failures
- Suitable for non-critical, high-frequency topics

### 2.2 Observer Promotion Policies

Observer replicas can transition to ISR membership under configured conditions:

#### `under-min-isr` Policy
- Automatically promotes observers when ISR size falls below `min.insync.replicas`
- Ensures topic remains available during broker failures
- Reduces manual intervention during degraded scenarios
- Example: If ISR requires 2 replicas and one fails, observer is promoted to maintain min.insync.replicas=2

#### `under-replicated` Policy
- Promotes observers when the partition becomes under-replicated
- Maintains desired replication factor across the cluster
- Slower promotion than `under-min-isr` but less aggressive

#### Manual Promotion
- Administrators can manually promote observers through administrative APIs
- Useful for controlled failover scenarios
- Allows validation before promotion

### 2.3 Configuration Example

```json
{
  "version": 2,
  "replicas": [
    {
      "count": 1,
      "constraints": {
        "rack": "us-east-1a"
      }
    },
    {
      "count": 1,
      "constraints": {
        "rack": "us-east-1b"
      }
    }
  ],
  "observers": [
    {
      "count": 1,
      "constraints": {
        "rack": "us-west-2a"
      }
    },
    {
      "count": 1,
      "constraints": {
        "rack": "us-west-2b"
      }
    }
  ],
  "observerPromotionPolicy": "under-min-isr"
}
```

### 2.4 min.insync.replicas Configuration

The `min.insync.replicas` (minIsr) setting determines how many in-sync replicas must acknowledge writes:

- **minIsr=2 (Recommended for critical topics):** Requires acknowledgment from leader + 1 follower before write commits
- **minIsr=3:** Maximum durability; requires 2 followers to acknowledge (all must be in same region typically)
- **Observer Impact:** Observers do not count toward minIsr unless promoted
- **Latency Consideration:** Higher minIsr values increase write latency; balance with durability requirements

---

## 3. Cluster Linking Configuration

### 3.1 Cluster Linking Overview

Cluster Linking is Confluent's native feature for bi-directional, topic-level replication across clusters. It complements MRC by enabling:

- Cross-cluster (and cross-region) topic replication
- Active-passive or active-active architectures
- Automated failover scenarios
- Offset preservation and topic metadata synchronization

### 3.2 Cluster Linking Modes

#### Source Cluster Configuration
```
# Configure source cluster authorization
sasl.enabled.mechanisms=PLAIN
security.protocol=SASL_SSL
```

#### Destination Cluster Link Creation
1. Establish bidirectional connection between clusters
2. Define replication direction (unidirectional or bidirectional)
3. Configure consumer group IDs and offset translation
4. Set replication factor for mirrored topics

### 3.3 Integration with Observer Replicas

While Cluster Linking operates at the cluster level and observers at the partition level, they work synergistically:

- **Cluster Linking** mirrors entire topics between clusters for DR
- **Observer Replicas** optimize replication within a stretched cluster for latency reduction
- Combined approach: Primary cluster uses MRC with observers; secondary cluster replicates via Cluster Linking
- Failover scenario: Applications reconnect to secondary cluster where Cluster Linking has maintained topic replicas

### 3.4 Configuration Example

```yaml
# Cluster Linking source configuration
source_cluster:
  bootstrap_servers: "broker1.us-east.azure.internal:9092,broker2.us-east.azure.internal:9092"
  client_id: "cluster-link-producer"
  
# Destination cluster link configuration  
destination_cluster:
  bootstrap_servers: "broker1.us-west.azure.internal:9092,broker2.us-west.azure.internal:9092"
  cluster_link_name: "us-east-to-us-west"
  topic_filters: ["app-events", "transactions", "customer-data"]
  consumer_group_offset_sync: true
```

---

## 4. MRC Operational Best Practices

### 4.1 Disaster Recovery Strategy

#### Define Recovery Objectives
- **RPO (Recovery Point Objective):** Decide acceptable data loss
  - Critical systems: RPO = 0 (use synchronous replication)
  - Non-critical systems: RPO can be minutes/hours
  
- **RTO (Recovery Time Objective):** Define acceptable downtime
  - Enable automated failover for RTO < 1 minute
  - Implement observer promotion policies for rapid ISR restoration

#### Architecture Patterns

**Active-Passive MRC:**
- Primary region handles all traffic
- Secondary region receives asynchronous replicas via observers
- Failover manually triggered or via health monitoring
- Simpler operational model, lower cost

**Active-Active with Cluster Linking:**
- Both regions accept traffic simultaneously
- Cluster Linking maintains bi-directional topic replication
- Requires application-level conflict resolution
- Higher complexity but improved availability

### 4.2 Configuration Management

- **Centralized Configuration:** Use Infrastructure-as-Code (Terraform, Kubernetes) for consistent configuration across regions
- **Topic Configuration:** Document and version control topic replica placement policies
- **Broker Configuration:** Ensure identical broker configurations across regions to prevent split-brain scenarios
- **Schema Registry Coordination:** Deploy Schema Registry in both regions with active replication

### 4.3 Monitoring and Observability

Key metrics to monitor:

```
- Replication Lag: Observer replica lag should remain < 1s
- ISR Changes: Alert on unexpected ISR shrinkage
- Cross-Region Latency: Baseline and alert on > 100ms variance
- Network Throughput: Monitor cross-region bandwidth utilization
- Broker Availability: Track broker health across all regions
- Consumer Lag: Monitor consumer group offsets in both regions
```

Recommended tools:
- Confluent Control Center for centralized monitoring
- Prometheus + Grafana for custom metrics
- Azure Monitor for infrastructure-level observability

### 4.4 Testing and Validation

1. **Failover Drills:** Regularly simulate region failures to validate failover procedures
2. **Chaos Testing:** Kill brokers, introduce network latency to test resilience
3. **Offset Translation Validation:** Verify consumers can resume without data loss after failover
4. **Application-Level Testing:** Test applications' ability to reconnect and resume operations

### 4.5 Operational Procedures

#### Normal Operation
- Monitor replication lag and ISR membership
- Document any anomalies or manual interventions
- Regularly review and optimize observer promotion policies

#### Failover Procedure
1. Detect failure through monitoring/alerting
2. Verify secondary region health and replication status
3. Execute client failover (update bootstrap servers)
4. Promote observer replicas to ISR if necessary
5. Monitor convergence and stability
6. Document root cause and timeline

#### Failback Procedure
1. Verify primary region recovery and stability
2. Check replication status from secondary to primary
3. Gradually migrate clients back to primary region
4. Demote promoted observers back to observer status
5. Validate cluster state and replication lag

### 4.6 Capacity Planning

- **Compute:** Each region should have sufficient broker capacity for independent operation
- **Storage:** Account for replication overhead and observer replicas consuming disk space
- **Network:** Budget for cross-region replication bandwidth
  - Synchronous replication: 2x traffic (acknowledgments)
  - Observer replication: 1x traffic (asynchronous)
- **Latency Budget:** Inter-region latency impacts write performance; plan network accordingly

### 4.7 Security Considerations

- **Inter-Broker Communication:** Encrypt broker-to-broker traffic with mTLS
- **Client Authentication:** Implement consistent authentication across regions
- **Access Control:** Use ACLs to restrict cross-region operations
- **Network Isolation:** Segregate cluster network traffic from application traffic
- **Audit Logging:** Enable and centralize audit logs for compliance tracking

### 4.8 Common Pitfalls and Mitigations

| Pitfall | Cause | Mitigation |
|---------|-------|-----------|
| **Offset Translation Issues** | Consumer offsets diverge during failover | Implement offset translation logic; test failover procedures |
| **Replication Loops** | Bidirectional replication creates cycles | Unidirectional Cluster Linking; careful topology design |
| **Network Congestion** | Insufficient cross-region bandwidth | Use observer replicas to reduce synchronous replication |
| **Split Brain** | Inconsistent configuration across regions | Centralized IaC; validation before deployment |
| **Excessive Observer Promotion** | Aggressive promotion policy causes cascading failures | Tune promotion policy; implement gradual promotion |

---

## 5. Azure-Specific Considerations

### 5.1 Regional Deployment

- Leverage Azure regions with low inter-region latency (< 50ms)
- Use Azure ExpressRoute for dedicated, high-bandwidth cross-region connectivity
- Deploy Confluent Platform on Azure VMs or AKS (Managed Kubernetes)

### 5.2 Availability Zones

- Within each Azure region, distribute brokers across 3 availability zones
- Combine AZ redundancy with region redundancy for defense in depth

### 5.3 Network Architecture

- Virtual Network Peering between regions
- Network Security Groups (NSGs) to control inter-region traffic
- Azure Private Endpoints for cluster-internal communication
- Azure Load Balancer for client connection distribution

---

## Conclusion

Confluent Multi-Region Clusters provide a robust foundation for building resilient, globally distributed event streaming platforms. By leveraging observer replicas, strategic replica placement, and cluster linking, organizations can achieve sub-second replication latency while maintaining strong durability guarantees. Success with MRC requires careful planning of network infrastructure, comprehensive monitoring, regular failover testing, and clear operational procedures. When deployed on Azure with proper configuration and operational discipline, MRC enables mission-critical event streaming architectures with true business continuity guarantees.

---

## References

- Confluent Documentation: Multi-Region Clusters Configuration
- Confluent Documentation: Cluster Linking Guide
- Tutorial: Multi-Region Clusters on Confluent Platform
- Multi-Region Kafka using Synchronous Replication for Disaster Recovery
- Disaster Recovery for Multi-Datacenter Apache Kafka Deployments
- Confluent Cloud Multi-Region Active-Active Patterns
