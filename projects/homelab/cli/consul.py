"""Consul service discovery CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from models.topology import HomelabTopology
from workflows.sync import sync_services_to_consul

consul_app = typer.Typer(help="Consul service discovery commands.")
console = Console()


@consul_app.callback(invoke_without_command=True)
def consul_callback(ctx: typer.Context) -> None:
    """Consul service discovery commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@consul_app.command("sync")
def consul_sync(
    node: str = typer.Argument("macerator", help="Node whose services to register"),
    consul_url: str = typer.Option(
        "http://10.10.0.1:8500", "--consul", help="Consul HTTP API endpoint"
    ),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """Synchronize all services assigned to a node with the Consul Catalog."""
    topo = HomelabTopology.load(config)

    console.print(
        f"[bold blue]>>> Syncing services for node '{node}' to Consul at {consul_url}...[/bold blue]"
    )
    try:
        results = sync_services_to_consul(node, topo, consul_url=consul_url)
    except Exception as exc:
        console.print(f"[bold red]Consul Sync Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Consul Service Registration: {node}")
    table.add_column("Service", style="cyan")
    table.add_column("Status", justify="center")

    for svc, success in results.items():
        status = (
            "[bold green]Registered[/bold green]"
            if success
            else "[bold red]Failed[/bold red]"
        )
        table.add_row(svc, status)

    console.print(table)
