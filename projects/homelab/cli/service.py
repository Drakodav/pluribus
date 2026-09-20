"""Service lifecycle management commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from services.registry import get_all_services, get_service

service_app = typer.Typer(help="Service lifecycle management commands.")
console = Console()


@service_app.callback(invoke_without_command=True)
def service_callback(ctx: typer.Context) -> None:
    """Service lifecycle management commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@service_app.command("list")
def service_list() -> None:
    """List all available service instances registered in the engine."""
    services = get_all_services()
    table = Table(title="Registered Service Implementations")
    table.add_column("Service Name", style="bold cyan")
    table.add_column("Role", style="magenta")
    table.add_column("Port", justify="right")
    table.add_column("Exposure", justify="center")
    table.add_column("Class", style="green")

    for name, svc in sorted(services.items()):
        table.add_row(
            name,
            svc.role,
            str(svc.upstream_port),
            svc.exposure,
            svc.__class__.__name__,
        )
    console.print(table)


@service_app.command("up")
def service_up(
    name: str = typer.Argument(..., help="Service name to start"),
) -> None:
    """Idempotently bring up a service stack."""
    console.print(f"[bold blue]>>> Bringing up service '{name}'...[/bold blue]")
    try:
        svc = get_service(name)
        success = svc.up()
        if success:
            console.print(
                f"[bold green]Service '{name}' is up and running![/bold green]"
            )
        else:
            console.print(f"[bold red]Failed to bring up service '{name}'[/bold red]")
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@service_app.command("down")
def service_down(
    name: str = typer.Argument(..., help="Service name to stop"),
) -> None:
    """Stop a running service stack."""
    console.print(f"[bold blue]>>> Stopping service '{name}'...[/bold blue]")
    try:
        svc = get_service(name)
        success = svc.down()
        if success:
            console.print(f"[bold green]Service '{name}' stopped.[/bold green]")
        else:
            console.print(f"[bold red]Failed to stop service '{name}'[/bold red]")
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@service_app.command("restart")
def service_restart(
    name: str = typer.Argument(..., help="Service name to restart"),
) -> None:
    """Restart a service stack."""
    console.print(f"[bold blue]>>> Restarting service '{name}'...[/bold blue]")
    try:
        svc = get_service(name)
        success = svc.restart()
        if success:
            console.print(f"[bold green]Service '{name}' restarted.[/bold green]")
        else:
            console.print(f"[bold red]Failed to restart service '{name}'[/bold red]")
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@service_app.command("destroy")
def service_destroy(
    name: str = typer.Argument(..., help="Service name to destroy"),
) -> None:
    """Tear down a service stack and purge ephemeral resources."""
    console.print(f"[bold red]>>> Destroying service '{name}'...[/bold red]")
    try:
        svc = get_service(name)
        success = svc.destroy()
        if success:
            console.print(f"[bold green]Service '{name}' destroyed.[/bold green]")
        else:
            console.print(f"[bold red]Failed to destroy service '{name}'[/bold red]")
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@service_app.command("status")
def service_status(
    name: str = typer.Argument(..., help="Service name to inspect"),
) -> None:
    """Query runtime status and health of a service."""
    try:
        svc = get_service(name)
        stat = svc.status()
        console.print(f"[bold cyan]Status for service '{name}':[/bold cyan]")
        for item, st in stat.items():
            console.print(f"  {item}: [bold]{st}[/bold]")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
