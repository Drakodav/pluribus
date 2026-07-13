# Workspace Rules for AI Agents

Welcome to the Pluribus workspace. As an agent operating in this repository, you must adhere to the following rules and design principles to ensure consistency, clarity, and safety.

## 1. Directory Ownership & Decoupling
- **Root Minimalist Policy**: Do not create top-level directories or workspace-wide package/project configuration files (e.g., `package.json`, `pyproject.toml` in the root). 
- **Folder Scoping**: Keep project dependencies, database paths, and runtime configurations isolated inside their respective subfolders under `projects/` and `tools/`.
- **Project Agent Folders**: Every project must maintain a local `.agents/` folder for agent checklist tracking (`.agents/task.md`), issue PRDs (`.agents/issues/`), and temporary execution/scratch files (`.agents/temp/`).
- **Scratch and Temp Space**:
  - Subproject-specific temporary run files, manual testing scripts, or database test logs must be written inside `projects/<project-name>/.agents/temp/`. This folder is globally gitignored.
- **Language Standards**: Subprojects must adhere to standardized language configurations defined inside `.agents/rules/` (e.g., `.agents/rules/python.md` for Python).

## 2. Command Orchestration
- **Command Runner**: The repository uses `just` as the uniform interface for executing tasks.
- **Root Justfile**: The root `Justfile` orchestrates workspace-wide actions. If a subdirectory has unique build/run tasks, define a local `Justfile` within that directory and proxy it from the root `Justfile` if appropriate.

## 3. Code & Safety Conventions
- **No Side Effects**: Do not make network requests or execute untrusted code without explicit user awareness.
- **Linting & Formatting**: Follow formatting rules defined within each project folder. Maintain code styles and preserve unrelated comments or docstrings.

## 4. Git & Commit Guidelines
- **No Auto-Committing**: Do not run `git commit` automatically. Always present the proposed files and commit message to the user, and ask for explicit approval before running any commit command.

## 5. Naming Conventions
- **Folder and File Names**: All directory and file names should be strictly lowercase and separated by a dash (kebab-case), for example: `git-history-cv-extractor` or `session-log.md`.
- **Task Runner Names**: Local directory task runner files must be named `justfile` in all lowercase (never capitalized as `Justfile`).


## Agent skills

### Issue tracker

Issues are tracked on GitHub using the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Using default triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context layout configured. See `docs/agents/domain.md`.
