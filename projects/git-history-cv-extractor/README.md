# git-history-cv-extractor

This is a utility project designed to scan and extract metadata/context from Git repositories (commits, diffs, refactoring events, message summaries) for downstream consumption by an AI to construct or update a CV/resume.

## Features

- **Interactive Console Wizard**: A guided terminal interface powered by `questionary` to authenticate, register repositories, view stats, and export reports.
- **Dual-Mode Operation**:
  - *Test Mode*: Sandbox execution utilizing a local `output/test/` workspace. Automatically scans the parent Pluribus monorepo read-only on startup, bypassing authentication.
  - *Real Mode*: Production execution utilizing `output/real/` workspace. Requires active GitHub authentication to clone/fetch external repositories.
- **SQLite Ingestion Cache**: Powered by `sqlmodel` (SQLAlchemy/Pydantic) to store parsed repositories, commits, and file changes, avoiding redundant Git queries.
- **Git Extraction Engine**: Clones, fetches, and parses commit histories, author details, and file-level addition/deletion metrics using `GitPython`.
- **Interactive Author Resolution**: Prompts you to confirm whether encountered commit authors represent your work. Decisions (including ignored accounts) are cached persistently.
- **Tech Stack Auto-Detection**: Dynamically maps modified file extensions to summarize the technologies used in each repository.
- **Markdown Report Generation**: Groups contribution statistics and commit logs by repository into a comprehensive Markdown file optimized for resume generation.

## Setup & Usage

This project uses `just` as a command runner and `uv` for environment management.

### System Prerequisites
- [uv](https://github.com/astral-sh/uv) (Astral's fast Python package installer and resolver)
- [just](https://github.com/casey/just) (Command orchestrator)
- [GitHub CLI (gh)](https://cli.github.com/) (Required for Real Mode GitHub token retrieval)

### Command Reference

Run these commands inside the `projects/git-history-cv-extractor` directory:

- **List commands**: `just` (or `just --list`)
- **Initialize & Sync dependencies**: `just setup`
- **Execute script**: `just run`
- **Format codebase**: `just format`
- **Lint codebase**: `just lint`
- **Static type check**: `just typecheck`
- **Run project hooks**: `just pre-commit` (runs check, format, and ty typecheck)
- **Clean output & environment**: `just clean`
