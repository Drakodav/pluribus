import shutil
import tempfile
from pathlib import Path

import pytest

from src.database import RepositoryStore
from src.reports.achievements_generator import AchievementsReport
from src.reports.filter import ChangeFilter
from src.reports.manager import ReportManager
from src.reports.summary_generator import SummaryReport
from src.reports.tech_stack_generator import TechStackReport


@pytest.fixture
def test_env():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    store = RepositoryStore(db_path)

    # Add a test repo
    repo_id = store.add_repository(
        "test-repo", "https://github.com/foo/bar.git", "/tmp/bar"
    )

    # Add commits
    c1 = store.add_commit(
        repo_id,
        "sha1",
        "Me",
        "me@email.com",
        "2026-07-16 12:00:00",
        "feat: implement first feature",
    )
    c2 = store.add_commit(
        repo_id,
        "sha2",
        "Me",
        "me@email.com",
        "2026-07-16 13:00:00",
        "refactor(git-cv): clean up logic",
    )
    c3 = store.add_commit(
        repo_id,
        "sha3",
        "Me",
        "me@email.com",
        "2026-07-16 14:00:00",
        "docs: update docs",
    )
    c4 = store.add_commit(
        repo_id,
        "sha4",
        "Me",
        "me@email.com",
        "2026-07-16 15:00:00",
        "feat: commit with many files",
    )

    # Add file changes (some matching default exclusion patterns)
    store.add_file_change(c1, "src/main.py", 10, 2)
    store.add_file_change(c1, "package-lock.json", 100, 100)  # Excluded
    store.add_file_change(c2, "src/reports/filter.py", 5, 0)
    store.add_file_change(c2, "node_modules/lodash/index.js", 20, 20)  # Excluded
    store.add_file_change(c3, "README.md", 2, 1)

    # Add 7 files to c4 to trigger truncation
    for i in range(7):
        store.add_file_change(c4, f"src/file_{i}.py", 1, 1)

    yield store, repo_id, Path(temp_dir)

    shutil.rmtree(temp_dir)


def test_summary_report(test_env):
    store, repo_id, temp_dir = test_env
    output_file = temp_dir / "summary.md"
    change_filter = ChangeFilter()

    report = SummaryReport()
    report.generate(store, [repo_id], output_file, change_filter)

    assert output_file.exists()
    content = output_file.read_text()

    # Check that repo info and commits are logged
    assert "Repository: test-repo" in content
    assert "feat: implement first feature" in content
    assert "refactor(git-cv): clean up logic" in content
    assert "docs: update docs" in content

    # Check stats are filtered (additions: 10+5+2+7 = 24; deletions: 2+0+1+7 = 10)
    assert "+24 / -10 lines" in content
    assert "10 files changed" in content
    assert "package-lock.json" not in content
    assert "node_modules" not in content

    # Check truncation works (show 5 files, truncate the rest)
    assert "... (+2 more files)" in content


def test_tech_stack_report(test_env):
    store, repo_id, temp_dir = test_env
    output_file = temp_dir / "tech_stack.md"
    change_filter = ChangeFilter()

    report = TechStackReport()
    report.generate(store, [repo_id], output_file, change_filter)

    assert output_file.exists()
    content = output_file.read_text()

    # Check headers and table values
    assert "Language & Extension Breakdown" in content
    assert "Directory & Module Activity" in content
    assert "`PY`" in content
    assert "`MD`" in content
    assert "`src/reports`" in content


def test_achievements_report(test_env):
    store, repo_id, temp_dir = test_env
    output_file = temp_dir / "achievements.md"
    change_filter = ChangeFilter()

    report = AchievementsReport()
    report.generate(store, [repo_id], output_file, change_filter)

    assert output_file.exists()
    content = output_file.read_text()

    # Check category classifications
    assert "### Feature Delivery" in content
    assert "feat: implement first feature" in content
    assert "feat: commit with many files" in content
    assert "### Refactoring & Architecture" in content
    assert "refactor(git-cv): clean up logic" in content
    assert "### Testing & Documentation" in content
    assert "docs: update docs" in content

    # Check truncation works (+2 more)
    assert "... +2 more" in content


def test_report_manager(test_env):
    store, repo_id, temp_dir = test_env
    output_dir = temp_dir / "reports_out"
    change_filter = ChangeFilter()

    manager = ReportManager()
    paths = manager.generate_reports(
        store, [repo_id], output_dir, ["summary", "tech_stack"], change_filter
    )

    assert len(paths) == 2
    assert "summary" in paths
    assert "tech_stack" in paths
    assert paths["summary"].exists()
    assert paths["tech_stack"].exists()
