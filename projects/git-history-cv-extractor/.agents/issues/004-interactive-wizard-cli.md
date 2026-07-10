# Issue 004: Interactive Wizard CLI & Markdown Exporter

* **Status**: Pending


## Overview
We need an interactive, wizard-based console interface to guide the user through authentication, ingesting repositories, checking database statistics, and exporting contribution summaries for AI ingestion.

We will use the **`questionary`** library to implement a premium console menu with arrow-key selections.

## Requirements

### 1. Startup Mode Prompt
Upon starting the tool, the CLI must prompt the user to select their running mode:
* **Test Mode**: Uses the database and workspace paths under `output/test/`.
* **Real Mode**: Uses the database and workspace paths under `output/real/`.

This choice sets the active subdirectory path for all operations.

### 2. The Interactive Console Loop (using Questionary)
Design a text menu loop showing:
* **Current Status Banner**: Display the active mode (e.g. `[Test Mode]` or `[Real Mode]`), the login status (e.g. `Logged in as: <username>`), and the number of ingested repositories in that mode.
* **Menu Options**:
  1. **Authenticate with GitHub**: Runs the `gh CLI` check and caches the token.
  2. **Add / Sync a Repository**: Prompts the user for a Git URL, performs the clone/fetch scan, and updates the active mode database.
  3. **Show Database Stats**: Prints a summarized dashboard of all ingested repositories in the active mode (total commits, lines of code changed, language breakdown by file extensions).
  4. **Generate Markdown Summary**: Generates a formatted Markdown file summarizing commits, files worked on, and description details, saved to `<mode_dir>/reports/contributions_summary.md`.
  5. **Exit**: Exits the program.

### 3. Markdown Exporter Details (Repository Grouped)
Implement a report generation utility that groups your achievements by repository:
* Retrieve all commits and file change metrics for the author from the active SQLite database.
* Group commits by repository and write a structured Markdown file.
* For each repository, format the following details:
  - **Repository Name and Remote URL**
  - **Auto-detected Tech Stack**: Inferred from the file extensions modified by the author in this repository (e.g., `Python, Shell, Markdown`).
  - **Activity Period**: First commit date to last commit date.
  - **Summary Metrics**: Total commits, files touched, total lines added/deleted.
  - **Grouped Log**: A list of commits sorted chronologically, showing:
    - Commit date and hash.
    - Commit message.
    - Files touched, including line count change metrics per file.

## Definition of Done
- Console script complies with Ruff formatting/linting and `ty` type checking.
- Verification steps:
  - Launching the tool prompts for Test vs. Real Mode.
  - Selecting "Show Database Stats" prints a correctly aligned summary.
  - Selecting "Generate Markdown Summary" successfully creates a readable Markdown file detailing contributions.
