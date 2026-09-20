"""Validation workflows for topology and Docker Compose stacks."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from models.topology import HomelabTopology
from providers.docker import validate_compose_files


class ValidationReport(NamedTuple):
    """Encapsulates results from a complete homelab validation run."""

    topology: HomelabTopology
    compose_results: dict[str, bool]
    all_compose_valid: bool


def run_full_validation(
    project_root: Path,
    config_path: Path | None = None,
) -> ValidationReport:
    """Execute complete validation across topology schema and Docker Compose files."""
    if config_path is None:
        config_path = project_root / "topology.yaml"

    topo = HomelabTopology.load(config_path)
    compose_results = validate_compose_files(project_root)
    all_compose_valid = all(compose_results.values()) if compose_results else True

    return ValidationReport(
        topology=topo,
        compose_results=compose_results,
        all_compose_valid=all_compose_valid,
    )
