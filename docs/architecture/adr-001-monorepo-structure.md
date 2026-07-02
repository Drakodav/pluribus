# ADR 001: Decoupled Monorepo Structure

* **Status**: Accepted
* **Date**: 2026-07-02
* **Author**: Antigravity & Developer

## Context

We need to establish a repository structure for "Pluribus" that will contain multiple independent applications, utility tools, documentation, and agent configurations. The goals are:
1. Provide a unified workspace for a single developer and their AI agents.
2. Avoid locking the project into a single framework, language runtime, or heavy workspace configuration early on.
3. Keep the repository modular, allowing easy deletion or addition of components.

## Decision

We will adopt a **Decoupled, Justfile-Driven Monorepo Structure**:
* The repository root remains free of project-wide configurations (no root-level `package.json`, `tsconfig.json`, or `pyproject.toml`).
* Applications live in `apps/` and CLI tools/scripts live in `tools/`. Each subdirectory is self-contained with its own dependencies and configuration files.
* [just](https://github.com/casey/just) is used as the root command runner to orchestrate tasks across the independent folders.
* Agent instructions, workspace configuration, and memory files are placed under `.agents/` and `docs/memory/` respectively.

## Consequences

### Positive
* **Decoupling**: Adding, modifying, or removing a project under `apps/` or `tools/` will not break dependencies in other projects.
* **Polyglot Flexibility**: We can freely mix TypeScript, Python, Rust, or Go without resolving root-level build tool conflicts.
* **Context Cleanliness**: AI agents can easily understand where files belong and locate configurations since they are isolated.

### Negative / Trade-offs
* **No Root Node Modules**: Dependencies must be installed per-project rather than globally at the root, which requires running installs in multiple directories (though this can be automated via `just`).
* **Code Sharing**: Code sharing between TS projects cannot rely on pnpm workspaces, and must instead use local imports or folder-relative packaging if needed.
