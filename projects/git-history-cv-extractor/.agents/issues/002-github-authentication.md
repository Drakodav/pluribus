# Issue 002: GitHub Authentication (gh CLI integration)

* **Status**: Completed
* **Implementation Commit**: `PENDING`




## Overview
To clone and pull private repositories, the tool needs a valid GitHub Access Token. We will leverage the official GitHub CLI (`gh`) to handle authentication, ensuring a secure and lightweight setup.

The tool will demand that the `gh` CLI is installed and authenticated beforehand.

## Requirements

### 1. GitHub CLI Check & Token Acquisition
Implement a `GitHubAuth` helper class:
* **Check Installation**: Verify that the `gh` executable is available on the system path. If not, print a clear error message: *"GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/ and try again."* and terminate the wizard.
* **Retrieve Token**:
  - Run the subprocess command `gh auth token` (or `gh config get -h github.com oauth_token` as fallback).
  - If the command succeeds (returns exit code 0), retrieve and parse the output token.
  - If the command fails, display an error: *"Please authenticate with GitHub first by running: gh auth login"* and exit.

### 2. Cache Token
* Once the token is queried from the `gh` CLI, cache it in the SQLite `config` table under the key `github_token` to avoid spawning subprocesses for every subsequent repository action.
* In future runs, verify if the cached token is still valid. If not (e.g. clone returns authentication error), prompt the user to run `gh auth login` again and refresh the token.

## Definition of Done
- Auth module complies with Ruff style standards and `ty` type checking.
- Successful verification:
  - If `gh` is authenticated, the tool resolves the token cleanly and proceeds.
  - If `gh` is not authenticated, the tool fails gracefully with clear user instructions.
