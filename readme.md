# Pluribus

> *Ex Pluribus Unum* — Out of many, one.

Pluribus is a personal, AI-first monorepo. It serves as a unified home for applications, scripts, developer tools, infrastructure, and agent memory.

---

## The Story & Philosophy

### Why Pluribus?
The name **Pluribus** is Latin for "many," taking inspiration from the classic phrase *Ex Pluribus Unum* (a nod to the craftsmanship of Monkey 47 gin). 

For personal projects, the biggest bottleneck is often **context, decision, and setup fatigue**—creating a brand-new environment, choosing libraries, and setting up tooling from scratch for every quick website, script test, or utility idea.

Pluribus is designed to eliminate that friction. It is a single, unified "home" for many projects. When inspiration strikes, there is no setup fatigue: the tooling is already configured, the repository rules are defined, and the project can be spun up immediately in its own directory within a shared workspace.

---

## Projects Directory & Showcase

Explore the active projects currently maintained inside Pluribus:

| Project | Description | Primary Tech Stack | Documentation |
| :--- | :--- | :--- | :---: |
| **[Homelab](projects/homelab/)** | **Split-Brain Hybrid Cloud & Declarative Engine**<br>Self-hosted private cloud connecting an Oracle Cloud edge gateway (`aperio`) with an on-premises compute powerhouse (`macerator`) via an encrypted WireGuard mesh, Traefik TLS routing, Consul service discovery, Authentik SSO/OIDC, and a type-safe Python orchestration engine. | Python 3.13, Pydantic V2, Typer, Docker Compose, WireGuard, Consul, Traefik, Terraform, Authentik, PostgreSQL + pgvector, Immich, Home Assistant | [**Read Guide ➔**](projects/homelab/README.md) |
| **[Git History CV Extractor](projects/git-history-cv-extractor/)** | **Resume Intelligence & Contribution Miner**<br>Interactive developer intelligence utility that parses Git commits, diffs, and contribution histories across local and remote repositories into structured, LLM-optimized Markdown summaries for resume crafting. | Python 3.13, SQLModel, SQLite, GitPython, Questionary, Rich | [**Read Guide ➔**](projects/git-history-cv-extractor/README.md) |

---

## Repository Structure

The monorepo is organized to maximize decoupling, readability, and contextual clarity:

```
pluribus/
├── .agents/                    # Agent control plane (workspace rules, skills, configs)
│   ├── skills/                 # Custom domain-specific agent skills
│   └── AGENTS.md               # Standard workspace agent guidelines
├── docs/                       # Monorepo knowledge base and architectural records
│   ├── architecture/           # Architectural Decision Records (ADRs)
│   └── memory/                 # Session history logs and persistent notes
├── projects/                   # Independent applications and infrastructure stacks
│   ├── homelab/                # Hybrid cloud infrastructure & declarative CLI
│   └── git-history-cv-extractor/ # Git metadata mining & resume generation tool
├── tools/                      # Standalone CLI tools and automation scripts
├── justfile                    # Top-level task orchestrator
└── pluribus.code-workspace     # VS Code multi-root workspace definition
```

---

## Workspace Tooling

To ensure a seamless development experience across multiple independent projects, Pluribus provides:

- **VS Code Multi-Root Workspace**: Open `pluribus.code-workspace` in VS Code. This configuration isolates virtual environments, interpreters, and linting settings for each project natively, preventing dependency bleed.
- **Uniform Task Runner**: Uses [just](https://github.com/casey/just) to provide identical ergonomics across all directories (`just`, `just pre-commit`, `just format`, `just lint`).
- **Standardized Pre-Commit Quality Gates**: Repository pre-commit hooks verify code formatting, static type checking (`ty` / `mypy`), and test suites before commits are recorded.

---

## Getting Started

This repository uses [just](https://github.com/casey/just) as its primary command runner.

### System Prerequisites
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver)
- [just](https://github.com/casey/just) (Command orchestrator)
- [Docker Engine & Compose Plugin](https://docs.docker.com/engine/)

### Common Commands

```bash
# List all workspace orchestrator commands
just

# Verify environment prerequisites (uv, docker, terraform)
just doctor

# Install repository-wide Git pre-commit hooks
just install-hooks

# Run pre-commit checks across all projects
just pre-commit
```

---

## License

This repository is licensed under a custom **MIT License with Non-AI Restriction**. You are free to download, study, and use the code for personal development, but usage of this codebase (or any portion thereof) for the purpose of training machine learning models or artificial intelligence systems is strictly prohibited. See [LICENSE](LICENSE) for details.