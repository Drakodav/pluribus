import argparse
import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.reports.ai_agent import main


def test_ai_agent_runner_success() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        reports_dir = Path(temp_dir) / "reports"
        reports_dir.mkdir()
        # Create a mock report file
        report_file = reports_dir / "contributions_summary.md"
        report_file.write_text("Test contributions report", encoding="utf-8")

        output_file = reports_dir / "ai" / "star_accomplishments.md"

        # Mock turning response
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value="Mocked AI STAR analysis")

        mock_agent = MagicMock()
        mock_agent.chat = AsyncMock(return_value=mock_response)

        # Context manager __aenter__ and __aexit__
        mock_agent.__aenter__ = AsyncMock(return_value=mock_agent)
        mock_agent.__aexit__ = AsyncMock(return_value=None)

        # Mock the Agent import inside ai_agent
        with patch("src.reports.ai_agent.Agent", return_value=mock_agent):
            with patch("argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value = argparse.Namespace(
                    prompt="Generate STAR bullets",
                    reports_dir=str(reports_dir),
                    output=str(output_file),
                )
                # Run the async main in a synchronous loop wrapper
                asyncio.run(main())

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == "Mocked AI STAR analysis"
    finally:
        shutil.rmtree(temp_dir)


def test_ai_agent_runner_no_reports() -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        reports_dir = Path(temp_dir) / "reports"
        reports_dir.mkdir()

        output_file = reports_dir / "ai" / "star_accomplishments.md"

        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = argparse.Namespace(
                prompt="Generate STAR bullets",
                reports_dir=str(reports_dir),
                output=str(output_file),
            )
            with pytest.raises(ValueError, match="No report markdown files found"):
                asyncio.run(main())
    finally:
        shutil.rmtree(temp_dir)
