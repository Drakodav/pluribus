import json
import re
from collections.abc import Callable
from pathlib import Path

import git
from sqlmodel import Session

from database import DatabaseHelper, Repository


class GitExtractor:
    def __init__(
        self,
        db_helper: DatabaseHelper,
        repos_dir: Path,
        token: str | None = None,
    ):
        self.db_helper = db_helper
        self.repos_dir = repos_dir
        self.token = token
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def get_repo_name(self, url: str) -> str:
        """Extracts the repository name from a git URL."""
        match = re.search(r"/([^/]+?)(?:\.git)?$", url)
        if match:
            return match.group(1)
        raise ValueError(f"Invalid Git URL format: {url}")

    def get_authenticated_url(self, url: str) -> str:
        """Appends the authentication token to HTTPS URLs."""
        if not self.token or not url.startswith("https://"):
            return url
        # Insert token into HTTPS URL: https://<token>@github.com/...
        return re.sub(r"https://(github\.com/)", f"https://{self.token}@\\1", url)

    def clone_or_update(self, url: str) -> tuple[git.Repo, Path]:
        """Clones a repository if missing, or pulls/fetches latest updates."""
        repo_name = self.get_repo_name(url)
        local_path = self.repos_dir / repo_name

        if not local_path.exists():
            clone_url = self.get_authenticated_url(url)
            repo = git.Repo.clone_from(clone_url, local_path)
        else:
            repo = git.Repo(local_path)
            try:
                repo.remotes.origin.pull()
            except git.GitCommandError:
                # Fallback to fetch if pull has merge issues/divergences
                repo.remotes.origin.fetch()

        return repo, local_path

    def get_author_emails(self) -> list[str]:
        """Retrieves known author emails cached in the database."""
        emails_str = self.db_helper.get_config("author_emails")
        if emails_str:
            try:
                emails = json.loads(emails_str)
                if isinstance(emails, list):
                    return [str(e) for e in emails]
            except json.JSONDecodeError:
                pass
        return []

    def save_author_emails(self, emails: list[str]):
        """Caches approved author emails list in the database config table."""
        self.db_helper.set_config("author_emails", json.dumps(emails))

    def scan_repository(
        self, url: str, email_prompt_callback: Callable[[str, str], bool]
    ) -> dict:
        """Syncs the repository locally and parses all un-scanned commits."""
        repo, local_path = self.clone_or_update(url)
        repo_name = self.get_repo_name(url)

        # Register repository in database
        repo_id = self.db_helper.add_repository(
            name=repo_name, url=url, local_path=str(local_path)
        )

        # Read last scanned commit
        with Session(self.db_helper.engine) as session:
            db_repo = session.get(Repository, repo_id)
            last_scanned = db_repo.last_scanned_commit if db_repo else None

        head_commit = repo.head.commit

        # If already up to date, skip scanning
        if last_scanned and head_commit.hexsha == last_scanned:
            return self.db_helper.get_repo_stats(repo_id)

        # Walk commit history back to the last scanned commit
        commits_to_scan = []
        for commit in repo.iter_commits():
            if last_scanned and commit.hexsha == last_scanned:
                break
            commits_to_scan.append(commit)

        # Process commits from oldest to newest
        commits_to_scan.reverse()

        # Initialize email mappings
        author_emails = self.get_author_emails()
        if not author_emails:
            try:
                config_email = repo.config_reader().get_value("user", "email")
                if config_email:
                    author_emails = [str(config_email)]
                    self.save_author_emails(author_emails)
            except Exception:
                pass

        for commit in commits_to_scan:
            email = str(commit.author.email or "unknown@email.com")
            name = str(commit.author.name or "Unknown Author")

            # Check dynamic email mappings
            if email not in author_emails:
                is_me = email_prompt_callback(name, email)
                if is_me:
                    author_emails.append(email)
                    self.save_author_emails(author_emails)
                else:
                    # Skip commit if not written by the user
                    continue

            commit_date_str = commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S")
            commit_message_str = str(
                commit.message.decode("utf-8")
                if isinstance(commit.message, bytes)
                else (commit.message or "")
            )

            commit_db_id = self.db_helper.add_commit(
                repo_id=repo_id,
                commit_hash=commit.hexsha,
                author_name=name,
                author_email=email,
                commit_date=commit_date_str,
                message=commit_message_str,
            )

            # Extract additions/deletions statistics per file
            try:
                files_stats = commit.stats.files
                for filepath, stats in files_stats.items():
                    self.db_helper.add_file_change(
                        commit_id=commit_db_id,
                        file_path=str(filepath),
                        additions=stats.get("insertions", 0),
                        deletions=stats.get("deletions", 0),
                    )
            except Exception:
                pass

        # Update last scanned metadata
        self.db_helper.update_repository_scanned(repo_id, head_commit.hexsha)

        return self.db_helper.get_repo_stats(repo_id)
