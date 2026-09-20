"""Docker Compose service manager and inspector."""

from __future__ import annotations

import subprocess
from pathlib import Path

from models.topology import HomelabTopology
from providers.ssh import run_ssh_command


def validate_compose_files(project_root: Path) -> dict[str, bool]:
    """Validate all service and node compose files using 'docker compose config -q'."""
    results: dict[str, bool] = {}

    compose_files: list[Path] = []
    services_dir = project_root / "services"
    if services_dir.exists():
        compose_files.extend(sorted(services_dir.glob("*/docker-compose.yml")))

    nodes_dir = project_root / "nodes"
    if nodes_dir.exists():
        compose_files.extend(sorted(nodes_dir.glob("*/*/*/docker-compose.yml")))
        compose_files.extend(sorted(nodes_dir.glob("*/*/docker-compose.yml")))

    for compose_path in compose_files:
        rel_name = str(compose_path.relative_to(project_root).parent)
        cmd = ["docker", "compose", "-f", str(compose_path), "config", "-q"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        results[rel_name] = proc.returncode == 0

    return results


def get_remote_container_status(
    node_name: str,
    topology: HomelabTopology,
) -> str:
    """Fetch running docker containers from a remote node via SSH."""
    cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
    proc = run_ssh_command(node_name, topology, cmd, timeout=15.0)
    if proc.returncode == 0:
        return proc.stdout.strip()
    return f"Error querying node '{node_name}': {proc.stderr.strip()}"
