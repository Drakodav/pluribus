"""Synchronization workflows for code deployment and Consul service discovery."""

from __future__ import annotations

import subprocess
from pathlib import Path

from models.topology import HomelabTopology
from providers.consul import ConsulClient
from providers.ssh import build_rsync_command, run_ssh_command


def sync_code_to_node(
    node_name: str,
    project_root: Path,
    topology: HomelabTopology,
    target_dest: str = "~/projects/homelab/",
) -> subprocess.CompletedProcess[bytes]:
    """Sync repository code to a node via rsync over ProxyJump SSH."""
    # Ensure remote directory exists before invoking rsync
    run_ssh_command(node_name, topology, f"mkdir -p {target_dest}")
    cmd = build_rsync_command(project_root, node_name, target_dest, topology)
    return subprocess.run(cmd, check=False)


def sync_services_to_consul(
    node_name: str,
    topology: HomelabTopology,
    consul_url: str = "http://10.10.0.1:8500",
) -> dict[str, bool]:
    """Register all declared services for a node into Consul catalog."""
    client = ConsulClient(base_url=consul_url)
    return client.sync_node_services(node_name, topology)
