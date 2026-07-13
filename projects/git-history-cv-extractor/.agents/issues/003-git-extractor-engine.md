# Issue 003: Git Extraction Engine

* **Status**: Completed
* **Implementation Commit**: `PENDING`




## Overview
We need an extraction engine that clones remote repositories, performs incremental fetching, parses commits and file diff statistics, and stores them in the SQLite database.

We will use the **GitPython** library to perform repository operations and walk commit history.

To support mode separation:
- **Test Mode**: Cloned repositories are saved to `output/test/repos/<repo-name>/`.
- **Real Mode**: Cloned repositories are saved to `output/real/repos/<repo-name>/`.

## Requirements

### 1. Repository Life-cycle & Path Mapping
* Save all clones inside `<mode_dir>/repos/<repo-name>/`.
* If a repository has not been cloned yet:
  - Form the authenticated clone URL using the retrieved access token:
    `https://<token>@github.com/<owner>/<repo>.git` (or use the SSH path directly if the URL specifies SSH).
  - Run `git.Repo.clone_from(clone_url, local_path)`.
* If the repository already exists locally:
  - Open the repository: `repo = git.Repo(local_path)`.
  - Run `repo.remotes.origin.pull()` or `repo.remotes.origin.fetch()` to get the latest commits.

### 2. Identity and Email Aliases Detection
To filter commits that belong to *you*:
* Store your known/approved git email addresses in the `config` SQLite table under the key `author_emails` (as a JSON list).
* When scanning a repository, check each commit's author email:
  - If the commit's author email is in the `author_emails` list, parse it.
  - If the commit's author name suggests it is you (e.g. matching your primary name/email alias prefix) but the email is not in the list:
    - Prompt the user in the CLI: *"We found commits by '<Name> <new@email.com>'. Is this you? [y/N]"*
    - If you select yes, add the new email address to the database `author_emails` config list and scan those commits.

### 3. Full Commit Diff Parsing (Data Wholeness)
For a repository, parse commits as follows:
* **Incremental Check**:
  - Read `last_scanned_commit` for the repository from the SQLite database.
  - If the repository has a saved scanned commit and it matches the current HEAD, skip scanning.
  - Otherwise, walk the commit history from the current HEAD back to either the beginning of history or until the `last_scanned_commit` is reached.
* **Diff Parsing**:
  - For each commit by an approved author, extract: hash, author name, author email, date, and commit message.
  - Compare the commit with its parent (`commit.parents[0]` or `git.NULL_TREE` if it's the first commit) using `commit.diff()`.
  - Calculate statistics for each modified file:
    - File path.
    - File extension (resolved cleanly, e.g. `.py`, `.ts`, `.md`).
    - Lines added (`additions`).
    - Lines deleted (`deletions`).
  - Save the commit and file changes to the database using `DatabaseHelper`.
  - Once scanning is complete, update the `last_scanned_commit` in the database to the current repository HEAD.

## Definition of Done
- Engine code compiles under `ty` type check and adheres to Ruff styling.
- Verification tests:
  - Clonable private and public repository commits are successfully parsed.
  - Modified files, extensions, and lines added/deleted are saved correctly in the SQLite tables.
  - Subsequent scans of the same repository skip already-processed commits (verify via scan count output log).
