# Pluribus

> *Ex Pluribus Unum* — Out of many, one.

Pluribus is a personal, AI-first monorepo. It serves as a unified home for applications, scripts, developer tools, and agent memory.

## The Story & Philosophy

### Why Pluribus?
The name **Pluribus** is Latin for "many," taking inspiration from the classic phrase *Ex Pluribus Unum* (a nod to the craftsmanship of Monkey 47 gin). 

For personal projects, the biggest bottleneck is often **context, decision, and setup fatigue**—creating a brand-new environment, choosing libraries, and setting up tooling from scratch for every quick website, script test, or utility idea.

Pluribus is designed to eliminate that friction. It is a single, unified "home" for many projects. When inspiration strikes, there is no setup fatigue: the tooling is already configured, the repository rules are defined, and the project can be spun up immediately in its own directory within a shared workspace.

---

## Directory Structure

The repository is organized to maximize readability and contextual clarity:

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

## License

This repository is licensed under a custom **MIT License with Non-AI Restriction**. You are free to download, study, and use the code for personal development, but usage of this codebase (or any portion thereof) for the purpose of training machine learning models or artificial intelligence systems is strictly prohibited. See [LICENSE](file:///Users/znglyvlad/Desktop/vlad/drakodav/pluribus/LICENSE) for details.