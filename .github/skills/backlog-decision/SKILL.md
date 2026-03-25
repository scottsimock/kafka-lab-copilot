---
name: backlog-decision
description: Help humans document architectural and design decisions using consistent templates with tags, rationale, and implementation notes. Agents can query decisions to understand code structure. Use when creating, documenting, searching, or retrieving software decisions that inform implementation.
---

# Backlog Decision

## Overview

Decisions are how teams capture **why** code is structured a certain way. This skill helps humans document decisions consistently so agents understand architectural choices and future teams know the reasoning.

Decisions are stored in the **Backlog MCP workspace** (`backlog://decisions`) and managed through both CLI commands and MCP resources.

**Key principle**: Only humans make decisions. Agents can ask "should we make a decision about X?" but humans decide.

## Quick start

When creating a decision, you will provide the following information:

**Required Fields:**
- **Title**: A clear, descriptive title for the decision
- **Status**: Proposed (for discussion) or Accepted (if already decided)
- **Date**: Today's date or when decision was made (YYYY-MM-DD format)
- **Tags**: Domain/team keywords for organization (comma-separated, kebab-case)

**Decision Content:**
- **Rationale**: Why this decision? (constraints, trade-offs, benefits)
- **Implementation notes**: How does this affect the code? (modules, patterns, deployment)

**Optional:**
- **Link to task**: Related backlog task ID that prompted this decision (e.g., `task-2.1`). Format: `task-{epic}.{task}` or leave blank to skip

Decisions are created and tracked through the **Backlog MCP** (`backlog://decisions`) and saved as markdown files with auto-generated IDs (decision-000X) and kebab-case filenames.

**Example workflow:**

For a decision on PostgreSQL usage:
- **Title**: "Use PostgreSQL for persistent storage"
- **Status**: Accepted
- **Date**: 2026-03-25
- **Tags**: database, infrastructure, backend
- **Linked Task**: task-2.1
- **Rationale**: PostgreSQL provides ACID transactions and JSONB support needed for payment processing. Team has existing experience. MongoDB was rejected due to lack of multi-document transactions.
- **Implementation Notes**: All database queries go through repository pattern in `src/repositories/`. Connection pooling via PgBouncer. Schema migrations use Flyway.

**Result**: `decision-0005-use-postgresql-for-persistent-storage.md` created and tracked in `backlog://decisions` with all metadata.

### Query decisions

Find decisions by tags or keywords:

```bash
backlog decision search --tag database
backlog decision search --tag backend,infrastructure
backlog decision search "caching strategy"
```

### View a decision

```bash
backlog decision view <decision-id>
```

## MCP Integration

### For Agents (Programmatic Access)

Agents can access decisions through the **Backlog MCP** at `backlog://decisions` for structured decision queries and integration.

**MCP Decision Resource**: `backlog://decisions`
- Returns all decisions in the backlog with metadata
- Enables agents to understand architectural constraints before implementation
- Provides decision history, status, tags, and linked tasks

**Common Agent Workflows**:

1. **Agent queries decisions by tag**:
   ```
   Agent needs to implement API error handling.
   Query: backlog://decisions with tag=api,error-handling
   Response: Returns all accepted decisions about API error responses
   ```

2. **Agent reads linked task context**:
   ```
   Agent is assigned task-2.3.
   Query: backlog://decisions where linked_task = task-2.3
   Response: Returns decisions that drove this task implementation
   ```

3. **Agent searches decision history**:
   ```
   Agent implementing caching needs to understand evolution.
   Query: backlog://decisions search "caching"
   Response: Returns all caching decisions (active + superseded)
   ```

**MCP Procedure**: `backlog/decision/search`
- Agents invoke this to search decisions programmatically
- Returns structured decision metadata without requiring CLI parsing
- Enables agent-to-agent decision discovery

### For Humans (Manual Creation & Management)

Humans create and manage decisions via CLI commands that write to the Backlog MCP workspace:

```bash
# Create decision (interactive prompt via backlog decision create "{title}")
backlog decision create "Use PostgreSQL for persistent storage"

# Search decisions by tag
backlog decision search --tag database

# Search decisions by keyword  
backlog decision search "caching strategy"

# View a specific decision
backlog decision view decision-0001
```

All decisions are automatically tracked in `backlog://decisions` and linked to tasks where applicable.

## Decision template

Every decision follows this structure (Markdown):

```markdown
# Decision: {Title}

**ID**: decision-{number}  
**Status**: Proposed | Accepted | Rejected | Deprecated | Superseded  
**Date**: YYYY-MM-DD  
**Tags**: comma-separated-labels  
**Linked Task**: task-{epic}.{task} (optional)

## Rationale

Why was this decision made? Include:
- Problem or constraint it addresses
- Trade-offs considered
- Why this choice over alternatives
- Key benefits or risks

## Implementation Notes

How does this affect the codebase?
- Which modules or systems are affected?
- Patterns to follow (e.g., "all database queries go through repository layer")
- Dependencies or constraints for other decisions
- Deployment or configuration implications

## Notes

Additional context, references, or future considerations.
```

## Decision lifecycle

**Status values** (only humans update):

- **Proposed**: Under discussion; not yet finalized
- **Accepted**: Approved and active; code should follow this
- **Rejected**: Decided against; historical record
- **Deprecated**: Was active, but no longer applicable
- **Superseded**: Replaced by newer decision (reference with `decision-{id}`)

Update status when circumstances change. **Never edit history**—supersede instead.

## Tagging strategy

Use flexible tags to organize decisions by team/domain. Examples:

- **Infrastructure**: `database`, `caching`, `messaging`, `deployment`, `cloud`
- **Backend**: `api`, `auth`, `validation`, `error-handling`, `logging`
- **Frontend**: `ui-framework`, `state-management`, `styling`, `accessibility`
- **Architecture**: `microservices`, `monolith`, `event-driven`, `async-processing`
- **Process**: `testing`, `ci-cd`, `code-review`, `documentation`

Create tags as needed; keep them kebab-case and descriptive.

## Workflows

### Document a new decision

1. Identify the decision (must be significant enough to affect code/architecture)
2. Run `backlog decision create "{title}"` with a clear, descriptive title
3. **Answer interactive prompts** for:
   - **Status**: Proposed (for discussion) or Accepted (if already decided)
   - **Date**: Today's date or when decision was made (YYYY-MM-DD)
   - **Tags**: Domain/team keywords for organization (comma-separated, kebab-case)
   - **Linked Task**: Related backlog task ID (e.g., task-2.3) or leave blank
4. **Provide content** for:
   - **Rationale**: Why this decision? Trade-offs? Alternatives considered?
   - **Implementation Notes**: How does code follow this? Modules? Patterns? Constraints?
5. Review the generated decision file (auto-named `decision-000X-{kebab-case-title}.md`)
6. Update status to `Accepted` when approved by stakeholders (edit the file directly)

**Key points:**
- Respond to all prompts—don't skip fields (tags and linked task can be blank)
- Be specific in rationale (cite constraints, trade-offs, alternatives)
- Make implementation notes actionable for future developers
- Once created, link decisions to task completion (bidirectional traceability)

### Query decisions before implementation

Agents use this to understand architectural constraints:

```bash
backlog decision search --tag database
```

Returns all decisions tagged with "database" so agents know how data persistence works.

### Supersede an outdated decision

1. Create a new decision with the new approach
2. Set old decision status to `Superseded by decision-{new-id}`
3. Both decisions remain for historical context

### Link decision to task

When documenting a decision, optionally link to the backlog task that prompted it:

```
**Linked Task**: task-1.2
```

This creates traceability between decisions and implementation work.

## Advanced features

See [REFERENCE.md](REFERENCE.md) for:
- Best practices for decision documentation
- When to make a decision vs. when to defer
- Common decision patterns
- Decision review checklist

## Integration with agents

### How Agents Access Decisions via MCP

Agents query decisions through the Backlog MCP to understand architectural constraints and implementation patterns:

**Agent Query Workflow**:
1. Agent is assigned a task (e.g., task-2.5)
2. Agent queries `backlog://decisions` to find relevant architectural choices
3. Search uses filters: linked task (task-2.5), tags (e.g., api, database), or keywords
4. Agent reads decision rationale and implementation notes
5. Agent implements task following the decision patterns

**Example Agent Queries**:
```
Agent: "What caching strategy have we decided on?"
  → Query: backlog://decisions with tag=caching, status=Accepted
  → Response: Returns decision-0006 (Use Redis for distributed session caching)
  → Agent reads implementation notes for Redis integration patterns

Agent: "What decisions affect this task?"
  → Query: backlog://decisions where linked_task = task-2.3
  → Response: Returns all decisions that prompted task-2.3
  → Agent aligns implementation with those architectural choices

Agent: "How should we handle database access?"
  → Query: backlog://decisions with tag=database,backend
  → Response: Returns decisions on repository pattern, connection pooling, migrations
  → Agent structures code to match those patterns
```

**MCP Procedure** used by agents:
```
backlog/decision/search
  Filters:
    - tag: <tag-name> or <tag1,tag2>
    - linked_task: <task-id> 
    - keyword: <search-term>
    - status: Proposed | Accepted | Rejected | Deprecated | Superseded
  Returns: Structured decision records with metadata
```

### How Agents Recommend (But Don't Create) Decisions

Agents can **identify when a decision is needed** but only humans create them:

```
Agent: "I'm implementing API error handling but found conflicting patterns. 
Should we create a decision about error response format?"
  → Human: "Yes, let me create that decision"
  → Human runs: backlog decision create "Standardize API error response format"
  → Human answers prompts (status, date, tags, linked task)
  → Human writes rationale and implementation notes
  → Decision is created in backlog://decisions, tracked by MCP
```

**Key rule**: Humans decide; agents recommend.

