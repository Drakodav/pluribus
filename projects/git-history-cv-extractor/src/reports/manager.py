from pathlib import Path

from src.database import RepositoryStore
from src.reports.achievements_generator import AchievementsReport
from src.reports.filter import ChangeFilter
from src.reports.summary_generator import SummaryReport
from src.reports.tech_stack_generator import TechStackReport

REPORT_MAPPING = {
    "summary": (SummaryReport, "contributions_summary.md"),
    "tech_stack": (TechStackReport, "technology_profile.md"),
    "achievements": (AchievementsReport, "achievements_highlights.md"),
}


class ReportManager:
    def __init__(self):
        pass

    def generate_reports(
        self,
        store: RepositoryStore,
        repo_ids: list[int],
        output_dir: Path,
        report_types: list[str],
        change_filter: ChangeFilter,
    ) -> dict[str, Path]:
        """Coordinates and triggers the generation of selected report types.

        Returns:
            dict[str, Path]: A dictionary mapping report type names to their
            generated file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}

        for r_type in report_types:
            if r_type not in REPORT_MAPPING:
                raise ValueError(f"Unknown report type: {r_type}")

            generator_cls, filename = REPORT_MAPPING[r_type]
            output_file = output_dir / filename

            # Instantiate and run the generator
            generator = generator_cls()
            generator.generate(store, repo_ids, output_file, change_filter)
            results[r_type] = output_file

        return results
