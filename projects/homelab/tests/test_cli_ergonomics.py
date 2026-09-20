"""Unit tests for CLI ergonomics, argument enforcement, and host safety guards."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from cli.host import host_app
from cli.main import app

runner = CliRunner()


def test_node_commands_require_explicit_target_no_defaults():
    """Verify that node access commands fail with code 2 when target is omitted."""
    # node ssh
    res_ssh = runner.invoke(app, ["node", "ssh"])
    assert res_ssh.exit_code == 2
    assert "Missing argument 'target'" in res_ssh.output

    # node sync
    res_sync = runner.invoke(app, ["node", "sync"])
    assert res_sync.exit_code == 2
    assert "Missing argument 'target'" in res_sync.output

    # node bootstrap
    res_boot = runner.invoke(app, ["node", "bootstrap"])
    assert res_boot.exit_code == 2
    assert "Missing argument 'target'" in res_boot.output

    # node run
    res_run = runner.invoke(app, ["node", "run"])
    assert res_run.exit_code == 2
    assert "Missing argument 'target'" in res_run.output

    # node deploy
    res_deploy = runner.invoke(app, ["node", "deploy"])
    assert res_deploy.exit_code == 2
    assert "Missing argument 'target'" in res_deploy.output


def test_node_run_portal_dispatches_ssh_with_pty():
    """Verify homelab node run constructs the remote host command and passes -t."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        res = runner.invoke(app, ["node", "run", "macerator", "status"])
        assert res.exit_code == 0
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]

        # Verify SSH flags and remote command
        assert "ssh" in cmd
        assert "-t" in cmd
        assert any(
            "cd ~/projects/homelab/ && uv run homelab host status" in arg for arg in cmd
        )


def test_node_run_portal_with_extra_args():
    """Verify homelab node run forwards arguments like --svc and --yes to host."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        res = runner.invoke(
            app,
            [
                "node",
                "run",
                "macerator",
                "restart",
                "--svc",
                "authentik",
            ],
        )
        assert res.exit_code == 0
        cmd = mock_run.call_args[0][0]
        assert any(
            "cd ~/projects/homelab/ && uv run homelab host restart --svc authentik"
            in arg
            for arg in cmd
        )


def test_host_commands_reject_workstation_execution():
    """Verify that running homelab host on a local workstation aborts with helpful guidance."""
    mock_ctx = MagicMock()
    mock_ctx.runtime.is_macerator = False
    mock_ctx.runtime.is_aperio = False
    mock_ctx.runtime.is_local_workstation = True
    mock_ctx.runtime.hostname = "MacBook-Pro.local"

    with patch("cli.host.AppContext", return_value=mock_ctx):
        res = runner.invoke(host_app, ["up"])
        assert res.exit_code == 1
        assert "Host Execution Error" in res.output
        assert "uv run homelab node run" in res.output


def test_host_destroy_requires_confirmation_when_not_yes():
    """Verify homelab host destroy prompts for confirmation and aborts if denied."""
    mock_runner = MagicMock()
    mock_runner.name = "macerator"

    with patch("cli.host.get_current_host_runner", return_value=mock_runner):
        # Simulate user answering 'n' to confirmation prompt
        res = runner.invoke(host_app, ["destroy"], input="n\n")
        assert res.exit_code != 0
        mock_runner.destroy.assert_not_called()


def test_host_destroy_proceeds_with_yes_flag():
    """Verify homelab host destroy skips confirmation prompt when --yes is passed."""
    mock_runner = MagicMock()
    mock_runner.name = "macerator"
    mock_runner.destroy.return_value = {"consul": True}

    with patch("cli.host.get_current_host_runner", return_value=mock_runner):
        res = runner.invoke(host_app, ["destroy", "--yes"])
        assert res.exit_code == 0
        mock_runner.destroy.assert_called_once()


def test_host_up_success_table():
    """Verify homelab host up executes successfully when mocked."""
    mock_runner = MagicMock()
    mock_runner.name = "macerator"
    mock_runner.up.return_value = {"consul": True, "redis": True}

    with patch("cli.host.get_current_host_runner", return_value=mock_runner):
        res = runner.invoke(host_app, ["up", "--svc", "consul"])
        assert res.exit_code == 0
        mock_runner.up.assert_called_once_with(service_name="consul")
        assert "consul" in res.output


def test_node_deploy_orchestrates_pipeline_in_order():
    """Verify homelab node deploy executes sync, setup, up, and status in order."""
    with (
        patch("cli.node.sync_code_to_node") as mock_sync,
        patch("subprocess.run") as mock_run,
    ):
        mock_sync.return_value = MagicMock(returncode=0)
        mock_run.return_value = MagicMock(returncode=0)

        res = runner.invoke(app, ["node", "deploy", "aperio"])
        assert res.exit_code == 0
        mock_sync.assert_called_once()
        assert mock_run.call_count == 3

        # Verify dispatched commands in order: setup, up, status
        calls = mock_run.call_args_list
        setup_cmd = " ".join(calls[0][0][0])
        up_cmd = " ".join(calls[1][0][0])
        status_cmd = " ".join(calls[2][0][0])

        assert "uv run homelab host setup" in setup_cmd
        assert "uv run homelab host up" in up_cmd
        assert "uv run homelab host status" in status_cmd


def test_node_deploy_aborts_on_sync_failure():
    """Verify homelab node deploy halts immediately if rsync sync fails."""
    with (
        patch("cli.node.sync_code_to_node") as mock_sync,
        patch("subprocess.run") as mock_run,
    ):
        mock_sync.return_value = MagicMock(returncode=11)

        res = runner.invoke(app, ["node", "deploy", "aperio"])
        assert res.exit_code == 11
        mock_sync.assert_called_once()
        mock_run.assert_not_called()
        assert "Deployment aborted: Sync failed" in res.output
