# Workspace Rules for AI Agents

Welcome to the Pluribus workspace. As an agent operating in this repository, you must adhere to the following rules and design principles to ensure consistency, clarity, and safety.

## 1. Directory Ownership & Decoupling
- **Root Minimalist Policy**: Do not create top-level directories or workspace-wide package/project configuration files (e.g., `package.json`, `pyproject.toml` in the root). 
- **Folder Scoping**: Keep project dependencies and runtime configurations isolated inside their respective subfolders under `projects/` and `tools/`.
- **Scratch Space**: Always use the `scratch/` directory for temporary files, log dumps, or test scripts. Never commit files directly under `scratch/` to Git.

## 2. Command Orchestration
- **Command Runner**: The repository uses `just` as the uniform interface for executing tasks.
- **Root Justfile**: The root `Justfile` orchestrates workspace-wide actions. If a subdirectory has unique build/run tasks, define a local `Justfile` within that directory and proxy it from the root `Justfile` if appropriate.

## 3. Persistent Memory & Documentation
- **Session Summarization**: At the end of every conversation, you must document your progress:
  - Create or append to a log file in `docs/memory/` (e.g., named by year-month or `session-log.md`).
  - Summarize what changed, why, and what actions are recommended next.
- **Architectural Records**: Major architectural decisions must be written as Markdown documents under `docs/architecture/` using the ADR (Architectural Decision Record) format.

## 4. Code & Safety Conventions
- **No Side Effects**: Do not make network requests or execute untrusted code without explicit user awareness.
- **Linting & Formatting**: Follow formatting rules defined within each project folder. Maintain code styles and preserve unrelated comments or docstrings.
