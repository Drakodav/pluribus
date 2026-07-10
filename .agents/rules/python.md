# Python Subproject Standards and Rules

Every Python subproject in the Pluribus monorepo must adhere to the following standards, configurations, and directory isolation boundaries:

## 1. Directory Structure & Boundaries
- All project code and run environments must live strictly inside the subproject folder: `projects/<project-name>/`.
- **No Global Scratch Pollution**: Agents are strictly prohibited from writing temporary code, logs, or test scripts in the root `scratch/` folder.
- **Agent Sandbox**: All agent checklists, PRDs, walkthroughs, and temporary test script execution files must live inside the project-level `.agents/` folder:
  - `projects/<project-name>/.agents/issues/` (Project PRDs / Issue specs)
  - `projects/<project-name>/.agents/temp/` (Gitignored temporary run/test files)
  - `projects/<project-name>/.agents/task.md` (Active checklist)

## 2. Standard Dependency and Code Styling Tooling
- **Package Manager**: Use Astral `uv` exclusively. Declare dependencies inside `pyproject.toml`. Do not run global pip installations.
- **Linter & Formatter**: Use `ruff`. All code must pass `ruff check .` and conform to `ruff format .`.
- **Type Checking**: Use `ty` (Astral's fast Rust-based static type checker). Ensure all code passes `ty check .` before staging/committing.
- **Python Code Conventions**:
  - Always prefer explicit type annotations (e.g. `var: int | None = None` instead of `Optional[int]`).
  - Keep functions small, modular, and single-purpose.
  - Document public APIs using clear docstrings.

## 3. Standard Task Runner Interface (`justfile`)
Every Python project must feature a local task runner named `justfile` in all lowercase, implementing the following standard recipes:

```just
# List available commands
default:
    @just --list

# Lint codebase
lint:
    uv run ruff check .

# Auto-format code
format:
    uv run ruff format .

# Run static type checking
typecheck:
    uv run ty check .

# Run project unit/integration tests
test:
    # (Specify python test command e.g., uv run pytest)

# Run the project entrypoint
run:
    # (Specify python run command e.g., uv run python main.py)

# Standard pre-commit hook aggregator
pre-commit: lint format typecheck test
```
