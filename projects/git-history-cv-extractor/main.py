import subprocess
import sys
from pathlib import Path

import git
import questionary

from src.auth import GitHubAuth
from src.database import RepositoryStore
from src.extractor import GitExtractor
from src.reports.filter import ChangeFilter
from src.reports.manager import ReportManager
from src.sync import RepositorySync


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


def run_reports_wizard(
    store: RepositoryStore, reports_dir: Path, project_path: Path
) -> None:
    """Prompts the user to configure and generate modular contribution reports."""
    repos = store.get_all_repositories()
    if not repos:
        print(
            "\n\033[1;31m[Error] No repositories found in the database. "
            "Ingest some first!\033[0m"
        )
        return

    # 1. Select Report Types
    choices = [
        questionary.Choice("Chronological Summary", "summary", checked=True),
        questionary.Choice("Technology Stack Profile", "tech_stack", checked=True),
        questionary.Choice(
            "Achievement & Contribution Highlights", "achievements", checked=True
        ),
    ]
    selected_reports = questionary.checkbox(
        "Select reports to generate:", choices=choices
    ).ask()

    if not selected_reports:
        print("\033[1;33m[Cancelled] No report types selected.\033[0m")
        return

    # 2. Select Filter Rules
    filter_mode = questionary.select(
        "Select file change exclusions/filters:",
        choices=[
            "Use Default Exclusions (ignores vendors, lockfiles, caches, assets)",
            "Add Custom Exclusions",
            "Disable Exclusions (includes all file changes in reports)",
        ],
    ).ask()

    if not filter_mode:
        print("\033[1;33m[Cancelled] Exclusions configuration aborted.\033[0m")
        return

    # Build ChangeFilter
    custom_patterns = None
    if "Add Custom Exclusions" in filter_mode:
        custom_input = questionary.text(
            "Enter custom glob patterns (comma-separated, e.g. *.json, *tests/*):"
        ).ask()
        if custom_input:
            custom_patterns = [p.strip() for p in custom_input.split(",") if p.strip()]

    # If disabled exclusions, pass a filter that includes everything
    if "Disable Exclusions" in filter_mode:

        class NoFilter(ChangeFilter):
            def should_include(self, file_path: str) -> bool:
                return True

        change_filter = NoFilter()
    else:
        change_filter = ChangeFilter(custom_patterns)

    # 3. Generate Reports
    repo_ids = [r.id for r in repos if r.id is not None]
    manager = ReportManager()

    try:
        paths = manager.generate_reports(
            store, repo_ids, reports_dir, selected_reports, change_filter
        )
        print("\n\033[1;32m[Success] Reports generated successfully!\033[0m")
        for r_type, path in paths.items():
            rel_path = path.relative_to(project_path)
            print(
                f"  - {r_type.replace('_', ' ').title()}: \033[1;36m{rel_path}\033[0m"
            )
    except Exception as e:
        print(f"\033[1;31m[Error during report generation] {e}\033[0m")


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
    store = RepositoryStore(db_path)
    auth_helper = GitHubAuth(store)
    workspace_root = project_dir.parent.parent

    # Mode-based initialization
    if is_test:
        try:
            repo = git.Repo(workspace_root)
            gh_user = str(
                repo.config_reader().get_value("user", "name") or "local-user"
            )
        except Exception:
            gh_user = "local-user"
        token = None
        extractor = GitExtractor(repos_dir, token)
        sync_helper = RepositorySync(store, extractor)

        # Auto-ingest local workspace read-only on startup
        print(
            f"\n[Test Mode] Automatically scanning local repository: "
            f"'{workspace_root.name}'..."
        )
        try:

            def prompt_email(name: str, email: str) -> bool:
                prompt_msg = (
                    f"[Test Mode] Found commits by '{name} <{email}>'. Is this you?"
                )
                res = questionary.confirm(prompt_msg, default=True).ask()
                return bool(res)

            sync_helper.sync_repository(
                str(workspace_root), prompt_email, is_local=True
            )
            print(
                "\033[1;32m[Success] Automatically Ingested Local Workspace "
                "History!\033[0m"
            )
        except Exception as e:
            print(f"\033[1;31m[Test Mode Setup Error] {e}\033[0m")
    else:
        if not auth_helper.check_gh_cli():
            print("\033[1;31m[Error] GitHub CLI (gh) is not installed.\033[0m")
            print("Please install it from https://cli.github.com/ and login first.")
            sys.exit(1)

        try:
            token = auth_helper.authenticate()
        except RuntimeError as e:
            print(f"\033[1;31m[Auth Error] {e}\033[0m")
            sys.exit(1)

        gh_user = get_gh_username()
        extractor = GitExtractor(repos_dir, token)
        sync_helper = RepositorySync(store, extractor)

    # Console Wizard loop
    while True:
        repo_count = store.get_repository_count()

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
                "Generate Contribution Reports...",
                "Exit",
            ],
        ).ask()

        if choice == "Authenticate & Check Token Status":
            if is_test:
                print(
                    "\033[1;33m[Test Mode] Authentication is bypassed. "
                    "No active token cached.\033[0m"
                )
                continue
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

                stats = sync_helper.sync_repository(url, prompt_email)
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
            repos = store.get_all_repositories()
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
                stats = store.get_repo_stats(repo_id)
                print(
                    "{:<20} | {:<8} | {:<12} | {:<12}".format(
                        r.name[:20],
                        stats["total_commits"],
                        f"+{stats['total_additions']}",
                        f"-{stats['total_deletions']}",
                    )
                )

        elif choice == "Generate Contribution Reports...":
            run_reports_wizard(store, reports_dir, project_dir)

        elif choice == "Exit" or choice is None:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
