import fnmatch
from pathlib import Path

DEFAULT_EXCLUDE_PATTERNS = [
    # Vendor & third-party folders
    "*vendors/*",
    "*wp-admin/*",
    "*wp-includes/*",
    # Package manager lockfiles
    "*package-lock.json",
    "*yarn.lock",
    "*pnpm-lock.yaml",
    "*uv.lock",
    "*poetry.lock",
    # Runtime, caches, and dependency folders
    "*node_modules/*",
    "*.venv/*",
    "*__pycache__/*",
    "*.pytest_cache/*",
    "*.ruff_cache/*",
    # Media asset extensions
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.svg",
    "*.gif",
    "*.ico",
    "*.webp",
]


class ChangeFilter:
    def __init__(self, custom_exclude_patterns: list[str] | None = None):
        self.exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)
        if custom_exclude_patterns:
            self.exclude_patterns.extend(custom_exclude_patterns)

    def should_include(self, file_path: str) -> bool:
        """Determines if a file path should be included in contribution reports.

        Matches file_path against the list of glob-like patterns.
        """
        # Convert path to posix format with a leading slash to simplify prefix matching
        posix_path = Path(file_path).as_posix()
        normalized_path = f"/{posix_path}"

        for pattern in self.exclude_patterns:
            # Match patterns against both raw posix path and
            # normalized path with leading slash.
            if fnmatch.fnmatch(posix_path, pattern) or fnmatch.fnmatch(
                normalized_path, pattern
            ):
                return False

        return True
