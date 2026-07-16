import re
from dataclasses import dataclass
from pathlib import Path

import git


@dataclass
class GitFileChange:
    file_path: str
    additions: int
    deletions: int


@dataclass
class GitCommit:
    hexsha: str
    author_name: str
    author_email: str
    commit_date: str  # ISO 8601 string: YYYY-MM-DD HH:MM:SS
    message: str
    file_changes: list[GitFileChange]


class GitExtractor:
    def __init__(
        self,
        repos_dir: Path,
        token: str | None = None,
    ):
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

    def scan_repository(
        self,
        url: str,
        since_commit: str | None = None,
        is_local: bool = False,
    ) -> tuple[list[GitCommit], str, Path]:
        """Syncs the repository locally and parses all un-scanned commits.

        Returns:
            tuple[list[GitCommit], str, Path]: A tuple containing the parsed
            commits, the latest commit hash (head.commit.hexsha), and the local path.
        """
        if is_local:
            local_path = Path(url)
            repo = git.Repo(local_path)
        else:
            repo, local_path = self.clone_or_update(url)

        head_commit = repo.head.commit

        # If already up to date, return empty list
        if since_commit and head_commit.hexsha == since_commit:
            return [], head_commit.hexsha, local_path

        # Walk commit history back to the since_commit
        commits_to_scan = []
        for commit in repo.iter_commits():
            if since_commit and commit.hexsha == since_commit:
                break
            commits_to_scan.append(commit)

        # Process commits from oldest to newest
        commits_to_scan.reverse()

        parsed_commits = []
        for commit in commits_to_scan:
            email = str(commit.author.email or "unknown@email.com")
            name = str(commit.author.name or "Unknown Author")
            commit_date_str = commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S")
            commit_message_str = str(
                commit.message.decode("utf-8")
                if isinstance(commit.message, bytes)
                else (commit.message or "")
            )

            file_changes = []
            try:
                files_stats = commit.stats.files
                for filepath, stats in files_stats.items():
                    file_changes.append(
                        GitFileChange(
                            file_path=str(filepath),
                            additions=stats.get("insertions", 0),
                            deletions=stats.get("deletions", 0),
                        )
                    )
            except Exception:
                pass

            parsed_commits.append(
                GitCommit(
                    hexsha=commit.hexsha,
                    author_name=name,
                    author_email=email,
                    commit_date=commit_date_str,
                    message=commit_message_str,
                    file_changes=file_changes,
                )
            )

        return parsed_commits, head_commit.hexsha, local_path
