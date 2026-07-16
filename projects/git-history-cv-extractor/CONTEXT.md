---
name: git-history-cv-extractor
alias: git-cv
description: CLI utility that scans Git repositories, stores commit/file changes in SQLite, and generates structured Markdown summaries for CV consumption.
stack: python cli
---

# Git History CV Extractor

A CLI utility that scans local or remote Git repositories to parse commit history, authors, diff statistics, and file change metrics, storing them in a local SQLite cache. It aggregates this data to generate structured Markdown summaries that can be consumed by downstream AI systems to construct or update a CV/resume.

## Language

**Repository**:
A Git repository configured to be scanned for contributor history.
_Avoid_: project, folder

**Commit**:
A parsed record of a specific Git commit from a tracked repository containing hash, date, message, and author credentials.
_Avoid_: revision, patch

**File Change**:
Line-level modification statistics (additions and deletions) extracted per file path within a single commit.
_Avoid_: diff, patch block

**Author Email Configuration**:
An approved list of git email addresses stored in the local config table used to filter and verify which commits belong to the user.
_Avoid_: user emails, aliases

**Ignored Emails Configuration**:
A list of git emails explicitly marked as not belonging to the user to prevent redundant command-line association prompts.
_Avoid_: blocked list, blacklisted emails

**Real Mode**:
An execution setting where repository clones and the primary SQLite cache are maintained under the production data paths.
_Avoid_: production mode

**Test Mode**:
An isolated execution setting where repository clones and database caches are targeted under separate testing directory structures.
_Avoid_: mock mode, sandbox

**Repository Synchronization**:
The process of cloning/updating a Git repository, extracting its commit history, filtering commits by approved author emails, prompting for unknown author emails, and storing the results in the database.
_Avoid_: ingestion loop, data writing.



# git-history-cv-extractor Checklist

- [x] Issue 001: Database Setup and Helpers
- [x] Issue 002: GitHub Authentication (gh CLI integration)
- [x] Issue 003: Git Extraction Engine (GitPython scanning & author matching)
- [x] Issue 004: Interactive Wizard CLI (Questionary & Markdown report)
- [ ] Issue 005: Unit Testing & Mock Verifications (pytest implementation)
