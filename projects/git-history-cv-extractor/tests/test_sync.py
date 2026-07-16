import shutil
import tempfile
from pathlib import Path

import pytest

from src.database import RepositoryStore
from src.extractor import GitCommit, GitExtractor, GitFileChange
from src.sync import RepositorySync


class FakeExtractor(GitExtractor):
    def __init__(
        self, commits_to_return, head_sha="abc1234", local_path=Path("/tmp/fake-repo")
    ):
        super().__init__(Path("/tmp/fake-repos"))
        self.commits_to_return = commits_to_return
        self.head_sha = head_sha
        self.local_path = local_path
        self.scanned_since = None

    def get_repo_name(self, url):
        return "fake-repo"

    def scan_repository(self, url, since_commit=None, is_local=False):
        self.scanned_since = since_commit
        return self.commits_to_return, self.head_sha, self.local_path


@pytest.fixture
def store():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    store = RepositoryStore(db_path)
    yield store
    shutil.rmtree(temp_dir)


def test_sync_repository_successful_sync(store):
    # Setup test data
    file_change = GitFileChange(file_path="foo.py", additions=10, deletions=2)
    commit = GitCommit(
        hexsha="sha123",
        author_name="Me",
        author_email="me@email.com",
        commit_date="2026-07-16 12:00:00",
        message="A good commit",
        file_changes=[file_change],
    )

    fake_extractor = FakeExtractor([commit], head_sha="sha123")
    sync = RepositorySync(store, fake_extractor)

    # Pre-configure approved email
    sync.save_author_emails(["me@email.com"])

    # Callback should not be called since me@email.com is already approved
    callback_called = False

    def prompt_callback(name, email):
        nonlocal callback_called
        callback_called = True
        return True

    stats = sync.sync_repository(
        "https://github.com/test/fake-repo.git", prompt_callback
    )

    assert callback_called is False
    assert stats["total_commits"] == 1
    assert stats["files_changed"] == 1
    assert stats["total_additions"] == 10
    assert stats["total_deletions"] == 2

    # Verify saved repo
    repos = store.get_all_repositories()
    assert len(repos) == 1
    assert repos[0].name == "fake-repo"
    assert repos[0].last_scanned_commit == "sha123"


def test_sync_repository_prompt_callback(store):
    file_change = GitFileChange(file_path="foo.py", additions=5, deletions=1)
    commit = GitCommit(
        hexsha="sha456",
        author_name="Unknown",
        author_email="unknown@email.com",
        commit_date="2026-07-16 12:00:00",
        message="Another commit",
        file_changes=[file_change],
    )

    fake_extractor = FakeExtractor([commit], head_sha="sha456")
    sync = RepositorySync(store, fake_extractor)

    # Callback approves the email
    def prompt_callback(name, email):
        assert name == "Unknown"
        assert email == "unknown@email.com"
        return True

    stats = sync.sync_repository(
        "https://github.com/test/fake-repo.git", prompt_callback
    )

    assert stats["total_commits"] == 1
    # Verify email is now approved
    assert "unknown@email.com" in sync.get_author_emails()


def test_sync_repository_ignore_callback(store):
    file_change = GitFileChange(file_path="foo.py", additions=5, deletions=1)
    commit = GitCommit(
        hexsha="sha456",
        author_name="Unknown",
        author_email="unknown@email.com",
        commit_date="2026-07-16 12:00:00",
        message="Another commit",
        file_changes=[file_change],
    )

    fake_extractor = FakeExtractor([commit], head_sha="sha456")
    sync = RepositorySync(store, fake_extractor)

    # Callback rejects the email (not me)
    def prompt_callback(name, email):
        return False

    stats = sync.sync_repository(
        "https://github.com/test/fake-repo.git", prompt_callback
    )

    # Commit should be skipped, so total_commits is 0
    assert stats["total_commits"] == 0
    assert "unknown@email.com" in sync.get_ignored_emails()
