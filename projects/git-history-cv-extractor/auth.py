import shutil
import subprocess

from database import DatabaseHelper


class GitHubAuth:
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper

    def check_gh_cli(self) -> bool:
        """Checks if the GitHub CLI (gh) is installed on the system path."""
        return shutil.which("gh") is not None

    def get_token(self) -> str | None:
        """Resolves the GitHub token from the database cache or gh CLI.

        Returns:
            str | None: The active token, or None if not authenticated.
        """
        # 1. Check SQLite config table first
        token = self.db_helper.get_config("github_token")
        if token:
            return token

        # 2. Check gh CLI
        if not self.check_gh_cli():
            return None

        try:
            # Run gh auth token to retrieve token
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=True,
            )
            token = result.stdout.strip()
            if token:
                # Cache the token in the database
                self.db_helper.set_config("github_token", token)
                return token
        except subprocess.CalledProcessError:
            pass

        return None

    def clear_cached_token(self):
        """Clears the cached token in the database.

        Forces re-authentication on the next fetch/pull.
        """
        self.db_helper.set_config("github_token", "")

    def authenticate(self) -> str:
        """Validates that gh CLI is installed and authenticated.

        Returns:
            str: The active auth token.

        Raises:
            RuntimeError: If gh is missing or not authenticated.
        """
        if not self.check_gh_cli():
            raise RuntimeError(
                "GitHub CLI (gh) is not installed. Please install "
                "it from https://cli.github.com/ and try again."
            )

        token = self.get_token()
        if not token:
            raise RuntimeError(
                "GitHub CLI (gh) is not authenticated. Please run: gh auth login"
            )
        return token
