# Backlog Decision - Reference

## Field Specifications

### Required Fields

| Field | Format | Notes |
|-------|--------|-------|
| **ID** | `decision-000#` | Auto-generated sequentially (e.g., decision-0005) |
| **Title** | String, max 100 chars | Clear, specific decision statement |
| **Date** | YYYY-MM-DD | Auto-set to current date |
| **Status** | Proposed \| Accepted \| Rejected \| Superseded | Controls file location (see below) |
| **Rationale** | Markdown text | Explain drivers, constraints, alternatives considered |
| **Tags** | Comma-separated lowercase | Categorize decisions (e.g., infrastructure, database, architecture) |

### Optional Fields

| Field | Format | Notes |
|-------|--------|-------|
| **Linked Task** | task-{epic}.{task} | Reference backlog task (e.g., task-1.2) |
| **Alternatives Considered** | Markdown text | Document rejected options and why |
| **Consequences** | Markdown text | Document impact, trade-offs, and follow-on work |
| **Cost Implications** | Markdown text | Budget, resource, or licensing impacts |
| **Security Considerations** | Markdown text | Security risks, mitigations, compliance notes |
| **Implementation Notes** | Markdown text | How to apply this decision in code/infrastructure |

## File Naming Convention

```
decision-{id}-{slugified-title}.md
```

**Rules:**
- ID: `decision-0001`, `decision-0002`, etc.
- Title slug: lowercase, hyphens separate words, no special characters
- Example: `decision-0005-use-confluent-enterprise-for-kafka.md`

## File Location

- **Active decisions** (Proposed, Accepted): `backlog/decisions/`
- **Archived decisions** (Rejected, Superseded): `backlog/archive/decisions/`

## Frontmatter Template

```yaml
---
id: decision-000#
title: Decision Title
date: YYYY-MM-DD
status: Proposed | Accepted | Rejected | Superseded
tags: tag1, tag2, tag3
linked_task: task-#.# (optional)
---
```

## Validation Rules

The agent enforces:
1. ✓ Title must be non-empty and <100 characters
2. ✓ Status must be one of: Proposed, Accepted, Rejected, Superseded
3. ✓ Rationale must be non-empty
4. ✓ Tags must be lowercase, hyphenated words
5. ⚠ Linked task ID format checked (warns if not found in backlog, but allows override)
6. ✓ ID auto-generated; filename slugified correctly

## Example Decision

See `backlog/archive/decisions/decision-0001-use-confluent-enterprise.md` for a complete approved decision.
