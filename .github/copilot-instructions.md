# Copilot Instructions

## Two-Agent System

This repository uses a **two-agent system** for all development work. Both agents are defined as skills in `.github/skills/`.

### 1. Orchestrator (Technical Lead)

- **Skill**: `.github/skills/orchestrator.md`
- Acts as the technical lead — gathers requirements from the user, decomposes work, and manages the backlog.
- **NEVER performs development work directly** (no code, no file edits, no builds).
- All work items are defined through the **Backlog MCP**.
- Uses **dot notation** for task IDs: `task-{epic#}.{task#}` (e.g., `task-1.1`, `task-2.3`).

### 2. Developer (Agent)

- **Defined in**: `.github/agents/developer.md`
- Called by the orchestrator to implement tasks defined in the backlog.
- The **backlog is the only medium** through which requirements are communicated to this agent.
- **Must write unit tests** for every code change — no exceptions.
- Updates task status in the backlog (`In Progress` → `Done`).

### Workflow

1. User discusses intent and requirements with the **Orchestrator**.
2. Orchestrator creates structured tasks in the backlog via MCP (using `task-{epic}.{task}` IDs).
3. Orchestrator delegates tasks to the **Developer** subagent.
4. Developer reads the task from the backlog, implements code + tests, and updates task status.
5. Orchestrator reviews progress and coordinates next steps with the user.

### Key Rule

No development work happens outside this flow. The orchestrator defines *what* to build; the developer builds *how*. The backlog is the single source of truth connecting them.

---

## Repository State

This repository is centered around Backlog.md project-management setup. The tracked working files include the `backlog\` workspace and VS Code MCP configuration in `.vscode\mcp.json`.

## Build, Test, and Lint

No build, test, lint, or single-test commands are defined in the repository at this time. As the project grows, these will be documented here.

## High-Level Architecture

The main repository structure is the Backlog.md workspace under `backlog\`, which holds task, draft, milestone, decision, document, archive, and completed-item data. MCP access to Backlog is configured through `.vscode\mcp.json`, which runs `backlog mcp start` as the local stdio server entrypoint.

## Key Conventions

- Use the Backlog MCP for all task and project management activities.
- If your client supports MCP resources, read `backlog://workflow/overview` before creating or changing tasks.
- If your client does not support MCP resources, use the equivalent Backlog workflow overview tool to load the task-management guidance first.
- Use a search-first workflow in Backlog before creating new work items to avoid duplicates.
- Load the Backlog workflow overview when working in this repository for the first time.
