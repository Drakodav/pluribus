"""Unit tests for Service and Node Runner lifecycle abstractions."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nodes.macerator.runner import MaceratorRunner
from nodes.registry import get_node_runner
from services.base import BaseService
from services.compose_base import ComposeService
from services.registry import get_all_services, get_service


def test_service_registry_resolution():
    """Verify service registry discovers all services and handles aliases."""
    services = get_all_services()
    expected_services = {
        "authentik",
        "cockpit",
        "code",
        "consul",
        "home-assistant",
        "netdata",
        "photos",
        "postgres",
        "redis",
    }
    assert set(services.keys()) == expected_services

    # Verify alias resolution
    ha = get_service("ha")
    assert ha.name == "home-assistant"

    # Verify invalid service raises ValueError
    with pytest.raises(ValueError) as exc:
        get_service("nonexistent-service")
    assert "Unknown service" in str(exc.value)


def test_compose_service_lifecycle():
    """Verify ComposeService lifecycle commands invoke docker compose correctly."""
    service_dir = Path("/mock/service")
    service = ComposeService(service_dir)
    service.name = "mock-service"

    with patch.object(Path, "exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            # Test up()
            assert service.up() is True
            assert mock_run.call_count >= 1

            # Test down()
            mock_run.reset_mock()
            assert service.down() is True
            assert mock_run.call_args[0][0][:4] == [
                "docker",
                "compose",
                "-f",
                str(service.compose_file),
            ]

            # Test restart()
            mock_run.reset_mock()
            assert service.restart() is True

            # Test destroy()
            mock_run.reset_mock()
            assert service.destroy() is True

            # Test status()
            mock_run.reset_mock()
            mock_run.return_value = MagicMock(
                returncode=0, stdout="mock_container: Up 2 hours\n"
            )
            stat = service.status()
            assert stat == {"mock_container": "Up 2 hours"}


def test_macerator_runner_registry_and_services():
    """Verify MaceratorRunner loads assigned services in strict dependency order."""
    runner = get_node_runner("macerator")
    assert isinstance(runner, MaceratorRunner)
    assert runner.name == "macerator"
    assert runner.role == "powerhouse"

    services = runner.get_services()
    service_names = [s.name for s in services]
    assert service_names == [
        "consul",
        "redis",
        "postgres",
        "authentik",
        "photos",
        "cockpit",
        "home-assistant",
        "netdata",
        "code",
    ]


def test_macerator_runner_lifecycle_dispatch():
    """Verify MaceratorRunner dispatches lifecycle calls to services."""
    runner = get_node_runner("macerator")

    with patch.object(MaceratorRunner, "setup_host", return_value=True):
        mock_svc = MagicMock(spec=BaseService)
        mock_svc.name = "consul"
        mock_svc.up.return_value = True
        mock_svc.down.return_value = True

        with patch.object(runner, "_resolve_targets", return_value=[mock_svc]):
            up_res = runner.up(service_name="consul")
            assert up_res == {"consul": True}
            mock_svc.up.assert_called_once()

            down_res = runner.down(service_name="consul")
            assert down_res == {"consul": True}
            mock_svc.down.assert_called_once()
