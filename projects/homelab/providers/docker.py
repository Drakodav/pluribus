"""Docker Compose service manager and inspector."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from models.topology import HomelabTopology
from providers.ssh import run_ssh_command


def needs_sudo_for_docker() -> bool:
    """Check if current user lacks read/write access to docker daemon socket."""
    if os.geteuid() == 0:
        return False
    sock = Path("/var/run/docker.sock")
    if not sock.exists():
        return False
    return not os.access(sock, os.R_OK | os.W_OK)


def build_docker_compose_cmd(
    compose_file: Path | str,
    *subcommand: str,
    env_file: Path | str | None = None,
) -> list[str]:
    """Construct docker compose command with --env-file, compose path, and sudo if required."""
    cmd: list[str] = []
    if needs_sudo_for_docker():
        cmd.append("sudo")
    cmd.extend(["docker", "compose"])
    if env_file and Path(env_file).exists():
        cmd.extend(["--env-file", str(env_file)])
    cmd.extend(["-f", str(compose_file)])
    cmd.extend(subcommand)
    return cmd


def validate_compose_files(project_root: Path) -> dict[str, bool]:
    """Validate all service and node compose files using 'docker compose config -q'."""
    results: dict[str, bool] = {}
    env_file = project_root / ".env"

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
        cmd = ["docker", "compose"]
        if env_file.exists():
            cmd.extend(["--env-file", str(env_file)])
        cmd.extend(["-f", str(compose_path), "config", "-q"])
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
