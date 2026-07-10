# Issue 001: Database Setup and Helpers

## Overview
We need a local persistent data store to cache repository metadata, commit logs, and file changes. This allows us to run fast incremental updates, avoid re-parsing old commits, and run SQL queries to generate reports.

We will use **`sqlmodel`** (built on top of SQLAlchemy and Pydantic) for type safety and database table mappings. The database file will be stored at `output/extractor.db`.

## Requirements

### 1. Database Schema (SQLModel classes)
Define the following models in Python:

* **`Config`**: Key-value pairs for configuration settings.
  * `key`: `str` (Primary Key)
  * `value`: `str`
* **`Repository`**: Monitored repos.
  * `id`: `int | None` (Primary Key, Autoincrement)
  * `name`: `str` (Unique, Index)
  * `url`: `str`
  * `local_path`: `str`
  * `last_scanned_commit`: `str | None`
  * `last_scanned_at`: `datetime` (Default: current timestamp)
* **`Commit`**: Parsed commit records.
  * `id`: `int | None` (Primary Key, Autoincrement)
  * `repo_id`: `int` (Foreign Key referencing `Repository.id`)
  * `hash`: `str` (Unique, Index)
  * `author_name`: `str`
  * `author_email`: `str`
  * `commit_date`: `str` (ISO 8601 string)
  * `message`: `str`
* **`FileChange`**: Changes per file in each commit.
  * `id`: `int | None` (Primary Key, Autoincrement)
  * `commit_id`: `int` (Foreign Key referencing `Commit.id`)
  * `file_path`: `str`
  * `file_extension`: `str`
  * `additions`: `int`
  * `deletions`: `int`

### 2. DatabaseHelper Interface
Implement a `DatabaseHelper` class in Python containing the following methods:
* `__init__(db_path: Path)`: Connects to SQLite and calls `SQLModel.metadata.create_all(engine)`.
* `get_config(key: str) -> str | None`: Queries configuration value.
* `set_config(key: str, value: str)`: Inserts or updates configuration value.
* `add_repository(name: str, url: str, local_path: str) -> int`: Inserts or returns repository ID if already existing.
* `update_repository_scanned(repo_id: int, commit_hash: str)`: Updates `last_scanned_commit` and `last_scanned_at` for a repository.
* `add_commit(repo_id: int, commit_hash: str, author_name: str, author_email: str, commit_date: str, message: str) -> int`: Inserts a commit and returns its internal database ID.
* `add_file_change(commit_id: int, file_path: str, additions: int, deletions: int)`: Resolves file extension and inserts a file change record.
* `get_repo_stats(repo_id: int) -> dict`: Returns a dictionary containing:
  * `total_commits`: `int`
  * `files_changed`: `int`
  * `total_additions`: `int`
  * `total_deletions`: `int`

## Definition of Done
- Database helper code satisfies Ruff formatting and linting check.
- `ty` type checking passes cleanly.
- Unit tests or manual test scripts verify that:
  - Config key-values are correctly saved and read.
  - Repos, commits, and file changes are successfully saved and respect unique constraints.
  - Statistics query outputs match test inserts.
