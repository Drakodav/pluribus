"""Remote node access, synchronization, and control-plane commands."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from models.topology import HomelabTopology
from providers.ssh import build_ssh_command
from providers.wireguard import generate_node_connect_script
from workflows.sync import sync_code_to_node

node_app = typer.Typer(
    help="Remote node access, synchronization, and control-plane commands."
)
console = Console()


@node_app.callback(invoke_without_command=True)
def node_callback(ctx: typer.Context) -> None:
    """Remote node access, synchronization, and control-plane commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@node_app.command("ssh")
def node_ssh(
    target: str = typer.Argument(..., help="Target node or gateway name (required)"),
    command: str | None = typer.Option(
        None, "--cmd", "-c", help="Remote command to execute"
    ),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Connect to a node or gateway via SSH (with automatic bastion ProxyJump)."""
    topo = HomelabTopology.load(config)
    try:
        cmd = build_ssh_command(target, topo, remote_command=command)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[dim]Connecting to '{target}': {' '.join(cmd)}[/dim]")
    os.execvp(cmd[0], cmd)


@node_app.command("sync")
def node_sync(
    target: str = typer.Argument(..., help="Target node name to sync to (required)"),
    dest: str = typer.Option(
        "~/projects/homelab/", "--dest", "-d", help="Remote destination directory"
    ),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
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


@node_app.command("bootstrap")
def node_bootstrap(
    target: str = typer.Argument(..., help="Target node name (required)"),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Generate self-contained WireGuard onboarding bootstrap script for a node."""
    topo = HomelabTopology.load(config)
    try:
        script = generate_node_connect_script(target, topo)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold green]=== WireGuard Bootstrap Script for Node: {target} ===[/bold green]"
    )
    console.print("Run the following snippet on the target node directly:\n")
    console.print("cat << 'EOF' | sudo bash")
    sys.stdout.write(script)
    if not script.endswith("\n"):
        sys.stdout.write("\n")
    console.print("EOF")


@node_app.command("generate-wireguard-bootstrap", hidden=True)
def node_generate_wireguard_bootstrap(
    target: str = typer.Argument(..., help="Target node name (required)"),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Alias for 'bootstrap' command."""
    node_bootstrap(target=target, config=config)


@node_app.command("exec")
def node_exec(
    target: str = typer.Argument(..., help="Target node or gateway name (required)"),
    command: str = typer.Argument(..., help="Shell command to execute on remote host"),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Execute an arbitrary shell command on a remote node or gateway over SSH."""
    topo = HomelabTopology.load(config)
    try:
        cmd = build_ssh_command(target, topo, remote_command=command)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[dim]Running on '{target}': {command}[/dim]")
    proc = subprocess.run(cmd, check=False)
    raise typer.Exit(code=proc.returncode)


@node_app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def node_run(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="Target node name (required)"),
    action: str = typer.Argument(
        ...,
        help="Host action to execute (e.g. up, down, restart, status, setup, destroy)",
    ),
    dest: str = typer.Option(
        "~/projects/homelab/", "--dest", "-d", help="Remote homelab project directory"
    ),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Portal to execute 'homelab host' lifecycle commands directly on a remote node via SSH."""
    topo = HomelabTopology.load(config)
    extra_args = ctx.args
    arg_str = f" {' '.join(extra_args)}" if extra_args else ""
    remote_cmd = f"cd {dest} && uv run homelab host {action}{arg_str}"

    try:
        cmd = build_ssh_command(target, topo, remote_command=remote_cmd)
        # Allocate pseudo-terminal (-t) so interactive prompts (like destroy confirmation) stream cleanly
        cmd.insert(1, "-t")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold blue]>>> Dispatching host command '{action}' to remote node '{target}'...[/bold blue]"
    )
    proc = subprocess.run(cmd, check=False)
    raise typer.Exit(code=proc.returncode)
