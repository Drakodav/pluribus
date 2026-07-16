import json
from collections.abc import Callable
from pathlib import Path

import git

from src.database import RepositoryStore
from src.extractor import GitExtractor


class RepositorySync:
    def __init__(self, store: RepositoryStore, extractor: GitExtractor):
        self.store = store
        self.extractor = extractor

    def get_author_emails(self) -> list[str]:
        """Retrieves known author emails cached in the database."""
        emails_str = self.store.get_config("author_emails")
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
        self.store.set_config("author_emails", json.dumps(emails))

    def get_ignored_emails(self) -> list[str]:
        """Retrieves user-ignored author emails cached in the database."""
        emails_str = self.store.get_config("ignored_emails")
        if emails_str:
            try:
                emails = json.loads(emails_str)
                if isinstance(emails, list):
                    return [str(e) for e in emails]
            except json.JSONDecodeError:
                pass
        return []

    def save_ignored_emails(self, emails: list[str]):
        """Caches ignored author emails list in the database config table."""
        self.store.set_config("ignored_emails", json.dumps(emails))

    def sync_repository(
        self,
        url: str,
        email_prompt_callback: Callable[[str, str], bool],
        is_local: bool = False,
    ) -> dict:
        """Syncs git history, prompts for emails, and stores to database.

        Returns:
            dict: The repository statistics after synchronization.
        """
        # Determine repo name to query existing since_commit
        if is_local:
            repo_name = Path(url).name
        else:
            repo_name = self.extractor.get_repo_name(url)

        existing_repos = self.store.get_all_repositories()
        repo_record = next((r for r in existing_repos if r.name == repo_name), None)
        since_commit = repo_record.last_scanned_commit if repo_record else None

        # Delegate pure git extraction
        parsed_commits, head_commit_hash, local_path = self.extractor.scan_repository(
            url, since_commit=since_commit, is_local=is_local
        )

        # Register repository in database
        repo_id = self.store.add_repository(
            name=repo_name, url=url, local_path=str(local_path)
        )

        # Load author and ignored email lists
        author_emails = self.get_author_emails()
        ignored_emails = self.get_ignored_emails()
        if not author_emails:
            try:
                repo = git.Repo(local_path)
                config_email = repo.config_reader().get_value("user", "email")
                if config_email:
                    author_emails = [str(config_email)]
                    self.save_author_emails(author_emails)
            except Exception:
                pass

        # Filter, prompt, and store commits and file changes
        for commit in parsed_commits:
            email = commit.author_email
            name = commit.author_name

            if email in ignored_emails:
                continue

            if email not in author_emails:
                is_me = email_prompt_callback(name, email)
                if is_me:
                    author_emails.append(email)
                    self.save_author_emails(author_emails)
                else:
                    ignored_emails.append(email)
                    self.save_ignored_emails(ignored_emails)
                    # Skip commit
                    continue

            # Add to database
            commit_db_id = self.store.add_commit(
                repo_id=repo_id,
                commit_hash=commit.hexsha,
                author_name=name,
                author_email=email,
                commit_date=commit.commit_date,
                message=commit.message,
            )

            # Add file changes
            for fc in commit.file_changes:
                self.store.add_file_change(
                    commit_id=commit_db_id,
                    file_path=fc.file_path,
                    additions=fc.additions,
                    deletions=fc.deletions,
                )

        # Update last scanned commit metadata
        self.store.update_repository_scanned(repo_id, head_commit_hash)

        return self.store.get_repo_stats(repo_id)
