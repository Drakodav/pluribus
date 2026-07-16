from datetime import datetime
from pathlib import Path

from src.database import RepositoryStore
from src.reports.base_generator import BaseReport
from src.reports.filter import ChangeFilter


class SummaryReport(BaseReport):
    def generate(
        self,
        store: RepositoryStore,
        repo_ids: list[int],
        output_file: Path,
        change_filter: ChangeFilter,
    ) -> None:
        """Generates a chronological markdown summary of repository edits."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        repos = store.get_all_repositories()
        repos = [r for r in repos if r.id in repo_ids]

        if not repos:
            raise ValueError("No matching repositories found in database.")

        markdown_content = []
        markdown_content.append("# Monorepo Contribution Summary\n")
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

            # Re-calculate statistics based on filtered edits
            total_additions = sum(fc.additions for fc in filtered_changes)
            total_deletions = sum(fc.deletions for fc in filtered_changes)
            unique_files = {fc.file_path for fc in filtered_changes}
            files_changed = len(unique_files)

            # Detect active extensions
            extensions = set()
            for fc in filtered_changes:
                if fc.file_extension != "no-ext":
                    ext = fc.file_extension.replace(".", "").upper()
                    extensions.add(ext)

            tech_stack = ", ".join(sorted(extensions)) if extensions else "Unknown"
            activity_start = commits[0].commit_date
            activity_end = commits[-1].commit_date

            markdown_content.append(f"## Repository: {repo.name}")
            markdown_content.append(f"- **URL**: {repo.url}")
            markdown_content.append(f"- **Tech Stack**: {tech_stack}")
            markdown_content.append(
                f"- **Activity Period**: {activity_start} to {activity_end}"
            )
            markdown_content.append(
                f"- **Summary**: {len(commits)} commits, "
                f"{files_changed} files changed, "
                f"+{total_additions} / -{total_deletions} lines\n"
            )

            markdown_content.append("### Commits Log")
            for commit in commits:
                markdown_content.append(
                    f"#### Commit `{commit.hash[:7]}` on {commit.commit_date}"
                )
                markdown_content.append(f"**Message**: {commit.message.strip()}\n")

                c_changes = [fc for fc in filtered_changes if fc.commit_id == commit.id]
                if c_changes:
                    markdown_content.append("**Files Touched**:")
                    for fc in c_changes[:5]:
                        markdown_content.append(
                            f"- `{fc.file_path}` (+{fc.additions}, -{fc.deletions})"
                        )
                    if len(c_changes) > 5:
                        markdown_content.append(
                            f"- ... (+{len(c_changes) - 5} more files)"
                        )
                markdown_content.append("")  # Spacer

            markdown_content.append("---\n")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))
