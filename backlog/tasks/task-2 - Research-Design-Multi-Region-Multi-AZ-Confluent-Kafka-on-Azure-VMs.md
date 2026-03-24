---
id: TASK-2
title: 'Research & Design: Multi-Region, Multi-AZ Confluent Kafka on Azure VMs'
status: To Do
assignee: []
created_date: '2026-03-23 22:25'
labels:
  - epic
  - research
  - kafka
  - azure
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Epic to research, design, and document best practices for deploying and operating Confluent Kafka clusters across multiple Azure regions and availability zones on virtual machines. This research directly supports a message-generation application that produces to multiple Confluent Kafka clusters spanning Azure regions and AZs. The goal is a comprehensive architecture and deployment guide — covering ZooKeeper topology, VM infrastructure, IaC automation, networking, security, MRC configuration, monitoring, DR, and producer client patterns — that will serve as the foundation for building the application.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All subtask research (TASK-2.1 through TASK-2.12) is completed and reviewed
- [ ] #2 A comprehensive architecture document is produced covering multi-region and multi-AZ topology
- [ ] #3 Deployment guide covers VM sizing, storage, networking, ZooKeeper, and Confluent configuration
- [ ] #4 IaC toolchain recommendation and approach is documented
- [ ] #5 Monitoring and disaster recovery strategies are documented
- [ ] #6 Multi-region producer client patterns and configuration are documented for the message-generation application
<!-- AC:END -->
