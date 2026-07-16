# PRD: Issue 009 — CLI Wizard Integration for AI Report Analysis

## Goal
Integrate an AI-powered report analysis runner option into the Console Wizard CLI (`main.py`). The runner will invoke a configurable command line agent (such as `agy` or a local Python-based SDK script) to process the generated reports and save structured markdown outputs in `reports/ai/`.

## Proposed Requirements & Flow

1. **Top-Level Menu Option**:
   - Add `"Run AI Analysis on Reports..."` to the `main.py` console select menu.

2. **Pre-requisite Validation**:
   - When selected, check if `contributions_summary.md`, `technology_profile.md`, or `achievements_highlights.md` exist in the target reports directory.
   - If no report files are found, prompt the user: `"No generated reports found. Would you like to generate them now?"` and route them to the report generation wizard first.

3. **Prompt Selections Menu**:
   - Present a checkbox list of built-in analysis categories to choose from:
     - `STAR Accomplishments`: Summarize accomplishments as high-impact resume bullets using the STAR method. Naming: `ai/star_accomplishments.md`.
     - `Technology Profile`: Profile core languages, frameworks, and active directories. Naming: `ai/technology_profile_analysis.md`.
     - `Knowledge Condenser`: Analyze major architectural decisions and code refactoring. Naming: `ai/knowledge_condensation.md`.
     - `Custom Prompt`: Prompts the user to enter their own custom instructions and prompts for a custom filename (saving to `ai/<custom_name>.md`).

4. **Under-the-Hood Subprocess Invocation**:
   - Expose a configurable command template (e.g. `python -m src.reports.ai_agent --prompt "{prompt}" --reports-dir "{reports_dir}" --output "{output_file}"` or `agy run ...`).
   - Run the subprocess turn-by-turn for each selected analysis, showing progress indicators.
   - Output files must be strictly confined under the `reports/ai/` directory.

## Verification Plan
- Unit tests validating the analysis trigger logic and pre-requisite directory check behavior.
- Manual execution in Test Mode to trigger the command runner and assert that outputs are saved to the correct paths under `reports/ai/`.
