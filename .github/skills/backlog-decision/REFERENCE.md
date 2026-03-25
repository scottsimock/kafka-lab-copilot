# Decision Documentation Reference

## MCP Best Practices

### 1. Decisions are the Source of Truth in backlog://decisions

All decisions are tracked in the **Backlog MCP** at `backlog://decisions`. Every decision created via `backlog decision create` is automatically registered in the MCP workspace.

**What this means**:
- Agents query `backlog://decisions` to understand architectural constraints
- Decisions have structured metadata (ID, status, date, tags, linked tasks)
- Decision history is preserved (never delete; supersede instead)
- Decisions are discoverable by tag, keyword, linked task, and status

### 2. Link Decisions to Tasks for Full Traceability

When creating a decision, include the **Linked Task** field to connect architectural decisions to implementation work:

```markdown
**Linked Task**: task-2.3
```

This creates bidirectional traceability:
- **From decision → task**: Agents know which backlog task prompted this decision
- **From task → decision**: Developers know which architectural choices affect their task
- **MCP query**: Agents can search `backlog://decisions where linked_task = task-2.3` to find all related decisions

### 3. Use Tags for Agent Discovery

Tags are critical for agent queries. When creating a decision, assign tags that agents will search for:

```
Tags: database, infrastructure, backend
```

Agents will query:
```
backlog://decisions with tag=database
```

**Tag selection principle**: Choose tags that an agent implementing code would search for.

✅ **Good tags** (searchable, specific):
- `database`, `caching`, `api`, `auth`, `error-handling`, `logging`, `deployment`

❌ **Avoid** (too vague or redundant):
- `decision`, `misc`, `other` (not helpful for discovery)

### 4. Status Lifecycle in the MCP

Decisions flow through statuses that agents understand:

```
Proposed (discussion) → Accepted (active) → Superseded (historical) or Deprecated (retired)
```

**Agent behavior by status**:
- **Accepted**: Agent reads and follows implementation notes
- **Proposed**: Agent may refer to but shouldn't assume it's final
- **Superseded**: Agent reads old decision to understand history, but follows new decision
- **Rejected/Deprecated**: Agent may reference for historical context only

**Key rule**: Update status in the MCP when circumstances change. Never delete or edit old decisions.

### 5. Naming and ID Conventions Understood by MCP

**Decision File Format**:
```
decision-{four-digit-number}-{kebab-case-title}.md
```

**Examples** (as stored in backlog://decisions):
- `decision-0001-use-confluent-enterprise.md` → ID: decision-0001
- `decision-0002-azure-regional-deployment.md` → ID: decision-0002
- `decision-0005-use-postgresql-for-persistent-storage.md` → ID: decision-0005

The MCP auto-generates the next available ID when you run `backlog decision create`.

**Task Reference Format** (for Linked Task field):
```
**Linked Task**: task-{epic}.{task}
```

Examples:
- `**Linked Task**: task-2.3`
- `**Linked Task**: task-1.1`

The MCP validates that the linked task exists in `backlog://tasks`.

---

## Best Practices

### 1. Capture Real Context

A good rationale explains **why**, not just **what**:

**❌ Weak**:
> We decided to use PostgreSQL.

**✅ Strong**:
> We chose PostgreSQL because our e-commerce transactions require ACID compliance, and PostgreSQL's transactional integrity protects payment processing. We considered MySQL but it lacks robust multi-document transaction support. The team has existing PostgreSQL experience, reducing operational risk.

### 2. Document Implementation Implications

Link decisions to code patterns so agents know how to follow the decision:

**❌ Weak**:
> Use dependency injection for services.

**✅ Strong**:
> Use dependency injection for all service dependencies. Pattern: services receive dependencies via constructor; no global singletons. Implementation: use the `@Injectable()` decorator in the `services/` module. Affects: all new service files must follow this pattern. Exceptions must be approved via new decision.

### 3. One Decision Per Record

Each decision should address a single architectural choice, not multiple concerns.

**❌ Bundled** (hard to reference):
> Use PostgreSQL and implement caching with Redis

**✅ Separated**:
- Decision 1: "Use PostgreSQL for persistent storage"
- Decision 2: "Use Redis for session caching"

### 4. Record Trade-offs in Rationale

Show what was considered and why alternatives were rejected:

**Example**:
> **Rationale:**  
> We chose PostgreSQL over:
> - **MySQL**: Simpler but weaker JSONB support and less robust transaction handling
> - **MongoDB**: More flexible schema but lacks multi-document ACID guarantees (critical for payments)
> - **DynamoDB**: Fully managed, but vendor lock-in and higher cost at scale
> 
> PostgreSQL balances robustness, team familiarity, and cost.

### 5. Think About Consequences

What ripple effects does this decision create?

**Example**:
> **Implementation Notes:**  
> - All database operations must use the repository pattern (see `src/repositories/`)
> - Schema migrations use Flyway (see `migrations/` folder)
> - Backups are automated via AWS RDS snapshots (DevOps concern)
> - Connection pooling configured in `config/database.env`
> - Performance: queries over 1s are logged for monitoring

### 6. Use Status Lifecycle Correctly

**Proposed** → (discussion) → **Accepted** → (time passes) → **Deprecated** or **Superseded**

- Don't delete or edit old decisions in the MCP
- Supersede them to maintain history in `backlog://decisions`
- The full decision history tells the story of how the system evolved

### 7. Tag for Team Organization and Agent Discovery

Use tags so the right people and agents find relevant decisions:

**For backend team**: `database`, `api`, `auth`, `logging`  
**For frontend team**: `ui-framework`, `state-management`, `styling`  
**For infra team**: `deployment`, `cloud`, `monitoring`, `security`  
**For agents**: Tags help queries like `backlog://decisions with tag=database` return relevant decisions

Tags make decisions discoverable via the Backlog MCP.

## When to Make a Decision

Not every choice needs a decision record. Make a decision when:

✅ **It affects multiple parts of the codebase** (e.g., "use repository pattern")  
✅ **It's expensive to change later** (e.g., "use PostgreSQL" vs "use MongoDB")  
✅ **It influences other decisions** (e.g., "async processing with message queues")  
✅ **New team members need to understand why** (e.g., "authentication via JWT, not sessions")  
✅ **It represents a trade-off between valid alternatives** (e.g., "monolith vs. microservices")

❌ **Skip decisions for**: minor naming conventions, temporary workarounds, routine implementation details

## Decision Review Checklist

Before marking a decision as `Accepted`:

- [ ] **Rationale is clear**: Why this choice? What alternatives were considered?
- [ ] **Implementation notes exist**: How should code follow this decision?
- [ ] **Tags are assigned**: Can it be found by the right teams?
- [ ] **Linked task** (if applicable): Does it reference the backlog task that triggered it?
- [ ] **One decision per record**: Is it focused on a single concern?
- [ ] **Status is appropriate**: Proposed for discussion, Accepted for active decisions
- [ ] **Consequences are considered**: What ripple effects will this have?

## Common Decision Patterns

### Pattern: Technology Choice

**Template:**
```
# Decision: Use [Technology] for [Purpose]

**Rationale**: Why [Technology]? What alternatives? Trade-offs?

**Implementation Notes**: 
- How is it configured?
- Where in the codebase does it apply?
- What patterns must be followed?
- Dependencies or constraints?

**Example**: Use PostgreSQL for persistent storage
```

### Pattern: Architectural Style

**Template:**
```
# Decision: [Style] for [Component]

**Rationale**: Benefits, constraints, alternatives considered.

**Implementation Notes**:
- Design pattern and naming conventions
- Where this applies vs. doesn't apply
- When/how to deviate (if ever)

**Example**: Repository pattern for all database access
```

### Pattern: Process or Convention

**Template:**
```
# Decision: [Process] for [Activity]

**Rationale**: Why this process? What problem does it solve?

**Implementation Notes**:
- Step-by-step workflow
- Tools and automation
- Responsibilities and approval gates

**Example**: All code changes require peer review before merge
```

## Querying Decisions

### By agents during implementation

Agents search for decisions related to their task:

```
"I need to implement payment processing. What decisions affect this?"
→ Search: --tag payments, --tag auth, --tag database
→ Returns 3+ decisions about payment-related choices
```

### By humans during planning

Humans search to understand current architectural stance:

```
"Do we have a logging strategy?"
→ Search: --tag logging
→ Returns decision on logging framework and patterns
```

### By new team members for onboarding

New hires read decisions to understand "why the code is this way":

```
"Why are we using PostgreSQL?"
→ Search: decision-001
→ Reads rationale: ACID for transactions, team experience, etc.
```

## Superseding a Decision

When circumstances change and a decision is no longer valid:

1. **Create a new decision** with the updated choice
2. **Update old decision status** to `Superseded by decision-{new-id}`
3. **Keep both** for historical context

**Example**:

```markdown
# Decision: Use Redis for caching (Superseded)

**Status**: Superseded by decision-0005

**Superseded by**: decision-0005 - Use Memcached for caching

...original decision content...
```

**Why keep history?** Future teams understand why the original choice was made and why it was replaced. This prevents "decision churn" (re-arguing the same choice repeatedly).

## Integration with Backlog MCP

Decisions are integrated into the Backlog MCP for seamless agent access and task traceability:

### MCP Resource: backlog://decisions

All decisions are stored in the Backlog MCP workspace under `backlog://decisions` and are queryable by:
- **ID**: `backlog://decisions/decision-0001`
- **Tag**: `backlog://decisions?tag=database`
- **Linked Task**: `backlog://decisions?linked_task=task-2.3`
- **Status**: `backlog://decisions?status=Accepted`
- **Keyword search**: `backlog://decisions?search=caching`

### Bidirectional Traceability

Link decisions to backlog tasks for full context:

**In Decision file** (`backlog/decisions/decision-0007-use-versioned-apis.md`):
```markdown
**Linked Task**: task-2.3
```

**In Backlog task** (`backlog/tasks/task-2.3.md`):
```markdown
## Implementation Notes
Must follow decision-0007 (Use versioned APIs) for all API endpoints.
See: ../decisions/decision-0007-use-versioned-apis.md
```

**How agents use this**:
1. Agent is assigned `task-2.3`
2. Agent queries: `backlog://decisions where linked_task = task-2.3`
3. Agent retrieves decision-0007 with rationale and implementation notes
4. Agent structures code to match the API versioning decision

### Superseding Decisions in the MCP

When a decision becomes outdated:

1. Create a new decision with the updated choice
2. Update old decision status to `Superseded by decision-{new-id}`
3. Both remain in `backlog://decisions` for historical context

**Example**:
```markdown
# Decision: Use in-memory cache for session storage (SUPERSEDED)

**ID**: decision-004  
**Status**: Superseded by decision-006  
**Superseded By**: decision-006 - Use Redis for distributed session caching

[Original rationale and implementation notes...]
```

**Agent impact**:
- Agents querying with `status=Accepted` won't find the old decision
- Agents searching by keyword "caching" find both (can see the evolution)
- Agents following decision-006 use Redis, not in-memory caching

### Workflow: Creating a Decision Tracked by MCP

```bash
# Step 1: Create decision (adds to backlog://decisions)
backlog decision create "Use PostgreSQL for persistent storage"

# Step 2: Answer interactive prompts
Status: Accepted
Date: 2026-03-25
Tags: database,infrastructure,backend
Linked Task: task-2.1

# Step 3: Write rationale and implementation notes

# Result: decision-0005-use-postgresql-for-persistent-storage.md created
# and automatically tracked in backlog://decisions MCP resource
```

All operations use the Backlog MCP to maintain consistency and enable agent discovery.

