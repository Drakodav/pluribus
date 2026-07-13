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

## Workspace Tooling

To ensure a seamless development experience across multiple projects, Pluribus includes the following workspace setups:

- **VS Code Multi-Root Workspace**: Open `pluribus.code-workspace` in VS Code. This configuration isolates virtual environments, interpreters, and linting settings for each project natively, preventing dependency bleed.
- **Git Hooks**: Ensure project quality by installing pre-commit hooks that run static analysis and formatting locally before commits are finalized.

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

To install repository-wide Git pre-commit hooks, run:
```bash
just install-hooks
```