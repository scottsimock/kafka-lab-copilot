# kafka-lab-copilot

An AI-assisted development environment for building Kafka-based solutions, powered by a two-agent GitHub Copilot system with integrated backlog management.

## Overview

This repository uses a **two-agent system** to manage and implement all development work:

- **Orchestrator** — acts as the technical lead; gathers requirements, decomposes work into tasks, and manages the backlog via the Backlog MCP.
- **Developer** — implements tasks defined in the backlog, writes unit tests, and updates task status.

The backlog is the single source of truth. No development work happens outside this flow.

## Repository Structure

```
kafka-lab-copilot/
├── .github/
│   ├── agents/             # Developer agent definition
│   ├── skills/             # Orchestrator skill definition
│   └── copilot-instructions.md
├── .vscode/
│   └── mcp.json            # Backlog MCP server configuration
├── backlog/                # Backlog.md workspace
│   ├── tasks/              # Active task files
│   ├── completed/          # Completed tasks
│   ├── milestones/         # Project milestones
│   ├── decisions/          # Architecture decision records
│   ├── drafts/             # Draft tasks
│   ├── docs/               # Project documentation
│   └── archive/            # Archived items
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with GitHub Copilot extension
- [Backlog CLI](https://backlog.md) installed globally
- Node.js 18+

### Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd kafka-lab-copilot
   ```

2. Open in VS Code:
   ```bash
   code .
   ```

3. The Backlog MCP server will start automatically via `.vscode/mcp.json`.

## Workflow

1. Discuss intent and requirements with the **Orchestrator** in Copilot Chat.
2. The Orchestrator creates structured tasks in the backlog using `task-{epic}.{task}` notation (e.g., `task-1.1`).
3. The Orchestrator delegates tasks to the **Developer** subagent.
4. The Developer implements code + tests and marks tasks `Done`.
5. The Orchestrator reviews progress and coordinates next steps.

## Backlog Management

All project management is done through the **Backlog MCP**. Task IDs use dot notation:

| Format | Example | Description |
|--------|---------|-------------|
| `task-{epic}.{task}` | `task-1.1` | Task 1 under Epic 1 |

Task statuses: `To Do` → `In Progress` → `Done`

## Technology Stack

| Area | Technology |
|------|-----------|
| Streaming | Apache Kafka |
| Infrastructure | Terraform |
| Backend | Python / TypeScript |
| Scripting | Shell (bash) |
| AI Tooling | GitHub Copilot (Agentic) |
| Project Mgmt | Backlog.md + MCP |

## Contributing

All contributions flow through the two-agent system. To propose new work:

1. Open Copilot Chat and describe the feature or fix to the Orchestrator.
2. The Orchestrator will create the appropriate backlog tasks.
3. Assign the task to the Developer agent for implementation.
