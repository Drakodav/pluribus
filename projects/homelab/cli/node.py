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


@node_app.command("copy-id")
def node_copy_id(
    target: str = typer.Argument(..., help="Target node or gateway name (required)"),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Authorize local SSH public key on target host for passwordless access."""
    topo = HomelabTopology.load(config)
    from context import AppContext

    ctx = AppContext()
    key_str = ctx.get_required_env("NODE_APERIO_SSH_KEY")
    key_path = Path(key_str).expanduser()
    pub_path = key_path.with_suffix(key_path.suffix + ".pub")
    if not pub_path.exists():
        pub_path = Path(str(key_path) + ".pub")

    if not pub_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Public key not found at '{pub_path}'"
        )
        raise typer.Exit(code=1)

    pub_key_content = pub_path.read_text().strip()
    remote_cmd = (
        f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
        f"grep -qxF '{pub_key_content}' ~/.ssh/authorized_keys 2>/dev/null || "
        f"echo '{pub_key_content}' >> ~/.ssh/authorized_keys && "
        f"chmod 600 ~/.ssh/authorized_keys"
    )

    console.print(
        f"[bold blue]>>> Authorizing public key ({pub_path.name}) on '{target}'...[/bold blue]"
    )
    cmd = build_ssh_command(target, topo, remote_command=remote_cmd)
    proc = subprocess.run(cmd, check=False)
    if proc.returncode == 0:
        console.print(
            f"[bold green]Public key authorized on '{target}'! Passwordless SSH is now active.[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Failed to authorize public key on '{target}' with exit code {proc.returncode}.[/bold red]"
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


@node_app.command(
    "exec",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def node_exec(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="Target node or gateway name (required)"),
    command: str = typer.Argument(..., help="Shell command to execute on remote host"),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Execute an arbitrary shell command on a remote node or gateway over SSH."""
    topo = HomelabTopology.load(config)
    full_cmd = f"{command} {' '.join(ctx.args)}" if ctx.args else command
    try:
        cmd = build_ssh_command(target, topo, remote_command=full_cmd)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[dim]Running on '{target}': {full_cmd}[/dim]")
    proc = subprocess.run(cmd, check=False)
    raise typer.Exit(code=proc.returncode)


def _dispatch_remote_host_cmd(
    target: str,
    action: str,
    topo: HomelabTopology,
    dest: str = "~/projects/homelab/",
    extra_args: list[str] | None = None,
) -> int:
    """Dispatch a 'homelab host <action>' command to a remote node via SSH with PTY."""
    arg_str = f" {' '.join(extra_args)}" if extra_args else ""
    remote_cmd = f"cd {dest} && uv run homelab host {action}{arg_str}"

    try:
        cmd = build_ssh_command(target, topo, remote_command=remote_cmd)
        cmd.insert(1, "-t")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1

    proc = subprocess.run(cmd, check=False)
    return proc.returncode


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
    console.print(
        f"[bold blue]>>> Dispatching host command '{action}' to remote node '{target}'...[/bold blue]"
    )
    code = _dispatch_remote_host_cmd(
        target=target,
        action=action,
        topo=topo,
        dest=dest,
        extra_args=ctx.args,
    )
    raise typer.Exit(code=code)


@node_app.command("deploy")
def node_deploy(
    target: str = typer.Argument(
        ..., help="Target node or gateway name to deploy (e.g. aperio, macerator)"
    ),
    dest: str = typer.Option(
        "~/projects/homelab/", "--dest", "-d", help="Remote homelab project directory"
    ),
    config: Path | None = typer.Option(
        None, "--config", help="Optional path to custom topology file"
    ),
) -> None:
    """Orchestrate end-to-end node deployment (sync -> setup -> up -> status)."""
    topo = HomelabTopology.load(config)
    project_root = Path(__file__).resolve().parent.parent

    console.print(
        "\n[bold cyan]================================================================[/bold cyan]"
    )
    console.print(f"[bold cyan] Deploying to Node: {target}[/bold cyan]")
    console.print(
        "[bold cyan] Sequence: [1] sync ➔ [2] setup ➔ [3] up ➔ [4] status[/bold cyan]"
    )
    console.print(
        "[bold cyan]================================================================[/bold cyan]\n"
    )

    # 1. Sync
    console.print(
        f"[bold blue][1/4] Syncing {project_root} to {target}:{dest}...[/bold blue]"
    )
    sync_proc = sync_code_to_node(target, project_root, topo, target_dest=dest)
    if sync_proc.returncode != 0:
        console.print(
            f"[bold red]Deployment aborted: Sync failed with exit code {sync_proc.returncode}[/bold red]"
        )
        raise typer.Exit(code=sync_proc.returncode)
    console.print("[bold green]  [ok] Sync completed successfully.[/bold green]\n")

    # 2. Setup
    console.print(f"[bold blue][2/4] Running host setup on '{target}'...[/bold blue]")
    setup_code = _dispatch_remote_host_cmd(target, "setup", topo, dest=dest)
    if setup_code != 0:
        console.print(
            f"[bold red]Deployment aborted: Host setup failed with exit code {setup_code}[/bold red]"
        )
        raise typer.Exit(code=setup_code)
    console.print(
        "[bold green]  [ok] Host setup completed successfully.[/bold green]\n"
    )

    # 3. Up
    console.print(f"[bold blue][3/4] Bringing up services on '{target}'...[/bold blue]")
    up_code = _dispatch_remote_host_cmd(target, "up", topo, dest=dest)
    if up_code != 0:
        console.print(
            f"[bold red]Deployment aborted: Service bring-up failed with exit code {up_code}[/bold red]"
        )
        raise typer.Exit(code=up_code)
    console.print("[bold green]  [ok] Services started successfully.[/bold green]\n")

    # 4. Status
    console.print(
        f"[bold blue][4/4] Fetching service status from '{target}'...[/bold blue]"
    )
    status_code = _dispatch_remote_host_cmd(target, "status", topo, dest=dest)
    if status_code != 0:
        console.print(
            f"[bold red]Status check exited with code {status_code}[/bold red]"
        )
        raise typer.Exit(code=status_code)

    console.print(
        f"\n[bold green] Deployment to '{target}' completed successfully![/bold green]\n"
    )
