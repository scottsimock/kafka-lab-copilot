---
name: plan-phase
description: Generate a structured implementation epic for a specific phase (1-4) of the Confluent Kafka on Azure roadmap. Produces backlog-ready epics with implementation subtasks, testing subtasks, and a spike retrospective documentation task. Use when starting a new phase, when user says "plan phase", or when the orchestrator needs to decompose a phase into backlog tasks.
---

# Plan Phase

Generate a structured backlog epic for a phase of the Confluent Kafka on Azure implementation roadmap.

## Quick Start

Invoke with a phase number (1–4): `/plan-phase 2`

## Workflow

1. **Read phase number** from user input (1–4). If missing or invalid, ask for it.
2. **Load phase definition** from [REFERENCE.md](REFERENCE.md) for the requested phase.
3. **Check prior-phase debt** — if phase > 1, read the spike retrospective from the prior phase's completed epic. Incorporate any technical debt or remediations into the current phase's tasks.
4. **Determine epic number** — query the Backlog MCP for the next available epic ID.
5. **Generate the epic** with subtasks in three categories (in this order):

### Epic Structure

```
task-{epic}.1   — [IMPL] First implementation subtask
task-{epic}.2   — [IMPL] Second implementation subtask
...
task-{epic}.N   — [TEST] Testing & validation subtask(s)
task-{epic}.N+1 — [TEST] Integration / end-to-end validation
task-{epic}.N+2 — [DOC]  Spike retrospective documentation
```

**Prefixes** indicate subtask category:
- `[IMPL]` — Development / implementation work. Developer agent writes code, IaC, config, or automation.
- `[TEST]` — Testing & validation. Developer agent writes and runs tests to verify implementation works.
- `[DOC]`  — Documentation. Produces the spike retrospective as the final subtask of the epic.

6. **Present the epic** to the user for review and approval before creating backlog items.
7. **Create in Backlog MCP** once approved, following the orchestrator workflow.

## Subtask Requirements

### Implementation Tasks (`[IMPL]`)

Each implementation subtask must include:
- Clear objective and scope (what to build)
- File/directory outputs expected
- Acceptance criteria (verifiable conditions)
- References to relevant ADRs and research documents (see REFERENCE.md)
- Dependencies on other subtasks within this epic

### Testing Tasks (`[TEST]`)

Each testing subtask must include:
- What is being tested and how
- Test type: unit, integration, end-to-end, or smoke test
- Pass/fail criteria
- Dependency on the implementation subtask(s) it validates

### Spike Retrospective (`[DOC]`)

The final subtask of every epic. Produces a markdown document at `backlog/docs/spike-phase-{N}.md` containing:

1. **Phase Summary** — what was delivered
2. **What Worked** — successful approaches, tools, patterns
3. **What Didn't Work** — failed approaches, blockers encountered, workarounds applied
4. **Technical Debt** — items deferred, shortcuts taken, known issues
5. **Remediations for Next Phase** — specific action items to address debt
6. **Metrics** — tasks completed, tests passing, infrastructure state
7. **Decision Amendments** — any ADRs that need updating based on implementation experience

## Cross-Reference Rules

When generating subtasks, always link to:
- **ADRs**: Reference by ID (e.g., `decision-0007`) when a task implements or depends on a decision
- **Research docs**: Reference by task ID (e.g., `research-task-2.5`) when a task draws from research findings
- **Architecture guide**: Reference specific sections when implementing architecture patterns

See [REFERENCE.md](REFERENCE.md) for the full phase definitions, task breakdowns, decision mappings, and research cross-references.
