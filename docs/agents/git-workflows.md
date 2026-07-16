# Git Workflows

Guidelines for AI agents performing Git operations in the Pluribus repository.

## 1. Branch Naming

Branches should be named cleanly using the project `alias` defined in the project's metadata header (see [domain.md](domain.md)).

- **Format**: `<project-alias>/<issue-number>-<short-description>`
- **Example**: `git-cv/123-sqlite-cache`
- **Fallback (No alias or no issue number)**:
  - If no alias exists, use the project folder name: `git-history-cv-extractor/123-sqlite-cache`
  - For general repository tasks: `general/<short-description>`

## 2. Commit Naming & Guidelines

- **Format**: `<project-alias>: <description> (fixes #<issue-number>)`
- **Example**: `git-cv: add SQLite caching layer (fixes #123)`
- **Fallback (No alias)**: Use `<project-name>: <description> (fixes #<issue-number>)`
- **General Commits**: `general: <description>`

> [!IMPORTANT]
> **No Auto-Committing Rule** (from [.agents/AGENTS.md](../../.agents/AGENTS.md)):
> Do NOT execute `git commit` automatically. Always present the proposed changes/files and target commit message to the user, and ask for explicit approval before running any commit command.

## 3. Pull Requests (PRs)

When preparing code changes for submission, create a Pull Request matching the issue structure:
- **PR Title**: `[<project-alias>] <title>` (e.g., `[git-cv] Add SQLite Caching Layer`).
- **PR Description**: Include the phrase `Closes #<issue-number>` to automatically link and close the tracking issue upon merge.

## 4. Git Worktrees for Isolated Tasks

In monorepos, multiple features or bug fixes might be worked on concurrently. To avoid dirtying your main workspace or losing uncommitted work:
- Use `git worktree` to isolate changes on a separate branch.
- Place all temporary worktrees under a directory that is gitignored, such as `projects/<project-name>/.agents/temp/worktrees/` or `.worktrees/` at the root.

### Example Commands:
1. **Create and switch to a worktree**:
   ```bash
   git worktree add -b git-cv/123-sqlite-cache projects/git-history-cv-extractor/.agents/temp/worktrees/123-sqlite-cache main
   ```
2. **Remove a worktree once done**:
   ```bash
   git worktree remove projects/git-history-cv-extractor/.agents/temp/worktrees/123-sqlite-cache
   ```
