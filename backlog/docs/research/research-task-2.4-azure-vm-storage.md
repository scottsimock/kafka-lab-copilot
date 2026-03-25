---
id: research-2.4
title: Azure VM Sizing and Storage Configuration
type: research
created_date: '2026-03-25 12:36'
updated_date: '2026-03-25 12:36'
---
# Azure VM Sizing and Storage Configuration for Confluent Kafka Brokers

**Task ID:** TASK-2.4  
**Epic:** Multi-Region Confluent Kafka Research on Azure  
**Date:** 2024  
**Status:** Research Documentation

---

## Executive Summary

This document provides comprehensive guidance on selecting Azure Virtual Machine SKUs and configuring storage for Confluent Kafka broker deployments. Kafka broker performance is fundamentally dependent on compute resources (CPU, memory, network bandwidth) and storage I/O characteristics. This research synthesizes industry best practices, Confluent's engineering recommendations, and Azure's infrastructure capabilities to deliver production-ready sizing guidance.

---

## 1. Recommended Azure VM SKUs for Kafka Brokers

### 1.1 General Sizing Principles

Kafka brokers require a balanced approach across three dimensions:
- **CPU cores:** 8-32 cores for production clusters (minimum 8 cores)
- **Memory:** 8-64 GB RAM (typically 1-2 GB per million messages/second of throughput)
- **Network:** 10+ Gbps network bandwidth (at least 10Gbps for production)

### 1.2 Recommended SKU Tiers

#### Entry-Level Brokers (Development/Testing)
- **SKU:** `Standard_D4s_v5` or `Standard_D4ds_v5`
  - vCPU: 4 cores
  - Memory: 16 GB
  - Network: 2 Gbps
  - Max Disk Throughput: Up to 500 Mbps (standard), 750 Mbps (with local SSD)
  - **Use Case:** Single-node development, Proof-of-Concept clusters, testing environments
  - **Typical Throughput:** 50-100 MB/s cluster throughput

#### Mid-Tier Brokers (Production - Small/Medium Scale)
- **SKU:** `Standard_D8s_v5` or `Standard_D8ds_v5` (Recommended)
  - vCPU: 8 cores
  - Memory: 32 GB
  - Network: 4 Gbps
  - Max Disk Throughput: 750 Mbps (standard), 1.2 Gbps (with local SSD)
  - **Use Case:** 3-5 broker production clusters, moderate throughput requirements
  - **Typical Throughput:** 200-500 MB/s cluster throughput
  - **Partition Target:** Up to 2,000-3,000 partitions per cluster

- **SKU:** `Standard_D16s_v5` or `Standard_D16ds_v5`
  - vCPU: 16 cores
  - Memory: 64 GB
  - Network: 8 Gbps
  - Max Disk Throughput: 1.2 Gbps (standard), 2.4 Gbps (with local SSD)
  - **Use Case:** 5-7 broker clusters, high-throughput requirements
  - **Typical Throughput:** 500-1000+ MB/s cluster throughput
  - **Partition Target:** Up to 5,000-8,000 partitions per cluster

#### High-Performance Brokers (Large-Scale Production)
- **SKU:** `Standard_E8s_v5`, `Standard_E16s_v5`, or `Standard_E32s_v5`
  - vCPU: 8, 16, or 32 cores
  - Memory: 64 GB, 128 GB, or 256 GB
  - Network: Up to 20 Gbps (E32s features accelerated networking)
  - Max Disk Throughput: 2-4 Gbps with appropriate disk configuration
  - **Use Case:** Large multi-broker clusters, extreme throughput/latency-sensitive workloads
  - **Typical Throughput:** 1000+ MB/s per broker
  - **Partition Target:** 8,000-15,000+ partitions per cluster
  - **Note:** E-series provides higher memory-to-vCPU ratio (4:1 vs 2:1 for D-series)

### 1.3 Memory Specifications Detail

Kafka memory allocation follows this pattern:
- **Heap Memory (JVM):** 8-16 GB (typically 50% of available memory)
- **OS Page Cache:** Remaining memory (critical for broker performance)
- **System Reserve:** 2-4 GB

**Example for D8s_v5 (32 GB total):**
```
Total Memory:        32 GB
JVM Heap:            12-16 GB
OS Page Cache:       14-16 GB
System Reserve:      2 GB
```

### 1.4 Network Specifications

Azure VM network specifications for Kafka:
- **Minimum Recommended:** 4 Gbps (Standard_D8s_v5 and above)
- **Optimal for High Performance:** 10+ Gbps (Enable Accelerated Networking)
- **Accelerated Networking:** Available on D16s_v5 and higher; provides ultra-low latency and consistent throughput

Enable Azure Accelerated Networking when available for:
- Reduced latency (microseconds vs milliseconds)
- Higher throughput ceiling
- Deterministic performance

---

## 2. Storage Configuration Options

### 2.1 Azure Managed Disk Types

#### Premium SSDs (Recommended for Kafka Brokers)
- **Disk Types:** P10 (128 GB) to P80 (32 TB)
- **Performance:** 
  - P30 (1 TB): 120 IOPS, 25 MB/s throughput, ~$10/month
  - P40 (2 TB): 500 IOPS, 100 MB/s throughput, ~$20/month
  - P50 (4 TB): 2,300 IOPS, 250 MB/s throughput, ~$40/month
  - P60 (8 TB): 5,000 IOPS, 500 MB/s throughput, ~$80/month
  - P80 (32 TB): 20,000 IOPS, 900 MB/s throughput, ~$300/month
- **SLA:** 99.99% availability
- **Best For:** Mission-critical Kafka brokers, high-throughput production environments
- **Recommended Sizing:** P50 or P60 for most production deployments

#### Standard SSDs
- **Disk Types:** E10 (128 GB) to E80 (32 TB)
- **Performance:** 
  - E30 (1 TB): 500 IOPS, 60 MB/s throughput, ~$3/month
  - E40 (2 TB): 500 IOPS, 60 MB/s throughput, ~$6/month
  - E50 (4 TB): 2,000 IOPS, 500 MB/s throughput, ~$12/month
- **SLA:** 99.9% availability
- **Best For:** Development, testing, non-critical workloads
- **Cost Advantage:** 70-80% cheaper than Premium SSDs

#### Ultra Disks
- **Performance:** Up to 160,000 IOPS, 4.5 GB/s throughput
- **Sizing:** 4 GB to 65 TB
- **Best For:** Extreme performance requirements, finance/trading workloads
- **Considerations:** Limited availability in some Azure regions; premium pricing

### 2.2 Storage Configuration for Kafka

#### Single Disk Configuration (Simpler)
- **Capacity:** 500 GB - 2 TB per broker depending on retention requirements
- **Recommended:** Premium SSD (P50 or P60)
- **Pros:** Simplicity, lower management overhead
- **Cons:** Single point of failure, limited throughput scaling
- **Use Case:** Development, smaller production clusters

**Sizing Formula:**
```
Disk Size = (Daily Ingestion GB × Retention Days) + 20% Buffer + Log Segment Overhead

Example:
- Daily Ingestion: 100 GB/day
- Retention: 7 days
- Disk Size = (100 × 7) × 1.2 = 840 GB minimum → Choose 1 TB (P50) disk
```

#### Multi-Disk RAID Configuration (Recommended for Production)

**RAID 10 (Striped + Mirrored) - Optimal for Kafka**
- **Disk Count:** 4-8 disks
- **Configuration:** 2 striped arrays, each mirrored
- **IOPS/Throughput:** Approximately 80-90% of all disks combined
- **Redundancy:** Survives single disk failure
- **Write Performance:** Slightly reduced due to mirroring
- **Use Case:** High-throughput production environments
- **Example (4-disk setup):**
  ```
  4 × Premium SSD P50 (4 TB each, 2,300 IOPS each)
  Total Capacity: 8 TB (RAID 10: ~4 TB usable)
  Total IOPS: ~9,200
  Total Throughput: ~1,000 MB/s
  ```

**RAID 0 (Striped) - Maximum Throughput**
- **Disk Count:** 4-8 disks
- **Configuration:** All disks striped together
- **IOPS/Throughput:** 100% of all disks combined
- **Redundancy:** None—single disk failure loses all data
- **Write Performance:** Maximum
- **Use Case:** Non-critical workloads, cached data scenarios
- **Example (4-disk setup):**
  ```
  4 × Premium SSD P50 (4 TB each, 2,300 IOPS each)
  Total Capacity: 16 TB
  Total IOPS: ~9,200
  Total Throughput: ~1,000 MB/s
  ```

**RAID 5 (Striped + Distributed Parity)**
- **Disk Count:** 3+ disks (typically 4-6)
- **IOPS/Throughput:** 70-80% of all disks combined (write penalty)
- **Redundancy:** Survives single disk failure
- **Write Performance:** Reduced due to parity calculations
- **Use Case:** Balanced cost/performance, good redundancy
- **Example (4-disk setup):**
  ```
  4 × Premium SSD P50 (4 TB each)
  Total Capacity: 12 TB (RAID 5: ~12 TB usable)
  Total IOPS: ~6,900 (write penalty applied)
  ```

### 2.3 Recommended Storage Architecture for Production Kafka

**Broker-Level Storage Setup:**
```
VM: Standard_D16s_v5 (16 vCPU, 64 GB memory)

Storage Configuration:
├── OS Disk
│   └── 128 GB Premium SSD (P10)
├── Kafka Broker Data
│   └── RAID 10 Array (4 × Premium SSD P60)
│       • Capacity: 32 TB (RAID 10 effective)
│       • Performance: ~20,000 IOPS, 2,000 MB/s
│       • Mounted at: /var/kafka/data
└── Logs/Indexes
    └── 512 GB Premium SSD (P30)
        • Mounted at: /var/kafka/log
```

**Cluster-Level (5-Node Broker Setup):**
```
Total Data Capacity: 5 × 8 TB = 40 TB usable
Total Throughput: 5 × 2,000 MB/s = 10,000 MB/s
Total IOPS: 5 × 20,000 = 100,000 IOPS
Cost: ~$35,000/month (with managed IPs, compute)
```

---

## 3. Sizing Methodology

### 3.1 Calculate Required Throughput

**Formula:**
```
Required Cluster Throughput (MB/s) = (Messages/sec × Avg Message Size) / (1024 × 1024)

Or, if working with records:
Required Throughput (MB/s) = (Records/sec × Avg Record Size) / (1024 × 1024)
```

**Example:**
```
Workload: 1 million messages/sec, average 1 KB per message
Required Throughput = (1,000,000 × 1 KB) / (1024 × 1024)
                    = (1,000,000 / 1,048,576) MB/s
                    ≈ 0.95 MB/s per broker

For 3-broker cluster: 0.95 × 3 ≈ 2.85 MB/s total (easily achievable)
```

### 3.2 Calculate Disk Space Requirements

**Formula:**
```
Total Disk Space = (Daily Ingestion Volume × Retention Days) × 1.2 + Log Overhead

Daily Ingestion Volume (GB) = (Messages/sec × 3600 × 24 × Avg Message Size) / (1024^3)
```

**Example (High-Throughput Scenario):**
```
Workload: 10 million messages/sec, 5 KB average, 7-day retention

Daily Ingestion:
= (10M/sec × 86,400 sec/day × 5 KB) / (1024^3)
= (4.32 × 10^12 KB) / (1,099,511,627,776 KB/GB)
≈ 3,932 GB/day (≈4 TB/day)

Total for 7 days:
= 4 TB/day × 7 × 1.2 (safety margin) = 33.6 TB

Per Broker (3-broker cluster):
= 33.6 TB / 3 ≈ 11.2 TB per broker
Recommendation: 16 TB effective storage (RAID 10 with 4 × 8 TB disks)
```

### 3.3 Partition Count Sizing

**Guideline:**
```
Partitions per Broker = Cluster Partitions / Number of Brokers

Recommended Maximums:
- Small Clusters (3 brokers): 500-1,000 partitions/broker
- Medium Clusters (5 brokers): 1,000-2,000 partitions/broker
- Large Clusters (7+ brokers): 2,000-3,000 partitions/broker

Hard Limit: 10,000-20,000 total partitions/cluster (depends on broker hardware)
```

**Example:**
```
Requirement: 5,000 total partitions for 50 topics
Cluster Size: 5 brokers

Partitions per broker: 5,000 / 5 = 1,000 partitions/broker
Memory overhead: ~500 KB per partition → 500 MB per broker
→ Well within acceptable range for D16s_v5
```

### 3.4 Memory Sizing for Brokers

**Formula:**
```
JVM Heap (GB) = 0.5 GB + (Throughput MB/s × 0.01)

Page Cache (GB) = (Total Partitions × 8 KB) + (Throughput MB/s × 100)
```

**Example (5,000 partition cluster, 500 MB/s throughput):**
```
JVM Heap = 0.5 + (500 × 0.01) = 5.5 GB
Page Cache Needed = (5,000 × 8 KB / 1024) + (500 × 100) = 50 GB

Total Memory Needed: ~60 GB
Recommended VM: Standard_D16s_v5 (64 GB) ✓
```

---

## 4. Performance Tuning Parameters

### 4.1 JVM Tuning

**Recommended JVM Settings for D16s_v5:**
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

### 4.2 Broker Configuration Tuning

**Critical Performance Parameters:**
```properties
# Network
num.network.threads=8
num.io.threads=8
socket.send.buffer.bytes=131072
socket.receive.buffer.bytes=131072
socket.request.max.bytes=104857600

# Log Segment Management
log.segment.bytes=1073741824  # 1 GB segments
log.flush.interval.messages=50000
log.cleanup.policy=retention

# Replication
min.insync.replicas=2
default.replication.factor=3

# Performance (for high-throughput scenarios)
compression.type=snappy
linger.ms=10
batch.size=32768
```

### 4.3 OS-Level Tuning

**Linux Kernel Parameters:**
```bash
# File descriptor limits
ulimit -n 100000

# TCP tuning
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.tcp.rmem = 4096 87380 67108864
net.tcp.wmem = 4096 65536 67108864

# Connection tuning
net.ipv4.tcp_max_syn_backlog = 65536
net.core.netdev_max_backlog = 65536

# Disk I/O
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
```

### 4.4 Storage Optimization

**Azure Disk Optimization:**
- Enable **Disk Caching:** Set to "Read/Write" for data volumes (be aware of durability implications)
- Use **Premium SSD** with **Bursting** enabled (temporary IOPS boost)
- Configure **RAID 10** for optimal balance of performance and reliability
- Monitor **Disk Latency:** Aim for < 5ms average latency

---

## 5. Cost Estimation

### 5.1 Example: Production 5-Broker Cluster

**Per Broker (Standard_D16s_v5 with RAID 10 storage):**
```
Compute:           $1.08/hour × 730 hrs/month = $788/month
OS Disk (128 GB):  $12/month
Data (RAID 10):    4 × P60 (8 TB) = $320/month (P60 ≈ $80/month each)
Network:           ~$50/month (data transfer)
─────────────────────────────────
Per Broker Total:  ~$1,170/month

5-Broker Cluster:  $1,170 × 5 = $5,850/month
```

### 5.2 Cost Optimization Strategies

| Strategy | Savings | Tradeoff |
|----------|---------|----------|
| Spot VMs | 60-70% | No SLA, can be terminated |
| Reserved Instances (1-yr) | 30-40% | Upfront commitment |
| Standard SSDs vs Premium | 70-80% | Lower I/O performance |
| On-demand (pay-per-month) | 0% | Highest hourly rate |

---

## 6. Implementation Checklist

- [ ] Select appropriate Azure VM SKU based on throughput requirements
- [ ] Calculate disk space needed using retention and ingestion rate
- [ ] Configure RAID 10 across 4-8 premium SSD drives
- [ ] Set up proper OS-level tuning (TCP, file descriptors, disk I/O)
- [ ] Configure JVM heap and G1GC parameters
- [ ] Enable Accelerated Networking if using D16s_v5 or higher
- [ ] Set up monitoring for disk latency, CPU utilization, and network throughput
- [ ] Perform capacity testing with expected workload
- [ ] Document baseline performance metrics
- [ ] Establish runbook for scaling storage/compute

---

## References

- Confluent Kafka on Azure Best Practices
- Azure Virtual Machines Pricing and Sizing Guide
- Kafka Performance Tuning Documentation
- RAID Configuration Best Practices for Distributed Systems

