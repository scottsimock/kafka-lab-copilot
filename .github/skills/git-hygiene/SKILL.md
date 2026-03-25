---
name: git-hygiene
description: Enforce consistent git practices including atomic commits, meaningful commit messages, co-author trailers, and branch-per-epic workflows after each completed task. Use when completing backlog tasks, making code changes, or when user mentions git commits or commit hygiene.
---

# Git Hygiene

Maintain clean, traceable commit history by following structured git practices throughout development work.

## Branch Workflow

All development work happens on **feature branches**, never directly on `main`. The orchestrator manages the branch lifecycle.

### Branch Lifecycle

```
main ─────────────────────────────────────────────────── main
  │                                                       ▲
  └── epic/{epic-id}/{short-description} ────────────────┘
        │        │        │        │           PR (human review)
        commit   commit   commit   commit
        task-1.1 task-1.2 task-1.3 task-1.4
```

### Orchestrator Responsibilities (before delegating work)

1. **Create the branch** before delegating any tasks to developer agents:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b epic/{epic-id}/{short-description}
   ```
   Example: `epic/1/azure-infrastructure-foundation`

2. **Confirm the branch** is active before kicking off developer agents:
   ```bash
   git branch --show-current
   ```

3. All developer agents commit to **this branch only** — never to `main`.

### Orchestrator Responsibilities (after all tasks complete)

Once every task in the epic is done and validated:

1. **Push the branch**:
   ```bash
   git push -u origin epic/{epic-id}/{short-description}
   ```

2. **Create a Pull Request** to `main` using the GitHub CLI:
   ```bash
   gh pr create \
     --base main \
     --head epic/{epic-id}/{short-description} \
     --title "Epic {epic-id}: {Epic Title}" \
     --body "## Summary
   
   {Brief description of what this epic delivers.}
   
   ## Tasks Completed
   
   - task-{epic}.1 - {description}
   - task-{epic}.2 - {description}
   ...
   
   ## Decisions Referenced
   
   - decision-XXXX - {title}
   
   ## Review Notes
   
   {Any context the reviewer should know.}"
   ```

3. **Notify the user** that the PR is ready for human review and approval.
4. **Do NOT merge** — a human must review and approve the PR.

### Branch Naming Convention

```
epic/{epic-number}/{kebab-case-description}
```

Examples:
- `epic/1/azure-infrastructure-foundation`
- `epic/2/confluent-kafka-deployment`
- `epic/3/monitoring-and-observability`

### Multiple Epics

Epics run sequentially. Each epic gets its own branch:
- Epic 1 branch → PR → human merges to main
- Orchestrator waits for merge confirmation
- Epic 2 branch created from updated main → PR → human merges
- And so on

If a subsequent epic must start before the prior PR is merged, branch from the prior epic's branch instead of `main`, and note this in the PR description.

## Commit Message Format

Follow this pattern for all commits related to backlog tasks:

```
Task: task-{epic}.{task} - Brief one-line summary

Optional multi-line body explaining the why/what.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

**Rules**:
- Line 1: `Task: task-ID - Summary` (keep under 72 chars after "Task: ")
- Line 2: Blank
- Lines 3+: Optional detailed explanation (wrap at 72 chars)
- Last line: Co-authored-by trailer (always include)
- One commit per completed task minimum
- Multiple commits ok for large tasks (keep each atomic/focused)

## Quick Start (Developer Agents)

When completing a backlog task:

1. **Verify you are on the correct branch**: `git branch --show-current` — must NOT be `main`
2. **Review changes**: `git status` and `git diff` to see all modifications
3. **Create atomic commit**:
   ```bash
   git add <files>
   git commit -m "Task: <task-id> - <concise description>
   
   <optional detailed explanation>
   
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
   ```
4. **Verify**: `git log --oneline -1` to confirm commit was created

## When to Commit

- **After each task completion**: Once a backlog task status moves to `Done`, a corresponding commit must be created
- **Atomic changes**: Each commit should represent one logical change
- **Before task transitions**: Commit before marking task status in backlog

## Verification Checklist

After delegating a task, the orchestrator verifies:

- [ ] Developer is on the correct epic branch (not `main`)
- [ ] All code changes are staged and committed
- [ ] Commit message includes task ID (`task-{epic}.{task}`)
- [ ] Co-author trailer is present
- [ ] Commit exists in git log: `git log --oneline | head -1`
- [ ] Commit contains only changes related to the task

After all tasks in an epic are complete, the orchestrator verifies:

- [ ] All task commits are on the epic branch
- [ ] Branch has been pushed to origin
- [ ] PR has been created to `main`
- [ ] PR description lists all completed tasks
- [ ] User has been notified for review

## Troubleshooting

**Developer committed to `main` by mistake?**
- Cherry-pick the commit to the epic branch and reset `main`:
  ```bash
  git checkout epic/{epic-id}/{description}
  git cherry-pick <commit-hash>
  git checkout main
  git reset --hard HEAD~1
  ```

**Commit already made but task status not updated?**
- Update task status in backlog to reflect git commit

**Need to amend the last commit?**
- `git commit --amend --no-edit` to add more changes
- `git commit --amend` to edit message

**Multiple commits for one task?**
- This is fine for large tasks
- Ensure each commit relates to the task and includes task ID in message

**GitHub CLI not available for PR creation?**
- Provide the user with the branch name and ask them to create the PR manually
- Include the PR title and body text for them to copy

---

**Related**: See orchestrator and developer agent definitions for how this integrates into workflows.
