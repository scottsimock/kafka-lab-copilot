# Monitoring, Observability, and Disaster Recovery for Confluent Kafka on Azure

**Document**: Research Task 2.8  
**Epic**: Multi-region Confluent Kafka on Azure  
**Date**: 2024  
**Status**: Completed

## Executive Summary

This document provides comprehensive guidance on implementing monitoring, observability, and disaster recovery strategies for multi-region Confluent Kafka deployments on Microsoft Azure. It covers key metrics, Azure Monitor integration, distributed tracing, logging, and DR procedures with defined RTO/RPO targets.

---

## 1. Key Kafka Metrics and JMX/Prometheus Monitoring

### 1.1 Critical Kafka Metrics

Confluent Kafka exposes critical metrics through multiple channels. Key metrics to monitor include:

**Broker-Level Metrics:**
- **UnderReplicatedPartitions**: Partitions with fewer in-sync replicas than configured
- **OfflinePartitionsCount**: Number of partitions with no available leader
- **ActiveControllerCount**: Number of active controllers (should always be 1)
- **LeaderElectionRateAndTimeMs**: Leader election frequency and duration
- **BytesInPerSec / BytesOutPerSec**: Throughput metrics for ingress and egress
- **FetchConsumerTotalTimeMs**: Consumer fetch latency
- **ProduceLocalTimeMsMax**: Producer latency on leader broker

**Topic/Partition Metrics:**
- **MessageBytesInPerSec**: Inbound message rate
- **ReplicaLagBytesMax**: Maximum replica lag across all partitions
- **ReplicationLatencyMs**: Replication delay metrics
- **ISRShrinkRate / ISRExpandRate**: In-sync replica membership changes

**Consumer Metrics:**
- **ConsumerLagSumPerSecond**: Total lag across consumer groups
- **ConsumerFetchLatencyAvgMs**: Consumer fetch latency
- **CommitLatencyMs**: Offset commit latency

### 1.2 JMX and Prometheus Integration

**JMX Export Configuration:**
Confluent Kafka includes built-in JMX metrics. Enable JMX export by configuring:

```properties
# server.properties
metrics.num.samples=100
metrics.sample.window.ms=30000
```

**Prometheus Integration:**
Deploy Prometheus with the JMX Exporter sidecar on Kafka brokers:

```yaml
# prometheus-jmx-config.yml
lowercaseOutputName: true
lowercaseOutputLabelNames: true
whitelistObjectNames:
  - "kafka.broker:*"
  - "kafka.controller:*"
  - "kafka.server:*"
  - "kafka.network:*"
```

Configure Prometheus to scrape Kafka brokers:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets:
          - 'kafka-broker-1:9090'
          - 'kafka-broker-2:9090'
          - 'kafka-broker-3:9090'
    relabel_configs:
      - source_labels: [__address__]
        regex: '([^:]+)(?::\d+)?'
        replacement: '${1}:9999'
        target_label: __param_target
```

**Metrics Retention:**
- Store Prometheus metrics for 15 days minimum in primary region
- Archive historical metrics to Azure Blob Storage for long-term analysis
- Retention policy: 30 days in hot tier, 90 days in cool tier

---

## 2. Azure Monitor Integration and Alerting

### 2.1 Azure Monitor Connectivity

**Architecture:**
- Deploy Azure Monitor agent on Kafka broker VMs
- Enable VM Insights for performance monitoring
- Configure Azure Log Analytics workspace for centralized logging
- Link Confluent Cloud metrics via Azure EventHubs integration

**Configuration Steps:**
1. Create Log Analytics workspace in each Azure region
2. Install Azure Monitor Agent (AMA) on Kafka VMs
3. Configure data collection rules (DCR) to collect Prometheus metrics
4. Set up cross-region log aggregation to primary Log Analytics workspace

**Metrics Stream:**
```
Kafka Metrics → JMX/Prometheus → Azure Monitor Agent → Log Analytics
```

### 2.2 Critical Alerting Rules

**Alert Configuration (in Log Analytics KQL):**

```kusto
// Alert: Broker Down
Perf
| where ObjectName == "kafka.broker"
| where CounterName == "ActiveControllerCount"
| summarize by Computer
| where todouble(CounterValue) == 0
| project Computer, AlertSeverity="Critical"

// Alert: Partition Under-Replicated
KafkaMetrics
| where metric_name == "UnderReplicatedPartitions"
| where metric_value > 0
| summarize max_lag=max(metric_value) by broker_id
| where max_lag > 0
| project AlertSeverity="High"

// Alert: Consumer Lag Spike
KafkaMetrics
| where metric_name == "ConsumerLag"
| summarize current_lag=avg(metric_value) by consumer_group
| where current_lag > 100000
| project consumer_group, AlertSeverity="Warning"

// Alert: Replication Latency
KafkaMetrics
| where metric_name == "ReplicationLatencyMs"
| summarize p99_latency=percentile(metric_value, 99) by broker_id
| where p99_latency > 5000
| project broker_id, AlertSeverity="High"
```

**Alert Action Groups:**
- **Critical**: PagerDuty escalation, SMS to on-call
- **High**: Email to platform team, Teams webhook
- **Warning**: Slack notification, internal ticketing

**Alert SLO Targets:**
- Alert notification delivery: < 1 minute
- Alert routing: < 2 minutes
- On-call response: < 15 minutes (SLA)

---

## 3. Distributed Tracing and Logging Strategies

### 3.1 Distributed Tracing Architecture

**OpenTelemetry Integration:**
- Instrument producer/consumer applications with OpenTelemetry SDK
- Export traces to Azure Application Insights
- Correlate traces across services using W3C Trace Context

**Trace Propagation:**
```
Producer App → [W3C TraceID] → Kafka Message Headers → Consumer App
```

**Sampling Strategy:**
- Head-based sampling: 10% of traces in production
- Tail-based sampling: 100% for high-latency requests (> 5s)
- Error sampling: 100% of failed traces

### 3.2 Comprehensive Logging Strategy

**Log Levels and Collection:**

| Log Type | Source | Destination | Retention | Sample Rate |
|----------|--------|-------------|-----------|------------|
| Broker Logs | Kafka brokers | Log Analytics | 90 days | 100% |
| Application Logs | Producer/Consumer | App Insights | 30 days | 100% |
| Audit Logs | Access/Auth events | Log Analytics | 365 days | 100% |
| Performance Logs | Prometheus/PerfMon | Log Analytics | 30 days | 100% |
| Debug Logs | Development VMs | Local storage | 7 days | 50% |

**Log Aggregation Configuration:**
```
Broker Logs (syslog) → Fluent Bit → Event Hubs → Log Analytics
```

**Correlation Strategy:**
- Use correlation ID header in all requests
- Include broker ID, partition, and offset in logs
- Link logs to metrics via timestamp and labels
- Query template for tracing a message end-to-end:

```kusto
let trace_id = "abc123def456";
union 
  (KafkaProducerLogs | where CorrelationId == trace_id),
  (KafkaMessageLogs | where CorrelationId == trace_id),
  (KafkaConsumerLogs | where CorrelationId == trace_id)
| sort by TimeGenerated asc
```

---

## 4. Disaster Recovery: Procedures and RTO/RPO Targets

### 4.1 RTO and RPO Targets by Failure Scenario

| Failure Scenario | RTO | RPO | Strategy |
|------------------|-----|-----|----------|
| Single broker failure | 5 min | 0 msg | ISR replication |
| Single region outage | 30 min | < 1 hour | Cross-region failover |
| Data center failure | 1 hour | < 2 hours | Cluster backup + restore |
| Catastrophic failure | 4 hours | < 4 hours | Secondary cluster activation |

### 4.2 Disaster Recovery Runbook

**Scenario 1: Single Broker Failure (RTO: 5 min, RPO: 0)**

*Detection:*
- Alert: Broker unreachable for 60 seconds
- OfflinePartitionsCount > 0
- ActiveControllerCount != 1

*Recovery Steps:*
1. Automated health check script validates broker cannot be reached
2. If unrecoverable: terminate instance, scale up replacement
3. New broker joins cluster, receives replicated data from other replicas
4. Wait for ISR recovery (typically 2-3 minutes)
5. Validate all partitions have min.insync.replicas met
6. Notify stakeholders when leader elections stabilize

**Scenario 2: Regional Outage (RTO: 30 min, RPO: < 1 hour)**

*Prerequisites:*
- Standby Kafka cluster in secondary region (warm standby)
- Cross-region mirroring enabled via MirrorMaker 2
- Consumer group offsets synced across regions

*Recovery Steps:*
1. Detect region outage: health checks fail for all brokers in primary region
2. Promote secondary cluster to primary (1-2 minutes)
   ```bash
   ./promote-cluster.sh --cluster secondary --new-role primary
   ```
3. Update producer/consumer connection strings to secondary (5 minutes)
4. Activate emergency service endpoints (via Azure Traffic Manager)
5. Monitor replication lag to identify synced topics
6. Verify data consistency for critical topics (10-15 minutes)
7. Begin gradual traffic migration (5 minutes)
8. Complete cutover validation (5 minutes)

**Scenario 3: Data Corruption / Accidental Deletion (RTO: 4 hours, RPO: < 24 hours)**

*Prerequisites:*
- Daily snapshots of critical topics to Azure Data Lake
- Backup retention: 30 days

*Recovery Steps:*
1. Identify affected topic and time range from logs
2. Verify data integrity in backup snapshot
3. Create new recovery topic from backup
4. Replay messages to original topic from recovery topic
5. Validate topic data integrity with hash verification
6. Communicate status to downstream consumers

**Scenario 4: Complete Cluster Loss (RTO: 1-2 hours, RPO: < 4 hours)**

*Prerequisites:*
- Automated backup to Azure Blob Storage (daily)
- Terraform IaC for cluster provisioning
- Configuration stored in Git repository

*Recovery Steps:*
1. Alert triggered: all brokers unreachable
2. Initiate cluster rebuild in alternate region using Terraform
3. Restore cluster metadata from latest backup
4. Restore topic configuration and partition assignments
5. Replay topic data from Azure Data Lake backups
6. Validate cluster health and metrics
7. Redirect producers/consumers to new cluster

### 4.3 Backup and Recovery Infrastructure

**Backup Strategy:**
- **Cluster Metadata**: Daily export to Azure Blob Storage + Git versioning
- **Topic Data**: Continuous replication to secondary region via MirrorMaker 2
- **Consumer Offsets**: Real-time sync to __consumer_offsets backup topic
- **Configuration**: Infrastructure-as-Code in Terraform + Git tracking

**Restore Validation:**
```bash
# Verify restored cluster matches backup
./validate-cluster-restore.sh \
  --backup-config $BACKUP_CONFIG \
  --restored-cluster $NEW_CLUSTER_ID \
  --topics $(cat critical-topics.txt)
```

**Testing Cadence:**
- Monthly DR drills simulating regional failover
- Quarterly full cluster rebuild testing
- Annual disaster recovery game days with all stakeholders

---

## 5. Monitoring Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Region 1 (Primary)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │   Broker 1   │      │   Broker 2   │      │   Broker 3   │   │
│  │  +JMX Port   │      │  +JMX Port   │      │  +JMX Port   │   │
│  └──────────────┘      └──────────────┘      └──────────────┘   │
│         │                     │                     │             │
│         └─────────────────────┴─────────────────────┘             │
│                          │                                         │
│                ┌─────────▼─────────┐                              │
│                │  Prometheus       │                              │
│                │  (Metrics Scrape) │                              │
│                └─────────┬─────────┘                              │
│                          │                                         │
│            ┌─────────────┴──────────────┐                         │
│            │                            │                         │
│     ┌──────▼──────┐           ┌─────────▼────────┐                │
│     │ Azure Mon   │           │  App Insights    │                │
│     │ Agent (AMA) │           │ (Tracing/Logs)   │                │
│     └──────┬──────┘           └─────────┬────────┘                │
│            │                            │                         │
│            └────────────┬───────────────┘                         │
│                         │                                         │
│              ┌──────────▼─────────┐                              │
│              │ Log Analytics      │                              │
│              │ Workspace          │                              │
│              └──────────┬─────────┘                              │
│                         │                                         │
│              ┌──────────▼─────────┐                              │
│              │  Alert Rules       │                              │
│              │  (KQL Queries)     │                              │
│              └──────────┬─────────┘                              │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                   ┌──────▼──────┐
                   │ Action Group │
                   │ (PagerDuty,  │
                   │  Slack, SMS) │
                   └─────────────┘
```

---

## 6. Key Recommendations

1. **Automation**: Implement self-healing broker replacement and automated failover
2. **Testing**: Execute monthly DR drills and capture lessons learned
3. **Alerting Hierarchy**: Establish clear escalation paths (Warning → High → Critical)
4. **Cross-Region Sync**: Maintain hot standby cluster with < 1 hour RPO
5. **Documentation**: Keep runbooks updated and accessible to on-call engineers
6. **Capacity Planning**: Monitor metrics trends to predict capacity needs 60 days ahead
7. **Cost Optimization**: Archive cold metrics to blob storage after 30 days

---

## 7. Implementation Checklist

- [ ] Deploy Prometheus with JMX exporter on all brokers
- [ ] Configure Log Analytics workspace in primary and secondary regions
- [ ] Set up 5 critical alert rules in Azure Monitor
- [ ] Implement OpenTelemetry tracing in producer/consumer applications
- [ ] Configure Fluent Bit for log aggregation
- [ ] Deploy MirrorMaker 2 for cross-region replication
- [ ] Create automated backup jobs to Azure Blob Storage
- [ ] Develop and test failover playbook
- [ ] Schedule monthly DR drill
- [ ] Document on-call escalation procedures

---

## Conclusion

Comprehensive monitoring and disaster recovery strategies are essential for maintaining high availability and data integrity in multi-region Kafka deployments. By implementing the architectures, metrics, and procedures outlined in this document, organizations can achieve industry-standard RTO/RPO targets while maintaining operational visibility and enabling rapid incident response.
