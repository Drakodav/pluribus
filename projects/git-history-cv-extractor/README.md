# Git History CV Extractor: Resume Intelligence & Contribution Miner

An AI-ready developer intelligence tool designed to parse, extract, and synthesize historical metadata from Git repositories (commits, diffs, refactoring events, and commit summaries) for downstream ingestion by Large Language Models to construct or update professional CVs and portfolios.

This project lives inside the **Pluribus** monorepo under [`projects/git-history-cv-extractor/`](.).

---

## 1. Pipeline Overview

```
   ┌───────────────────────┐       ┌───────────────────────┐
   │ Local Git Repository  │       │ Remote GitHub Repos   │
   │ (Read-Only Test Mode) │       │ (Authed via `gh` CLI) │
   └───────────┬───────────┘       └───────────┬───────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │    Git Extraction Pipeline    │
               │   (GitPython + Diff Parser)   │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │  Interactive Author Resolver  │
               │ (Persistent Identity Mapping) │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │   SQLite Ingestion Cache      │
               │    (SQLModel / Pydantic)      │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │     Tech Stack Detection      │
               │  & Markdown Report Generator  │
               │    (LLM-Optimized Context)    │
               └───────────────────────────────┘
```

---

## 2. Core Capabilities

- **Interactive Terminal Wizard**: Guided CLI built with `questionary` and `rich` to authenticate, register repositories, inspect contribution metrics, and export structured reports.
- **Dual-Mode Execution**:
  - **Sandbox / Test Mode**: Operates in an isolated `output/test/` workspace. Automatically analyzes the parent Pluribus repository on startup without requiring external network access or GitHub tokens.
  - **Real / Production Mode**: Operates in an `output/real/` workspace. Uses the local GitHub CLI (`gh`) session to dynamically list, clone, and ingest remote user repositories.
- **Persistent Ingestion Cache**: Uses `sqlmodel` (combining SQLAlchemy with Pydantic) and SQLite to cache repositories, commit hashes, author metadata, and file changes, preventing expensive re-parsing of Git histories.
- **Interactive Author Disambiguation**: As new commit authors or email aliases are discovered across repositories, the wizard prompts you to confirm whether they represent your work. Your identity resolutions (and ignored bot/colleague accounts) are persistently cached.
- **Tech Stack Auto-Detection**: Analyzes file extensions, commit scopes, and language distributions to summarize the exact technologies and frameworks used per repository.
- **LLM-Optimized Markdown Output**: Synthesizes key accomplishments, structural changes, repository statistics, and major milestones into an organized Markdown document ready for LLM prompt context.

---

## 3. Directory Layout

```
projects/git-history-cv-extractor/
├── main.py                     # CLI entrypoint and questionary console wizard
├── pyproject.toml              # Dependencies and project metadata (managed by uv)
├── justfile                    # Local project task runner recipes
├── src/                        # Core extraction and parsing modules
│   ├── cache.py                # SQLModel cache database schema and helpers
│   ├── extractor.py            # GitPython commit log and diff extraction
│   ├── github.py               # GitHub CLI token integration and repo listing
│   └── reporter.py             # Markdown summary and technology aggregator
└── tests/                      # Pytest unit and integration test suite
```

---

## 4. Setup & Usage

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (Python package installer and execution engine)
- [just](https://github.com/casey/just) (Command runner)
- [GitHub CLI (gh)](https://cli.github.com/) (Required for Real Mode repository fetching)

### Command Reference

Run these commands inside `projects/git-history-cv-extractor/`:

```bash
# Display all available recipes
just

# Install and sync virtual environment dependencies
just setup

# Launch the interactive extraction wizard
just run

# Run code formatting and lint checks
just format
just lint

# Run static type checking with ty
just typecheck

# Run pre-commit quality gate (ruff, formatting, typecheck)
just pre-commit

# Clean cache databases and temporary output directories
just clean
```

---

## 5. License

Maintained inside the **Pluribus** monorepo under the terms of the root repository [LICENSE](../../LICENSE).
