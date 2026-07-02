# Agent Memory & Session Logs

This directory serves as the persistent memory store for AI agents working in the Pluribus repository. 

To prevent context-loss ("amnesia") between different sessions or conversations, agents must document their progress in this folder.

## Session Log Template

When completing a task or wrapping up a conversation, append an entry to the current log file (e.g., `docs/memory/session-log.md`) following this format:

```markdown
## [YYYY-MM-DD] Session: [Short Summary of Task]
* **Agent**: [Agent Name or Version]

### What Was Accomplished
- Detailed bullet points of files created, modified, or deleted.
- Build commands run and verification outcomes.

### Architectural Decisions & Changes
- Any adjustments to configurations, file layouts, or schemas.
- References to new or updated ADRs in `docs/architecture/`.

### Key Learnings & Quirks
- Strange behaviors, unexpected bugs, or workarounds discovered.
- Helpful command snippets or dependency notes.

### Future Work / Next Steps
- What the user or subsequent agents should focus on next.
- Unresolved bugs or pending items.
```
