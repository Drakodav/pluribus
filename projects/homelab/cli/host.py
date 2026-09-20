"""Host lifecycle management commands (executed directly on a node)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from context import AppContext
from nodes.base import BaseNodeRunner
from nodes.registry import get_node_runner

host_app = typer.Typer(
    help="Host lifecycle management commands (executed directly on a node)."
)
console = Console()


def get_current_host_runner(node_override: str | None = None) -> BaseNodeRunner:
    """Resolve the appropriate node runner for the current host or override."""
    ctx = AppContext()

    if node_override:
        return get_node_runner(node_override)

    if ctx.runtime.is_macerator:
        return get_node_runner("macerator")
    if ctx.runtime.is_aperio:
        return get_node_runner("aperio")

    if ctx.runtime.is_local_workstation:
        console.print(
            f"[bold red]Host Execution Error:[/bold red] Running on local workstation '{ctx.runtime.hostname}'. "
            "'homelab host' commands are intended to run directly on a homelab node.\n"
            "[yellow]Hint: To execute host commands remotely from your workstation, use:[/yellow]\n"
            "  uv run homelab node run <node-name> <command>\n"
            "  uv run homelab node ssh <node-name>"
        )
        raise typer.Exit(code=1)

    try:
        return get_node_runner(ctx.runtime.hostname)
    except Exception as exc:
        console.print(
            f"[bold red]Error:[/bold red] Host '{ctx.runtime.hostname}' is not a registered homelab node: {exc}"
        )
        raise typer.Exit(code=1) from exc


@host_app.callback(invoke_without_command=True)
def host_callback(ctx: typer.Context) -> None:
    """Host lifecycle management commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@host_app.command("setup")
def host_setup(
    node: str | None = typer.Option(
        None, "--node", "-n", help="Optional node name override"
    ),
) -> None:
    """Prepare host-level prerequisites, directories, and firewall rules."""
    ctx = AppContext()
    if not ctx.runtime.is_root and not ctx.runtime.is_local_workstation:
        import os
        import sys

        console.print("[yellow]>>> Elevating 'host setup' with sudo...[/yellow]")
        os.execvp("sudo", ["sudo", *sys.argv])

    runner = get_current_host_runner(node)
    console.print(
        f"[bold blue]>>> Setting up host environment for '{runner.name}'...[/bold blue]"
    )
    success = runner.setup_host()
    if success:
        console.print(
            f"[bold green]Host environment for '{runner.name}' prepared successfully.[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Failed to set up host environment for '{runner.name}'.[/bold red]"
        )
        raise typer.Exit(code=1)


@host_app.command("up")
def host_up(
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to start"
    ),
    node: str | None = typer.Option(
        None, "--node", "-n", help="Optional node name override"
    ),
) -> None:
    """Prepare host and bring up all (or targeted) assigned services in dependency order."""
    runner = get_current_host_runner(node)
    console.print(
        f"[bold blue]>>> Bringing up host '{runner.name}' (service={svc or 'all'})...[/bold blue]"
    )
    results = runner.up(service_name=svc)

    table = Table(title=f"Host '{runner.name}' Services Up Status")
    table.add_column("Service", style="bold cyan")
    table.add_column("Status", justify="center")

    all_ok = True
    for s_name, ok in results.items():
        status_text = (
            "[bold green]Started[/bold green]" if ok else "[bold red]Failed[/bold red]"
        )
        table.add_row(s_name, status_text)
        if not ok:
            all_ok = False

    console.print(table)
    if not all_ok:
        raise typer.Exit(code=1)


@host_app.command("down")
def host_down(
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to stop"
    ),
    node: str | None = typer.Option(
        None, "--node", "-n", help="Optional node name override"
    ),
) -> None:
    """Stop all (or targeted) assigned services on this host."""
    runner = get_current_host_runner(node)
    console.print(
        f"[bold blue]>>> Stopping host '{runner.name}' (service={svc or 'all'})...[/bold blue]"
    )
    results = runner.down(service_name=svc)
    for s_name, ok in results.items():
        status_text = (
            "[bold green]Stopped[/bold green]" if ok else "[bold red]Failed[/bold red]"
        )
        console.print(f"  {s_name}: {status_text}")


@host_app.command("restart")
def host_restart(
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to restart"
    ),
    node: str | None = typer.Option(
        None, "--node", "-n", help="Optional node name override"
    ),
) -> None:
    """Restart all (or targeted) assigned services on this host."""
    runner = get_current_host_runner(node)
    console.print(
        f"[bold blue]>>> Restarting host '{runner.name}' (service={svc or 'all'})...[/bold blue]"
    )
    results = runner.restart(service_name=svc)
    for s_name, ok in results.items():
        status_text = (
            "[bold green]Restarted[/bold green]"
            if ok
            else "[bold red]Failed[/bold red]"
        )
        console.print(f"  {s_name}: {status_text}")


@host_app.command("destroy")
def host_destroy(
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to destroy"
    ),
    node: str | None = typer.Option(
        None, "--node", "-n", help="Optional node name override"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Confirm destruction without prompt"
    ),
) -> None:
    """Tear down and destroy assigned services on this host (requires confirmation)."""
    runner = get_current_host_runner(node)

    if not yes:
        target_desc = (
            f"service '{svc}'" if svc else f"all services on host '{runner.name}'"
        )
        typer.confirm(
            f"⚠️  Are you sure you want to destroy {target_desc}? This will stop containers and delete ephemeral volumes!",
            abort=True,
        )

    console.print(
        f"[bold red]>>> Destroying host '{runner.name}' services (service={svc or 'all'})...[/bold red]"
    )
    results = runner.destroy(service_name=svc)
    for s_name, ok in results.items():
        status_text = (
            "[bold green]Destroyed[/bold green]"
            if ok
            else "[bold red]Failed[/bold red]"
        )
        console.print(f"  {s_name}: {status_text}")


@host_app.command("status")
def host_status(
    svc: str | None = typer.Option(
        None, "--svc", "-s", help="Optional specific service to inspect"
    ),
    node: str | None = typer.Option(
        None, "--node", "-n", help="Optional node name override"
    ),
) -> None:
    """Query runtime status of services on this host."""
    runner = get_current_host_runner(node)
    statuses = runner.status(service_name=svc)
    table = Table(title=f"Host '{runner.name}' Services Status")
    table.add_column("Service", style="bold cyan")
    table.add_column("Details", style="green")

    for s_name, details in statuses.items():
        table.add_row(s_name, str(details))

    console.print(table)
