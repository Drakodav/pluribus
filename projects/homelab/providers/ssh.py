"""SSH ProxyJump and file synchronization transport module."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from models.topology import HomelabTopology


def build_ssh_command(
    target_name: str,
    topology: HomelabTopology,
    remote_command: str | None = None,
    identity_file: str | None = None,
) -> list[str]:
    """Build the argument list for an SSH connection with automatic ProxyJump."""
    cmd = ["ssh", "-o", "StrictHostKeyChecking=no"]

    key = (
        identity_file
        or os.environ.get("GATEWAY_SSH_KEY")
        or str(Path.home() / ".ssh" / "id_rsa")
    )
    if Path(key).exists():
        cmd.extend(["-i", key])

    if target_name in topology.gateways:
        gw = topology.gateways[target_name]
        target_host = f"{gw.ssh.user}@{gw.public_ip}"
        if gw.ssh.port != 22:
            cmd.extend(["-p", str(gw.ssh.port)])
        cmd.append(target_host)

    elif target_name in topology.nodes:
        node = topology.nodes[target_name]
        if node.ssh.bastion:
            bastion_gw = topology.gateways[node.ssh.bastion]
            bastion_spec = f"{bastion_gw.ssh.user}@{bastion_gw.public_ip}"
            if bastion_gw.ssh.port != 22:
                bastion_spec += f":{bastion_gw.ssh.port}"
            cmd.extend(["-J", bastion_spec])

        target_host = f"{node.ssh.user}@{node.backbone_ip}"
        if node.ssh.port != 22:
            cmd.extend(["-p", str(node.ssh.port)])
        cmd.append(target_host)
    else:
        raise ValueError(f"Unknown target host '{target_name}'.")

    if remote_command:
        cmd.append(remote_command)

    return cmd


def build_rsync_command(
    source_dir: Path | str,
    target_name: str,
    target_dest: str,
    topology: HomelabTopology,
    identity_file: str | None = None,
) -> list[str]:
    """Build rsync command line for syncing files through the bastion to target host."""
    source_dir = str(source_dir)
    if not source_dir.endswith("/"):
        source_dir += "/"

    key = (
        identity_file
        or os.environ.get("GATEWAY_SSH_KEY")
        or str(Path.home() / ".ssh" / "id_rsa")
    )
    ssh_opts = ["ssh", "-o", "StrictHostKeyChecking=no"]
    if Path(key).exists():
        ssh_opts.extend(["-i", key])

    if target_name in topology.nodes:
        node = topology.nodes[target_name]
        if node.ssh.bastion:
            bastion_gw = topology.gateways[node.ssh.bastion]
            ssh_opts.extend(["-J", f"{bastion_gw.ssh.user}@{bastion_gw.public_ip}"])
        dest_spec = f"{node.ssh.user}@{node.backbone_ip}:{target_dest}"
    elif target_name in topology.gateways:
        gw = topology.gateways[target_name]
        dest_spec = f"{gw.ssh.user}@{gw.public_ip}:{target_dest}"
    else:
        raise ValueError(f"Unknown target host '{target_name}'.")

    rsync_cmd = [
        "rsync",
        "-avz",
        "--delete",
        "--exclude=.git",
        "--exclude=.agents/temp",
        "--exclude=.venv",
        "--exclude=__pycache__",
        "--exclude=nodes/*/connect.sh",
        "-e",
        " ".join(ssh_opts),
        source_dir,
        dest_spec,
    ]
    return rsync_cmd


def run_ssh_command(
    target_name: str,
    topology: HomelabTopology,
    remote_command: str,
    timeout: float = 30.0,
) -> subprocess.CompletedProcess[str]:
    """Execute a command on the remote host via SSH and return output."""
    cmd = build_ssh_command(target_name, topology, remote_command)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
