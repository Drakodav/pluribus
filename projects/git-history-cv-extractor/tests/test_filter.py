from src.reports.filter import ChangeFilter


def test_change_filter_includes_source_files():
    change_filter = ChangeFilter()
    assert change_filter.should_include("src/main.py") is True
    assert change_filter.should_include("database.py") is True
    assert change_filter.should_include("README.md") is True
    assert change_filter.should_include("tests/test_sync.py") is True


def test_change_filter_excludes_vendors_and_lockfiles():
    change_filter = ChangeFilter()
    # Vendors
    assert change_filter.should_include("vendors/jquery.min.js") is False
    assert change_filter.should_include("app/vendors/custom/style.css") is False
    assert change_filter.should_include("wp-admin/includes/admin.php") is False

    # Caches and runtime
    assert change_filter.should_include("node_modules/react/index.js") is False
    assert change_filter.should_include(".venv/lib/site-packages/pytest.py") is False
    assert change_filter.should_include("src/__pycache__/main.cpython-310.pyc") is False

    # Lockfiles
    assert change_filter.should_include("uv.lock") is False
    assert change_filter.should_include("package-lock.json") is False
    assert change_filter.should_include("projects/subproject/pnpm-lock.yaml") is False

    # Assets
    assert change_filter.should_include("assets/logo.png") is False
    assert change_filter.should_include("banner.jpeg") is False
    assert change_filter.should_include("icons/favicon.ico") is False


def test_change_filter_custom_excludes():
    # Pass custom glob pattern
    change_filter = ChangeFilter(custom_exclude_patterns=["*.txt", "temp_*"])

    # Excluded by custom rules
    assert change_filter.should_include("notes.txt") is False
    assert change_filter.should_include("temp_run.log") is False

    # Others still included/excluded normally
    assert change_filter.should_include("src/main.py") is True
    assert change_filter.should_include("uv.lock") is False
