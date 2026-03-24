---
name: git-hygiene
description: Enforce consistent git practices including atomic commits, meaningful commit messages, and co-author trailers after each completed task. Use when completing backlog tasks, making code changes, or when user mentions git commits or commit hygiene.
---

# Git Hygiene

Maintain clean, traceable commit history by following structured git practices throughout development work.

## Quick Start

When completing a backlog task:

1. **Review changes**: `git status` and `git diff` to see all modifications
2. **Create atomic commit**:
   ```bash
   git add <files>
   git commit -m "Task: <task-id> - <concise description>
   
   <optional detailed explanation>
   
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
   ```
3. **Verify**: `git log --oneline -1` to confirm commit was created

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

## When to Commit

- **After each task completion**: Once a backlog task status moves to `Done`, a corresponding commit must be created
- **Atomic changes**: Each commit should represent one logical change
- **Before task transitions**: Commit before marking task status in backlog

## Verification Checklist

After delegating a task, verify completion includes:

- [ ] All code changes are staged and committed
- [ ] Commit message includes task ID (`task-{epic}.{task}`)
- [ ] Co-author trailer is present
- [ ] Commit exists in git log: `git log --oneline | head -1`
- [ ] Commit contains only changes related to the task

## Troubleshooting

**Commit already made but task status not updated?**
- Update task status in backlog to reflect git commit

**Need to amend the last commit?**
- `git commit --amend --no-edit` to add more changes
- `git commit --amend` to edit message

**Multiple commits for one task?**
- This is fine for large tasks
- Ensure each commit relates to the task and includes task ID in message

---

**Related**: See orchestrator and developer agent definitions for how this integrates into workflows.
