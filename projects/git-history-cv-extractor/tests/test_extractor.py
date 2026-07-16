import shutil
import tempfile
from pathlib import Path

import git
import pytest

from src.extractor import GitExtractor


@pytest.fixture
def temp_git_repo():
    # Setup temp dir
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir).resolve()

    # Initialize repo
    repo = git.Repo.init(repo_path)

    # Configure user name/email
    with repo.config_writer() as writer:
        writer.set_value("user", "name", "Test Contributor")
        writer.set_value("user", "email", "test@contributor.com")

    # Create a test file
    test_file = repo_path / "hello.py"
    test_file.write_text("print('hello')\n")

    # Add and commit
    repo.index.add([str(test_file)])
    author = git.Actor("Test Contributor", "test@contributor.com")
    repo.index.commit("Initial commit", author=author, committer=author)

    yield repo_path

    # Cleanup
    shutil.rmtree(temp_dir)


def test_git_extractor_extracts_commits(temp_git_repo):
    extractor = GitExtractor(repos_dir=temp_git_repo.parent / "repos")

    # Scan local repo
    parsed_commits, head_sha, _ = extractor.scan_repository(
        url=str(temp_git_repo), is_local=True
    )

    assert len(parsed_commits) == 1
    commit = parsed_commits[0]
    assert commit.hexsha == head_sha
    assert commit.author_name == "Test Contributor"
    assert commit.author_email == "test@contributor.com"
    assert commit.message.strip() == "Initial commit"
    assert len(commit.file_changes) == 1
    assert commit.file_changes[0].file_path == "hello.py"
    assert commit.file_changes[0].additions == 1
    assert commit.file_changes[0].deletions == 0


def test_git_extractor_since_commit(temp_git_repo):
    # Add a second commit
    repo = git.Repo(temp_git_repo)
    test_file2 = temp_git_repo / "world.py"
    test_file2.write_text("print('world')\n")
    repo.index.add([str(test_file2)])
    commit1_sha = repo.head.commit.hexsha
    author = git.Actor("Test Contributor", "test@contributor.com")
    repo.index.commit("Second commit", author=author, committer=author)
    commit2_sha = repo.head.commit.hexsha

    extractor = GitExtractor(repos_dir=temp_git_repo.parent / "repos")

    # Scan since the first commit
    parsed_commits, _, _ = extractor.scan_repository(
        url=str(temp_git_repo), since_commit=commit1_sha, is_local=True
    )

    assert len(parsed_commits) == 1
    assert parsed_commits[0].hexsha == commit2_sha
    assert parsed_commits[0].message.strip() == "Second commit"
