# Backlog Decision Examples

## MCP Workflow Examples

### Example: Agent Decision Discovery via MCP

**Scenario**: Agent is assigned task-2.5 (implement Azure resource monitoring).

**Agent Workflow**:
1. Agent reads task-2.5 from `backlog://tasks`
2. Agent queries decisions linked to this task:
   ```
   Query: backlog://decisions where linked_task = task-2.5
   Response: [decision-0002, decision-0004]
   ```
3. Agent retrieves decision-0002 (Azure regional deployment):
   ```json
   {
     "id": "decision-0002",
     "title": "Azure regional deployment strategy",
     "status": "Accepted",
     "linked_task": "task-2.5",
     "tags": ["cloud", "deployment", "infrastructure"],
     "implementation_notes": "All resources use Azure availability zones..."
   }
   ```
4. Agent structures monitoring solution to align with multi-region strategy
5. Agent can search related decisions by tag:
   ```
   Query: backlog://decisions?tag=infrastructure
   Response: [decision-0001, decision-0002, decision-0004, ...]
   ```

**Result**: Agent discovers all architectural constraints before implementation.

---

### Example: Multi-Agent Decision Consistency

**Scenario**: Multiple agents working on related features need to stay consistent.

**Team Setup**:
- Agent A implements task-1.2 (user authentication)
- Agent B implements task-1.3 (session management)
- Both query `backlog://decisions?tag=auth` to find common patterns

**Decision Found** (decision-0003):
```markdown
# Decision: Use JWT for stateless authentication

**Status**: Accepted
**Tags**: auth, security, backend
**Implementation Notes**: 
- All API endpoints validate JWT in Authorization header
- Use RS256 algorithm for token signing
- Token expiration: 1 hour for access, 30 days for refresh
```

**Agent A** structures login to return JWT following this pattern.
**Agent B** structures session endpoints to validate JWT per this decision.

**Result**: Both agents implement compatible authentication without coordination errors.

---

### Example: Discovering Deprecated Decisions

**Scenario**: Agent searches for caching strategy and finds outdated decision.

**Agent Query**: `backlog://decisions?tag=caching`

**Results**:
- decision-0004: `Status: Superseded by decision-0006`
- decision-0006: `Status: Accepted` (Use Redis for distributed session caching)

**Agent Behavior**:
- Reads decision-0004 to understand why in-memory caching was rejected
- Reads decision-0006 to understand Redis requirements
- Implements using Redis (the active decision)
- Avoids the mistake that was made in production

**Result**: Historical context prevents re-learning the same lesson.

---

## Detailed Decision Examples

### Example 1: Technology Choice

```markdown
# Decision: Use PostgreSQL for persistent storage

**ID**: decision-001  
**Status**: Accepted  
**Date**: 2026-03-25  
**Tags**: database, infrastructure, backend  
**Linked Task**: task-1.2

## Rationale

We need a database for our e-commerce platform with two critical requirements:
- **Transactional integrity**: Payment processing must guarantee ACID compliance
- **Data flexibility**: We need to store JSON product attributes and user preferences

We considered:
- **PostgreSQL** (chosen): ACID transactions, JSONB support, full-text search, strong JSON handling. Team has existing experience. Cons: slightly more complex operations.
- **MySQL**: Simpler to operate, but weaker JSONB support and multi-transaction limitations for payments
- **MongoDB**: Flexible schema, but no multi-document ACID transactions (unacceptable for payments)
- **DynamoDB**: Fully managed, but vendor lock-in and cost escalation at our scale

PostgreSQL balances robustness, team expertise, and operational complexity.

## Implementation Notes

- All database queries go through the repository pattern (`src/repositories/`)
- Connection pooling via PgBouncer (config in `config/database.env`)
- Schema migrations use Flyway (`db/migrations/`)
- JSONB columns used for flexible attributes (see `schema.sql` for patterns)
- Backups automated via AWS RDS snapshots (handled by DevOps)
- Slow query logging enabled; queries >1s logged to monitoring system

## Notes

- If query performance becomes a bottleneck, revisit caching (decision-002) before considering other databases
- Replication and read replicas available if scaling read load
```

## Example 2: Architectural Pattern

```markdown
# Decision: Repository pattern for all database access

**ID**: decision-002  
**Status**: Accepted  
**Date**: 2026-03-25  
**Tags**: backend, architecture, testing  
**Linked Task**: task-1.3

## Rationale

Direct database access scattered across services makes testing hard and creates tight coupling to schema changes. By using the repository pattern, we:
- Abstract database details from business logic
- Make it easy to mock database calls in tests
- Centralize query logic for easier optimization
- Reduce coupling between services and schema

Alternatives considered:
- **No abstraction**: Simpler initially, but leads to scattered SQL and tight coupling (rejected due to testing complexity)
- **ORM only**: ORMs hide details but can create N+1 query problems and performance surprises (we use Prisma for repositories, so this is layered)

Repository pattern balances simplicity with testability and maintainability.

## Implementation Notes

- Every service has a corresponding repository in `src/repositories/{ServiceName}Repository.ts`
- Repositories wrap database calls and return domain objects (not raw rows)
- Repositories are dependency-injected; never instantiate directly
- Repository methods are high-level (e.g., `findUsersByStatus()`, not `SELECT * WHERE...`)
- See `src/repositories/UserRepository.ts` for reference implementation
- All tests mock repositories using Jest (`jest.mock('repositories')`)

## Notes

- When adding a new service, create its repository first (before implementing business logic)
```

## Example 3: Process Decision

```markdown
# Decision: All code changes require peer review before merge

**ID**: decision-003  
**Status**: Accepted  
**Date**: 2026-03-25  
**Tags**: process, code-review, quality  

## Rationale

Peer review catches bugs early, spreads knowledge across the team, and maintains code quality. Without it, we risk:
- Production bugs
- Knowledge silos (only one person understands a module)
- Inconsistent code style and patterns
- Missed edge cases

Every pull request must be reviewed by at least one other engineer before merge.

## Implementation Notes

- PRs require 1 approval from the team before merge
- Use GitHub PR review feature; leave detailed comments
- Authors must address all feedback (with discussion if needed)
- Approval signals that code is ready for production
- Urgency (hotfixes) doesn't skip review; it accelerates review

## Notes

- This builds team knowledge and prevents "single points of failure"
```

## Example 4: Superseded Decision

```markdown
# Decision: Use in-memory cache for session storage

**ID**: decision-004  
**Status**: Superseded by decision-006  
**Date**: 2026-03-01  
**Tags**: caching, session, deprecated  

## Rationale

[Original rationale...]

In-memory caching was fast and simple for development. However, in production with multiple servers, session data became inconsistent across instances, causing users to be logged out when requests routed to a different server.

## Implementation Notes

[Original implementation...]

## Superseded

This decision was superseded by decision-006 (Use Redis for distributed caching) when we discovered in-memory caching doesn't work in a multi-server deployment. Redis solves the consistency problem while maintaining performance.

---

# Decision: Use Redis for distributed session caching

**ID**: decision-006  
**Status**: Accepted  
**Date**: 2026-03-20  
**Tags**: caching, session, infrastructure  

## Rationale

In-memory caching (decision-004) caused session consistency issues across multiple servers. Redis is a distributed, in-memory store that all servers can access, ensuring session consistency while maintaining performance.

[Rest of decision...]
```

## Example 5: Decision Query Workflow (CLI)

**Agent asks**: "How should I structure API responses?"

**Human runs**:
```bash
backlog decision search --tag api
```

**Returns**:
- decision-007: Use versioned APIs
- decision-008: Standardized error response format
- decision-009: Use JSON for all responses

**Agent reads**:
```markdown
# Decision: Use versioned APIs

Status: Accepted
Rationale: Backward compatibility when APIs evolve
Implementation Notes: All endpoints start with /v1/... Use version in URL not headers.
```

Agent now knows to structure endpoints as `/v1/users` rather than `/v2/users`.

---

## Example 6: MCP Decision Queries (Agent Integration)

These are programmatic queries agents use when accessing the Backlog MCP:

### Query 1: Find decisions by linked task
```
Agent implementation task: task-2.5

MCP Query: 
  Resource: backlog://decisions
  Filter: linked_task = "task-2.5"

Response (JSON):
  [
    {
      "id": "decision-0002",
      "title": "Azure regional deployment strategy",
      "status": "Accepted",
      "tags": ["infrastructure", "cloud"],
      "linked_task": "task-2.5",
      "rationale": "...",
      "implementation_notes": "..."
    }
  ]

Agent action: Read and apply decision-0002 patterns
```

### Query 2: Find decisions by tag
```
Agent needs: "How should we implement logging?"

MCP Query:
  Resource: backlog://decisions
  Filter: tag IN ["logging", "backend"]
  Filter: status = "Accepted"

Response (JSON):
  [
    {
      "id": "decision-0008",
      "title": "Use structured logging with JSON format",
      "status": "Accepted",
      "tags": ["logging", "backend"]
    },
    {
      "id": "decision-0009", 
      "title": "Log all API errors with context",
      "status": "Accepted",
      "tags": ["logging", "api", "error-handling"]
    }
  ]

Agent action: Implement logging per both decisions (unified approach)
```

### Query 3: Find decisions by keyword and status
```
Agent searches: "database performance"

MCP Query:
  Resource: backlog://decisions
  Search: "performance"
  Filter: tag = "database"
  Filter: status IN ["Accepted", "Superseded"]

Response (JSON):
  [
    {
      "id": "decision-0005",
      "title": "Use PostgreSQL for persistent storage",
      "status": "Accepted",
      "tags": ["database", "infrastructure"],
      "implementation_notes": "Slow query logging enabled; queries >1s logged"
    },
    {
      "id": "decision-0010",
      "title": "Add query caching layer",
      "status": "Superseded by decision-0011",
      "superseded_by": "decision-0011"
    },
    {
      "id": "decision-0011",
      "title": "Use Redis for query result caching",
      "status": "Accepted",
      "tags": ["database", "caching"],
      "linked_task": "task-2.8"
    }
  ]

Agent action: 
  - Read why caching was needed (decision-0010)
  - Implement Redis caching per decision-0011
  - Follow database patterns in decision-0005
```

### Query 4: Validate decision exists before implementation
```
Agent implementing task: task-1.4 (error handling)

MCP Query:
  Resource: backlog://decisions
  ID: decision-0008

Response (JSON):
  {
    "id": "decision-0008",
    "status": "Accepted",
    "implementation_notes": "..."
  }

Agent behavior:
  IF decision found and status = "Accepted" → implement per spec
  IF decision found and status = "Proposed" → wait for approval
  IF decision not found → add to task notes: "Recommend creating decision about error responses"
```

---

## Summary

These examples show how decisions serve as a knowledge base that:
1. **Guides implementation** - Agents query decisions before writing code
2. **Ensures consistency** - Multiple agents follow the same patterns
3. **Preserves history** - Superseded decisions explain why changes were made
4. **Enables discovery** - Tags and keywords help find relevant decisions
5. **Tracks relationships** - Linked tasks show which decisions drove which work
6. **Integrates with backlog** - Decisions and tasks are bidirectionally linked in the MCP

All decision operations maintain traceability in `backlog://decisions` for agent discovery and team understanding.

