from abc import ABC, abstractmethod
from pathlib import Path

from src.database import RepositoryStore
from src.reports.filter import ChangeFilter


class BaseReport(ABC):
    @abstractmethod
    def generate(
        self,
        store: RepositoryStore,
        repo_ids: list[int],
        output_file: Path,
        change_filter: ChangeFilter,
    ) -> None:
        """Generates the specific report format and writes it to output_file."""
        pass
