"""Node lifecycle, onboarding, and access commands."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from models.topology import HomelabTopology
from nodes.registry import get_node_runner
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


@node_app.command("setup")
def node_setup(
    node: str = typer.Argument("macerator", help="Target node name to configure"),
) -> None:
    """Prepare host-level prerequisites, directories, and firewall rules."""
    console.print(
        f"[bold blue]>>> Setting up host environment for node '{node}'...[/bold blue]"
    )
    try:
        runner = get_node_runner(node)
        success = runner.setup_host()
        if success:
            console.print(
                f"[bold green]Host environment for '{node}' prepared successfully.[/bold green]"
            )
        else:
            console.print(
                f"[bold red]Failed to set up host environment for '{node}'.[/bold red]"
            )
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@node_app.command("up")
def node_up(
    node: str = typer.Argument("macerator", help="Target node name"),
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to start"
    ),
) -> None:
    """Prepare host and bring up all (or targeted) assigned services in dependency order."""
    console.print(
        f"[bold blue]>>> Bringing up node '{node}' (service={svc or 'all'})...[/bold blue]"
    )
    try:
        runner = get_node_runner(node)
        results = runner.up(service_name=svc)
        table = Table(title=f"Node '{node}' Services Up Status")
        table.add_column("Service", style="bold cyan")
        table.add_column("Status", justify="center")

        all_ok = True
        for s_name, ok in results.items():
            status_text = (
                "[bold green]Started[/bold green]"
                if ok
                else "[bold red]Failed[/bold red]"
            )
            table.add_row(s_name, status_text)
            if not ok:
                all_ok = False

        console.print(table)
        if not all_ok:
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@node_app.command("down")
def node_down(
    node: str = typer.Argument("macerator", help="Target node name"),
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to stop"
    ),
) -> None:
    """Stop all (or targeted) assigned services on a node."""
    console.print(
        f"[bold blue]>>> Stopping node '{node}' (service={svc or 'all'})...[/bold blue]"
    )
    try:
        runner = get_node_runner(node)
        results = runner.down(service_name=svc)
        for s_name, ok in results.items():
            status_text = (
                "[bold green]Stopped[/bold green]"
                if ok
                else "[bold red]Failed[/bold red]"
            )
            console.print(f"  {s_name}: {status_text}")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@node_app.command("restart")
def node_restart(
    node: str = typer.Argument("macerator", help="Target node name"),
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to restart"
    ),
) -> None:
    """Restart all (or targeted) assigned services on a node."""
    console.print(
        f"[bold blue]>>> Restarting node '{node}' (service={svc or 'all'})...[/bold blue]"
    )
    try:
        runner = get_node_runner(node)
        results = runner.restart(service_name=svc)
        for s_name, ok in results.items():
            status_text = (
                "[bold green]Restarted[/bold green]"
                if ok
                else "[bold red]Failed[/bold red]"
            )
            console.print(f"  {s_name}: {status_text}")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@node_app.command("destroy")
def node_destroy(
    node: str = typer.Argument("macerator", help="Target node name"),
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to destroy"
    ),
) -> None:
    """Tear down and destroy assigned services on a node."""
    console.print(
        f"[bold red]>>> Destroying node '{node}' services (service={svc or 'all'})...[/bold red]"
    )
    try:
        runner = get_node_runner(node)
        results = runner.destroy(service_name=svc)
        for s_name, ok in results.items():
            status_text = (
                "[bold green]Destroyed[/bold green]"
                if ok
                else "[bold red]Failed[/bold red]"
            )
            console.print(f"  {s_name}: {status_text}")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@node_app.command("status")
def node_status(
    node: str = typer.Argument("macerator", help="Target node name"),
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to inspect"
    ),
) -> None:
    """Query runtime status of services on a node."""
    try:
        runner = get_node_runner(node)
        statuses = runner.status(service_name=svc)
        table = Table(title=f"Node '{node}' Services Status")
        table.add_column("Service", style="bold cyan")
        table.add_column("Details", style="green")

        for s_name, details in statuses.items():
            table.add_row(s_name, str(details))

        console.print(table)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
