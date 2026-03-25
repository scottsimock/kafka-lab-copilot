---
id: TASK-3.2
title: GitHub Actions CI/CD Pipeline
status: To Do
assignee: []
created_date: '2026-03-25 19:33'
labels: []
dependencies:
  - TASK-3.1
references:
  - decision-0009
  - research-task-2.11
parent_task_id: TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create GitHub Actions workflows for PR-driven plan and merge-driven apply with manual approval gates. PR triggers terraform validate + terraform plan with plan output posted as PR comment. Merge to main triggers terraform apply with GitHub Environment manual approval gate. Configure service principal credentials as GitHub Secrets. Add Ansible execution step post-TF apply with separate approval gate. Branch protection rules: require PR review + passing plan. Output: .github/workflows/infra-plan.yml, .github/workflows/infra-apply.yml
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PR creation triggers plan workflow; plan output visible in PR comment
- [ ] #2 Merge triggers apply workflow; apply requires manual approval before execution
- [ ] #3 Ansible step follows apply with its own approval gate
- [ ] #4 Workflow fails cleanly on invalid Terraform
<!-- AC:END -->
