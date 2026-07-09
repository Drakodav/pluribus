# Pluribus

> *Ex Pluribus Unum* — Out of many, one.

Pluribus is a personal AI-native monorepo designed for a single developer and a collaborative suite of AI agents. It serves as a unified workspace for applications, scripts, developer tools, and agent memory.

## Directory Structure

The repository is organized to maximize readability and contextual clarity for both human developers and AI agents:

- **`.agents/`** — Agent control plane: holds workspace-scoped rules, skills, and configuration.
  - **`skills/`** — Custom domain-specific skills for agents.
  - **`AGENTS.md`** — Workspace rules and instructions for agents.
- **`projects/`** — Independent projects and applications (e.g., frontends, APIs, libraries).
- **`tools/`** — Command-line utilities, background scripts, and automation tools.
- **`docs/`** — Knowledge base and repository documentation.
  - **`architecture/`** — Architectural Decision Records (ADRs).
  - **`memory/`** — Persistent agent session summaries.
- **`scratch/`** — A gitignored local playground for experiments, drafting, and testing.

## Getting Started

This repository uses [just](https://github.com/casey/just) as its primary command runner. 

To list all available commands, run:
```bash
just
```

To check environment prerequisites, run:
```bash
just doctor
```