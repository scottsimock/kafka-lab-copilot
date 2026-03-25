---
name: backlog-decision
description: Create architecture decision records (ADRs) for the project. Use when you need to document a significant technical or design decision.
---

# Backlog Decision

Create and manage architecture decision records (ADRs) for documenting significant project decisions.

## Quick Start

1. Invoke the skill with a decision title or context
2. Answer prompted questions about status, rationale, and tags
3. Review the generated decision file in `backlog/decisions/`
4. Move approved decisions to `backlog/archive/decisions/` when finalized

## Workflow

**Step 1: Invoke with context**
Provide a clear decision title (e.g., "Use Confluent Enterprise for Kafka").

**Step 2: Agent guides through required fields**
- **Title**: Decision title (auto-filled from input)
- **Status**: Choose from Proposed, Accepted, Rejected, Superseded
- **Rationale**: Explain why this decision was made
- **Tags**: Comma-separated categories (e.g., infrastructure, database, architecture)

**Step 3: Agent asks for optional fields**
- **Linked Task**: Related backlog task ID (e.g., task-1.2)
- **Additional Sections**: Alternatives Considered, Consequences, Cost Implications, etc.

**Step 4: File generated**
Decision file created at: `backlog/decisions/decision-000#-{title-slug}.md`
- ID auto-generated sequentially
- Date auto-set to current date
- Frontmatter + markdown template applied

## Decision Status Values

- **Proposed**: Under discussion; not yet approved
- **Accepted**: Approved and active
- **Rejected**: Considered but rejected
- **Superseded**: Replaced by a newer decision

See REFERENCE.md for field descriptions and validation rules.
