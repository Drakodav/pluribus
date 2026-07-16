from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.database import RepositoryStore
from src.reports.base import BaseReport
from src.reports.filter import ChangeFilter


@dataclass
class ExtStats:
    files: set[str] = field(default_factory=set)
    add: int = 0
    deletions: int = 0
    edits: int = 0


@dataclass
class DirStats:
    add: int = 0
    deletions: int = 0
    edits: int = 0


class TechStackReport(BaseReport):
    def generate(
        self,
        store: RepositoryStore,
        repo_ids: list[int],
        output_file: Path,
        change_filter: ChangeFilter,
    ) -> None:
        """Generates a technology profile report grouped by ext and directory."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        repos = store.get_all_repositories()
        repos = [r for r in repos if r.id in repo_ids]

        if not repos:
            raise ValueError("No matching repositories found in database.")

        markdown_content = []
        markdown_content.append("# Technology Stack & Activity Profile\n")
        markdown_content.append(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        for repo in repos:
            repo_id = repo.id
            if repo_id is None:
                continue

            commits = store.get_repository_commits(repo_id)
            if not commits:
                continue

            commit_ids = [c.id for c in commits if c.id is not None]
            all_file_changes = store.get_commits_file_changes(commit_ids)

            # Filter file changes using the ChangeFilter
            filtered_changes = [
                fc
                for fc in all_file_changes
                if change_filter.should_include(fc.file_path)
            ]

            if not filtered_changes:
                markdown_content.append(f"## Repository: {repo.name}")
                markdown_content.append("No code changes match the current filters.\n")
                markdown_content.append("---\n")
                continue

            # Aggregates by extension
            ext_stats = defaultdict(ExtStats)
            # Aggregates by directory path prefix (top + second level if present)
            dir_stats = defaultdict(DirStats)

            for fc in filtered_changes:
                # Extension
                ext = fc.file_extension.replace(".", "").upper()
                if ext == "NO-EXT":
                    ext = "PLAIN TEXT / NO EXTENSION"

                ext_stats[ext].files.add(fc.file_path)
                ext_stats[ext].add += fc.additions
                ext_stats[ext].deletions += fc.deletions
                ext_stats[ext].edits += 1

                # Directory grouping
                p = Path(fc.file_path)
                parts = p.parts
                if len(parts) > 1:
                    dir_prefix = "/".join(parts[:2])
                elif len(parts) == 1:
                    dir_prefix = "(root)"
                else:
                    dir_prefix = "unknown"

                dir_stats[dir_prefix].add += fc.additions
                dir_stats[dir_prefix].deletions += fc.deletions
                dir_stats[dir_prefix].edits += 1

            markdown_content.append(f"## Repository: {repo.name}")
            markdown_content.append(f"- **URL**: {repo.url}")
            num_files = len({fc.file_path for fc in filtered_changes})
            additions = sum(fc.additions for fc in filtered_changes)
            deletions = sum(fc.deletions for fc in filtered_changes)
            markdown_content.append(f"- **Total Active Files**: {num_files}")
            markdown_content.append(f"- **Total Lines Added**: {additions}")
            markdown_content.append(f"- **Total Lines Deleted**: {deletions}\n")

            # Render extensions table
            markdown_content.append("### Language & Extension Breakdown")
            markdown_content.append(
                "| Extension | Unique Files | Edits Count | "
                "Lines Added | Lines Deleted |"
            )
            markdown_content.append("|---|---|---|---|---|")
            for ext in sorted(ext_stats.keys()):
                stats = ext_stats[ext]
                n_files = len(stats.files)
                edits = stats.edits
                add = stats.add
                dels = stats.deletions
                markdown_content.append(
                    f"| `{ext}` | {n_files} | {edits} | +{add} | -{dels} |"
                )
            markdown_content.append("")

            # Render directories table
            markdown_content.append("### Directory & Module Activity")
            markdown_content.append(
                "| Directory / Path Prefix | Edits Count | "
                "Lines Added | Lines Deleted |"
            )
            markdown_content.append("|---|---|---|---|")
            for dir_name in sorted(dir_stats.keys()):
                stats = dir_stats[dir_name]
                edits = stats.edits
                add = stats.add
                dels = stats.deletions
                markdown_content.append(
                    f"| `{dir_name}` | {edits} | +{add} | -{dels} |"
                )
            markdown_content.append("")
            markdown_content.append("---\n")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))
