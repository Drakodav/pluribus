import re
from datetime import datetime
from pathlib import Path

from src.database import RepositoryStore
from src.reports.base import BaseReport
from src.reports.filter import ChangeFilter

# Keyword mappings for clustering achievements
CATEGORIES = [
    {
        "name": "Feature Delivery",
        "keywords": [
            r"\bfeat\b",
            r"\badd\b",
            r"\bnew\b",
            r"\bimplement\b",
            r"\bcreate\b",
            r"\bintroduce\b",
        ],
    },
    {
        "name": "Refactoring & Architecture",
        "keywords": [
            r"\brefactor\b",
            r"\bclean\b",
            r"\bdecouple\b",
            r"\bseam\b",
            r"\bmove\b",
            r"\bstructure\b",
            r"\borganize\b",
        ],
    },
    {
        "name": "Bug Fixes & Stability",
        "keywords": [
            r"\bfix\b",
            r"\bbug\b",
            r"\bresolve\b",
            r"\bcorrect\b",
            r"\bcrash\b",
            r"\bissue\b",
        ],
    },
    {
        "name": "Performance & Optimization",
        "keywords": [
            r"\bperf\b",
            r"\boptimize\b",
            r"\bspeed\b",
            r"\bfast\b",
            r"\bcache\b",
        ],
    },
    {
        "name": "Testing & Documentation",
        "keywords": [
            r"\btest\b",
            r"\bpytest\b",
            r"\bdocs\b",
            r"\breadme\b",
            r"\bcomment\b",
        ],
    },
]


class AchievementsReport(BaseReport):
    def generate(
        self,
        store: RepositoryStore,
        repo_ids: list[int],
        output_file: Path,
        change_filter: ChangeFilter,
    ) -> None:
        """Generates achievements summary grouped by categories."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        repos = store.get_all_repositories()
        repos = [r for r in repos if r.id in repo_ids]

        if not repos:
            raise ValueError("No matching repositories found in database.")

        markdown_content = []
        markdown_content.append("# Achievement & Contribution Highlights\n")
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

            # Map commit id to its filtered file changes
            commit_changes = {}
            for fc in filtered_changes:
                commit_changes.setdefault(fc.commit_id, []).append(fc.file_path)

            # Group commits into categories
            grouped_commits = {cat["name"]: [] for cat in CATEGORIES}
            other_commits = []

            for commit in commits:
                message_lower = commit.message.lower()
                matched = False
                for cat in CATEGORIES:
                    # Match any keyword regex
                    if any(re.search(kw, message_lower) for kw in cat["keywords"]):
                        grouped_commits[cat["name"]].append(commit)
                        matched = True
                        break
                if not matched:
                    other_commits.append(commit)

            markdown_content.append(f"## Repository: {repo.name}")
            markdown_content.append(f"- **URL**: {repo.url}\n")

            # Render each category
            for cat_name in grouped_commits.keys():
                cat_commits = grouped_commits[cat_name]
                if not cat_commits:
                    continue

                markdown_content.append(f"### {cat_name}")
                for commit in cat_commits:
                    files = commit_changes.get(commit.id, [])
                    files_str = f" ({', '.join(files)})" if files else ""
                    hash_str = commit.hash[:7]
                    msg = commit.message.strip()
                    date_str = commit.commit_date
                    markdown_content.append(
                        f"- **`{hash_str}`**: {msg} on {date_str}{files_str}"
                    )
                markdown_content.append("")

            # Render "Other Contributions" if any
            if other_commits:
                markdown_content.append("### Other Contributions")
                for commit in other_commits:
                    files = commit_changes.get(commit.id, [])
                    files_str = f" ({', '.join(files)})" if files else ""
                    hash_str = commit.hash[:7]
                    msg = commit.message.strip()
                    date_str = commit.commit_date
                    markdown_content.append(
                        f"- **`{hash_str}`**: {msg} on {date_str}{files_str}"
                    )
                markdown_content.append("")

            markdown_content.append("---\n")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))
