# git-history-cv-extractor

This is a utility project designed to scan and extract metadata/context from Git repositories (commits, diffs, refactoring events, message summaries) for downstream consumption by an AI to construct or update a CV/resume.

## Features

- Scans repository commits, authors, dates, and messages.
- Dumps contextual files into a gitignored `output/` directory.
- Fully managed using Astral `uv` and `ruff` (formatting & linting).

## Setup & Usage

This project uses `just` as a command runner and `uv` for environment management.

### System Prerequisites
- [uv](https://github.com/astral-sh/uv) (Astral's fast Python package installer and resolver)
- [just](https://github.com/casey/just) (Command orchestrator)

### Command Reference

Run these commands inside the `projects/git-history-cv-extractor` directory:

- **List commands**: `just` (or `just --list`)
- **Initialize & Sync dependencies**: `just setup`
- **Execute script**: `just run`
- **Format codebase**: `just format`
- **Lint codebase**: `just lint`
- **Clean output & environment**: `just clean`
