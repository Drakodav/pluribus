"""WireGuard overlay mesh commands."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from models.topology import HomelabTopology
from providers.wireguard import generate_gateway_wg_conf, generate_node_wg_conf

mesh_app = typer.Typer(help="WireGuard overlay mesh commands.")
console = Console()


@mesh_app.callback(invoke_without_command=True)
def mesh_callback(ctx: typer.Context) -> None:
    """WireGuard overlay mesh commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@mesh_app.command("config")
def mesh_config(
    target: str = typer.Argument("aperio", help="Target node or gateway name"),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to topology.yaml"
    ),
) -> None:
    """Print the generated /etc/wireguard/wg0.conf for any node or gateway."""
    topo = HomelabTopology.load(config)
    if target in topo.gateways:
        conf = generate_gateway_wg_conf(target, topo.gateways[target], topo)
    elif target in topo.nodes:
        node = topo.nodes[target]
        gw_name = node.ssh.bastion or next(iter(topo.gateways.keys()))
        conf = generate_node_wg_conf(target, node, topo.gateways[gw_name], topo)
    else:
        console.print(f"[bold red]Unknown target '{target}'[/bold red]")
        raise typer.Exit(code=1)

    sys.stdout.write(conf)
    if not conf.endswith("\n"):
        sys.stdout.write("\n")
