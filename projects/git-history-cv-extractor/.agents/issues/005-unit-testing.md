# Issue 005: Unit Testing & Mock Verifications

* **Status**: Pending
* **Implementation Commit**: `N/A`

## Overview
To ensure long-term stability and reliability of the `git-history-cv-extractor` subproject, we need a complete test suite covering the database schema, SQLite state caching, GitHub auth checks, and GitPython parsing.

## Requirements

### 1. Test Harness
- Install `pytest` and `pytest-mock` inside project dependencies:
  `uv add --dev pytest pytest-mock`
- Add a project-local target `just test` routing execution to `pytest`.

### 2. Database Unit Tests
- Assert SQLModel database creation functions correctly.
- Assert helper insertion methods (`add_repository`, `add_commit`, `add_file_change`) write rows and return correct IDs.
- Assert `get_repo_stats` calculates lines added/deleted and commits correctly.

### 3. Authentication Caching Tests
- Mock subprocess commands for `gh` checks.
- Assert that `GitHubAuth` caches tokens to the database on successful login and clears cache correctly on request.

### 4. Git Ingestion Mock Tests
- Mock GitPython dependencies (e.g. `git.Repo`, commits, stats dictionary) to assert that `GitExtractor.scan_repository` parses additions/deletions, maps author aliases using callback triggers, and updates the repository state safely.

---

## Verification Plan
- Executing `just test` runs all pytest files and passes successfully.
