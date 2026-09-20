"""Node lifecycle, onboarding, and access commands."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import typer
from rich.console import Console

from models.topology import HomelabTopology
from providers.ssh import build_ssh_command
from providers.wireguard import generate_node_connect_script
from workflows.sync import sync_code_to_node

node_app = typer.Typer(help="Node lifecycle and access commands.")
console = Console()


@node_app.callback(invoke_without_command=True)
def node_callback(ctx: typer.Context) -> None:
    """Node lifecycle and access commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@node_app.command("generate-wireguard-bootstrap")
def generate_wireguard_bootstrap(
    node: str = typer.Argument("macerator", help="Target node name"),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """Generate self-contained WireGuard onboarding bootstrap script for a node."""
    topo = HomelabTopology.load(config)
    try:
        script = generate_node_connect_script(node, topo)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold green]=== WireGuard Bootstrap Script for Node: {node} ===[/bold green]"
    )
    console.print("Run the following snippet on the target node directly:\n")
    console.print("cat << 'EOF' | sudo bash")
    sys.stdout.write(script)
    if not script.endswith("\n"):
        sys.stdout.write("\n")
    console.print("EOF")


@node_app.command("ssh")
def node_ssh(
    target: str = typer.Argument("macerator", help="Target node or gateway name"),
    command: str | None = typer.Option(
        None, "--cmd", "-c", help="Remote command to execute"
    ),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """Connect to a node or gateway via SSH (with automatic bastion ProxyJump)."""
    topo = HomelabTopology.load(config)
    try:
        cmd = build_ssh_command(target, topo, remote_command=command)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[dim]Executing: {' '.join(cmd)}[/dim]")
    os.execvp(cmd[0], cmd)


@node_app.command("sync")
def node_sync(
    target: str = typer.Argument("macerator", help="Target node name to sync to"),
    dest: str = typer.Option(
        "~/projects/homelab/", "--dest", "-d", help="Remote destination directory"
    ),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """Sync repository code to a node via rsync over ProxyJump SSH."""
    topo = HomelabTopology.load(config)
    project_root = Path(__file__).resolve().parent.parent

    console.print(
        f"[bold blue]>>> Syncing {project_root} to {target}:{dest}...[/bold blue]"
    )
    proc = sync_code_to_node(target, project_root, topo, target_dest=dest)
    if proc.returncode == 0:
        console.print("[bold green]Sync completed successfully![/bold green]")
    else:
        console.print(
            f"[bold red]Sync failed with exit code {proc.returncode}[/bold red]"
        )
        raise typer.Exit(code=proc.returncode)
