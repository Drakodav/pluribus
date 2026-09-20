"""Main Typer CLI application for the Homelab mesh engine."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from cli.consul import consul_app
from cli.mesh import mesh_app
from cli.node import node_app
from models.topology import HomelabTopology
from workflows.validate import run_full_validation

app = typer.Typer(
    name="homelab",
    help="Type-safe declarative configuration engine for hybrid homelab.",
    no_args_is_help=True,
)

app.add_typer(mesh_app, name="mesh")
app.add_typer(node_app, name="node")
app.add_typer(consul_app, name="consul")

console = Console()


@app.command("validate")
def validate(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """Validate topology.yaml integrity and all Docker Compose service stacks."""
    console.print(
        "[bold blue]>>> Validating Declarative Homelab Configuration...[/bold blue]"
    )
    project_root = Path(__file__).resolve().parent.parent

    try:
        report = run_full_validation(project_root, config_path=config)
    except Exception as exc:
        console.print(f"[bold red]Configuration Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Topology Schema Validation")
    table.add_column("Resource", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Status", style="green")

    table.add_row("Gateways", str(len(report.topology.gateways)), "Valid")
    table.add_row("Nodes", str(len(report.topology.nodes)), "Valid")
    table.add_row("Services", str(len(report.topology.services)), "Valid")
    console.print(table)

    console.print("\n[bold blue]>>> Validating Docker Compose Stacks...[/bold blue]")
    compose_table = Table(title="Docker Compose Service Validation")
    compose_table.add_column("Service Stack", style="cyan")
    compose_table.add_column("File Status", justify="center")

    for svc, valid in report.compose_results.items():
        status_text = (
            "[bold green]Valid[/bold green]"
            if valid
            else "[bold red]Invalid[/bold red]"
        )
        compose_table.add_row(svc, status_text)

    console.print(compose_table)

    if not report.all_compose_valid:
        console.print(
            "[bold red]Error: One or more compose files failed validation![/bold red]"
        )
        raise typer.Exit(code=1)

    console.print(
        "\n[bold green]All configuration and service definitions are valid![/bold green]"
    )


@app.command("services")
def list_services(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """List all registered services and their routing / exposure policies."""
    try:
        topo = HomelabTopology.load(config)
    except Exception as exc:
        console.print(f"[bold red]Configuration Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Declared Services ({topo.domain})")
    table.add_column("Service Name", style="bold cyan")
    table.add_column("Role", style="magenta")
    table.add_column("Port", justify="right")
    table.add_column("Exposure", justify="center")
    table.add_column("Subdomain / URL", style="blue")
    table.add_column("Assigned Nodes", style="yellow")

    for svc_name, svc in topo.services.items():
        assigned = [
            n_name for n_name, n in topo.nodes.items() if svc_name in n.services
        ]
        assigned_str = ", ".join(assigned) if assigned else "[dim]None[/dim]"
        url = f"{svc.subdomain}.{topo.domain}" if svc.subdomain else "-"
        exposure_color = (
            "green"
            if svc.exposure == "public"
            else ("yellow" if svc.exposure == "sso" else "dim")
        )
        exp_formatted = f"[{exposure_color}]{svc.exposure}[/{exposure_color}]"

        table.add_row(
            svc_name,
            svc.role,
            str(svc.upstream_port),
            exp_formatted,
            url,
            assigned_str,
        )

    console.print(table)


if __name__ == "__main__":
    app()
