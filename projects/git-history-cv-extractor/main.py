import subprocess
import sys
from datetime import datetime
from pathlib import Path

import questionary
from sqlmodel import Session, select

from auth import GitHubAuth
from database import Commit, DatabaseHelper, FileChange, Repository
from extractor import GitExtractor


def get_gh_username() -> str:
    """Retrieves the username of the currently authenticated GitHub CLI user."""
    try:
        result = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown-user"


def generate_markdown_report(
    db_helper: DatabaseHelper, output_file: Path, project_path: Path
):
    """Compiles all stored commits and metrics into a formatted Markdown file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with Session(db_helper.engine) as session:
        repos = session.exec(select(Repository)).all()
        if not repos:
            print(
                "\n\033[1;31m[Error] No repositories found in the database. "
                "Ingest some first!\033[0m"
            )
            return

        markdown_content = []
        markdown_content.append("# Monorepo Contribution Summary\n")
        markdown_content.append(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        for repo in repos:
            repo_id = repo.id
            if repo_id is None:
                continue

            commits = session.exec(
                select(Commit)
                .where(Commit.repo_id == repo_id)
                .order_by(Commit.commit_date)
            ).all()

            if not commits:
                continue

            stats = db_helper.get_repo_stats(repo_id)

            commit_ids = [c.id for c in commits if c.id is not None]
            file_changes = session.exec(
                select(FileChange).where(FileChange.commit_id.in_(commit_ids))  # type: ignore
            ).all()

            # Dynamic tech stack detection based on extensions modified
            extensions = set()
            for fc in file_changes:
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
                f"- **Summary**: {stats['total_commits']} commits, "
                f"{stats['files_changed']} files changed, "
                f"+{stats['total_additions']} / -{stats['total_deletions']} lines\n"
            )

            markdown_content.append("### Commits Log")
            for commit in commits:
                markdown_content.append(
                    f"#### Commit `{commit.hash[:7]}` on {commit.commit_date}"
                )
                markdown_content.append(f"**Message**: {commit.message.strip()}\n")

                c_changes = [fc for fc in file_changes if fc.commit_id == commit.id]
                if c_changes:
                    markdown_content.append("**Files Touched**:")
                    for fc in c_changes:
                        markdown_content.append(
                            f"- `{fc.file_path}` (+{fc.additions}, -{fc.deletions})"
                        )
                markdown_content.append("")  # Spacer

            markdown_content.append("---\n")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))

        rel_path = output_file.relative_to(project_path)
        print(f"\n\033[1;32m[Success] Report generated at: {rel_path}\033[0m")


def main():
    print("\033[1;36m====================================================\033[0m")
    print("\033[1;36m       Git History CV Extractor Console Wizard      \033[0m")
    print("\033[1;36m====================================================\033[0m\n")

    # Mode selection
    mode = questionary.select(
        "Select active running mode:",
        choices=[
            "Test Mode (uses output/test/ sandbox)",
            "Real Mode (uses output/real/ workspace)",
        ],
    ).ask()

    if not mode:
        print("Exit.")
        sys.exit(0)

    is_test = "Test Mode" in mode
    mode_str = "test" if is_test else "real"

    project_dir = Path(__file__).resolve().parent
    mode_dir = project_dir / "output" / mode_str

    db_path = mode_dir / ("test_extractor.db" if is_test else "extractor.db")
    repos_dir = mode_dir / "repos"
    reports_dir = mode_dir / "reports"

    # Initialize helpers
    db_helper = DatabaseHelper(db_path)
    auth_helper = GitHubAuth(db_helper)

    if not auth_helper.check_gh_cli():
        print("\033[1;31m[Error] GitHub CLI (gh) is not installed.\033[0m")
        print("Please install it from https://cli.github.com/ and login first.")
        sys.exit(1)

    # Resolve token credentials
    token: str | None = None
    try:
        token = auth_helper.authenticate()
    except RuntimeError as e:
        print(f"\033[1;31m[Auth Error] {e}\033[0m")
        sys.exit(1)

    gh_user = get_gh_username()
    extractor = GitExtractor(db_helper, repos_dir, token)

    # Console Wizard loop
    while True:
        with Session(db_helper.engine) as session:
            repo_count = len(session.exec(select(Repository)).all())

        print("\n\033[1;33m----------------------------------------------------\033[0m")
        print(
            f"Mode: \033[1;32m{mode_str.upper()}\033[0m | "
            f"User: \033[1;32m{gh_user}\033[0m | "
            f"Ingested Repos: \033[1;32m{repo_count}\033[0m"
        )
        print("\033[1;33m----------------------------------------------------\033[0m")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Authenticate & Check Token Status",
                "Add / Sync a Git Repository",
                "Show Database Statistics",
                "Generate Markdown Contribution Summary",
                "Exit",
            ],
        ).ask()

        if choice == "Authenticate & Check Token Status":
            try:
                auth_helper.clear_cached_token()
                fresh_token = auth_helper.authenticate()
                print(
                    f"\033[1;32m[Success] Successfully authenticated! "
                    f"Token length: {len(fresh_token)}\033[0m"
                )
            except RuntimeError as e:
                print(f"\033[1;31m[Error] {e}\033[0m")

        elif choice == "Add / Sync a Git Repository":
            url = questionary.text("Enter repository Git URL (HTTPS or SSH):").ask()
            if not url:
                continue

            try:
                repo_name = extractor.get_repo_name(url)
                print(f"\nIngesting history for repository: '{repo_name}'...")

                def prompt_email(name: str, email: str) -> bool:
                    prompt_msg = (
                        f"Encountered commits authored by '{name} <{email}>'. "
                        "Is this you?"
                    )
                    res = questionary.confirm(prompt_msg, default=True).ask()
                    return bool(res)

                stats = extractor.scan_repository(url, prompt_email)
                print(
                    f"\033[1;32m[Success] Ingested '{repo_name}' successfully!\033[0m"
                )
                print(f"  Total Commits: {stats['total_commits']}")
                print(f"  Files Touched: {stats['files_changed']}")
                print(f"  Lines Added:   +{stats['total_additions']}")
                print(f"  Lines Deleted: -{stats['total_deletions']}")
            except Exception as e:
                print(f"\033[1;31m[Error during sync] {e}\033[0m")

        elif choice == "Show Database Statistics":
            with Session(db_helper.engine) as session:
                repos = session.exec(select(Repository)).all()
            if not repos:
                print("\033[1;31mNo repositories found in database.\033[0m")
                continue

            print(
                "\n\033[1;36m{:<20} | {:<8} | {:<12} | {:<12}\033[0m".format(
                    "Repository", "Commits", "Additions", "Deletions"
                )
            )
            print("-" * 62)
            for r in repos:
                repo_id = r.id
                if repo_id is None:
                    continue
                stats = db_helper.get_repo_stats(repo_id)
                print(
                    "{:<20} | {:<8} | {:<12} | {:<12}".format(
                        r.name[:20],
                        stats["total_commits"],
                        f"+{stats['total_additions']}",
                        f"-{stats['total_deletions']}",
                    )
                )

        elif choice == "Generate Markdown Contribution Summary":
            report_file = reports_dir / "contributions_summary.md"
            generate_markdown_report(db_helper, report_file, project_dir)

        elif choice == "Exit" or choice is None:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
