"""Unit tests for Service and Node Runner lifecycle abstractions."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from context import AppContext, RuntimeInfo
from nodes.macerator.runner import MaceratorRunner
from nodes.registry import get_node_runner
from providers.consul import ConsulClient
from services.base import BaseService
from services.cockpit.service import CockpitService
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
        "pgadmin",
        "photos",
        "postgres",
        "redis",
    }
    assert set(services.keys()) == expected_services

    # Verify alias resolution
    assert get_service("auth").name == "authentik"
    assert get_service("manage").name == "cockpit"
    assert get_service("monitor").name == "netdata"
    assert get_service("ha").name == "home-assistant"
    assert get_service("pg-admin").name == "pgadmin"
    assert get_service("immich").name == "photos"

    # Verify invalid service raises ValueError
    with pytest.raises(ValueError) as exc:
        get_service("nonexistent-service")
    assert "Unknown service" in str(exc.value)


def test_app_context_singleton_and_env():
    """Verify AppContext behaves as a singleton and provides env helpers."""
    AppContext.reset()
    ctx1 = AppContext()
    ctx2 = AppContext()
    assert ctx1 is ctx2

    assert ctx1.root_domain == "vlmd.cc"
    assert ctx1.backbone_macerator_ip == "10.10.0.2"
    assert ctx1.backbone_aperio_ip == "10.10.0.1"
    assert "macerator" in ctx1.node_profiles
    assert "aperio" in ctx1.node_profiles


def test_runtime_info_detection():
    """Verify host runtime detection for macerator, aperio, and workstations."""
    # Test Macerator
    info_mac = RuntimeInfo("macerator-host")
    assert info_mac.is_macerator is True
    assert info_mac.is_aperio is False
    assert info_mac.is_local_workstation is False

    # Test Aperio
    info_ap = RuntimeInfo("aperio-vm")
    assert info_ap.is_aperio is True
    assert info_ap.is_macerator is False
    assert info_ap.is_local_workstation is False

    # Test Workstation
    info_ws = RuntimeInfo("developer-laptop")
    assert info_ws.is_local_workstation is True
    assert info_ws.is_macerator is False
    assert info_ws.is_aperio is False

    # Test explicit HOMELAB_NODE override
    with patch.dict(os.environ, {"HOMELAB_NODE": "macerator"}):
        info_over = RuntimeInfo("random-host")
        assert info_over.is_macerator is True


def test_traefik_tags_generation():
    """Verify Traefik router, TLS, entrypoints, and middleware tag generation."""
    photos = get_service("photos")
    tags = photos.get_traefik_tags("vlmd.cc")
    assert "traefik.enable=true" in tags
    assert "traefik.http.routers.photos.rule=Host(`photos.vlmd.cc`)" in tags
    assert "traefik.http.routers.photos.entrypoints=websecure" in tags
    assert "traefik.http.routers.photos.tls.certresolver=myresolver" in tags
    assert "traefik.http.services.photos.loadbalancer.server.port=2283" in tags
    assert not any("middlewares" in t for t in tags)

    # SSO service includes ForwardAuth middleware
    code = get_service("code")
    code_tags = code.get_traefik_tags("vlmd.cc")
    assert "traefik.http.routers.code.middlewares=auth-code@docker" in code_tags

    # Internal service generates no Traefik tags
    redis = get_service("redis")
    assert redis.get_traefik_tags("vlmd.cc") == []

    # Cockpit service includes primary manage rule, cockpit alias, and auth-cockpit middleware
    cockpit = CockpitService(Path("/mock/cockpit"))
    c_tags = cockpit.get_traefik_tags("vlmd.cc")
    assert "traefik.http.routers.manage.rule=Host(`manage.vlmd.cc`)" in c_tags
    assert "traefik.http.routers.manage-alias.rule=Host(`cockpit.vlmd.cc`)" in c_tags
    assert "traefik.http.routers.manage.middlewares=auth-cockpit@docker" in c_tags


def test_consul_mandatory_health_checks():
    """Verify Consul registration creates HTTP or TCP health check without exception."""
    client = ConsulClient()

    # Service with health_path -> HTTP check
    authentik = get_service("authentik")
    auth_payload = client.build_service_payload_from_object(
        authentik, "macerator", "10.10.0.2", "vlmd.cc"
    )
    assert "Check" in auth_payload
    assert "HTTP" in auth_payload["Check"]
    assert "http://10.10.0.2:9000/-/health/ready/" in auth_payload["Check"]["HTTP"]

    # Service without health_path -> TCP check
    postgres = get_service("postgres")
    pg_payload = client.build_service_payload_from_object(
        postgres, "macerator", "10.10.0.2", "vlmd.cc"
    )
    assert "Check" in pg_payload
    assert "TCP" in pg_payload["Check"]
    assert pg_payload["Check"]["TCP"] == "10.10.0.2:5432"


def test_all_eight_services_consul_connection():
    """Verify all 8 external services connect to Consul with health checks and Traefik routing."""
    client = ConsulClient()
    services_to_verify = [
        ("auth", "auth", 9000, "public", "/-/health/ready/"),
        ("code", "code", 8443, "sso", "/healthz"),
        ("consul", "consul", 8500, "sso", "/v1/status/leader"),
        ("home-assistant", "home-assistant", 8123, "public", "/manifest.json"),
        ("manage", "manage", 9090, "sso", "/ping"),
        ("monitor", "monitor", 19999, "sso", "/api/v1/info"),
        ("pgadmin", "pgadmin", 80, "public", "/misc/ping"),
        ("photos", "photos", 2283, "public", "/api/server/ping"),
    ]

    for (
        alias,
        expected_consul_name,
        port,
        exp,
        expected_health_path,
    ) in services_to_verify:
        svc = get_service(alias)
        assert svc.registered_name == expected_consul_name
        assert svc.upstream_port == port
        assert svc.exposure == exp

        payload = client.build_service_payload_from_object(
            svc, "macerator", "10.10.0.2", "vlmd.cc"
        )
        assert payload["Name"] == expected_consul_name
        assert payload["Port"] == port
        assert payload["Address"] == "10.10.0.2"

        # Verify Traefik tags
        assert "traefik.enable=true" in payload["Tags"]
        assert (
            f"traefik.http.services.{expected_consul_name}.loadbalancer.server.port={port}"
            in payload["Tags"]
        )

        # Verify Mandatory Health Check
        assert "Check" in payload
        if expected_health_path:
            assert "HTTP" in payload["Check"]
            assert (
                f"http://10.10.0.2:{port}{expected_health_path}"
                == payload["Check"]["HTTP"]
            )
        else:
            assert "TCP" in payload["Check"]
            assert f"10.10.0.2:{port}" == payload["Check"]["TCP"]


def test_consul_deregister():
    """Verify deregister_service sends PUT to consul agent endpoint."""
    client = ConsulClient()
    mock_resp = MagicMock(status_code=200)

    with patch("httpx.Client.put", return_value=mock_resp) as mock_put:
        assert client.deregister_service("photos-macerator") is True
        assert mock_put.call_args[0][0].endswith(
            "/v1/agent/service/deregister/photos-macerator"
        )


def test_compose_service_lifecycle():
    """Verify ComposeService lifecycle commands invoke docker compose with --env-file."""
    AppContext.reset()
    service_dir = Path("/mock/service")
    service = ComposeService(service_dir)
    service.name = "mock-service"

    with patch.object(Path, "exists", return_value=True):
        with patch.object(service, "post_up") as mock_post_up:
            with patch.object(service, "post_down") as mock_post_down:
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)

                    # Test up()
                    assert service.up() is True
                    mock_post_up.assert_called_once()
                    assert "--env-file" in mock_run.call_args[0][0]

                    # Test down()
                    mock_run.reset_mock()
                    assert service.down() is True
                    mock_post_down.assert_called_once()
                    assert "--env-file" in mock_run.call_args[0][0]
                    assert "down" in mock_run.call_args[0][0]

                    # Test restart()
                    mock_run.reset_mock()
                    mock_post_up.reset_mock()
                    assert service.restart() is True
                    mock_post_up.assert_called_once()

                    # Test destroy()
                    mock_run.reset_mock()
                    mock_post_down.reset_mock()
                    assert service.destroy() is True
                    mock_post_down.assert_called_once()

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
        "pgadmin",
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


def test_postgres_has_build_and_pre_up_checks():
    """Verify PostgresService detects custom Dockerfile and checks init scripts."""
    postgres = get_service("postgres")
    assert getattr(postgres, "has_build", False) is True

    # Other services should not have a Dockerfile
    redis = get_service("redis")
    assert getattr(redis, "has_build", False) is False

    # Verify missing Dockerfile or SQL init raises in pre_up
    with patch.object(Path, "exists", side_effect=[False, True]):
        with pytest.raises(FileNotFoundError) as exc:
            postgres.pre_up()
        assert "Dockerfile" in str(exc.value)

    with patch.object(Path, "exists", side_effect=[True, False]):
        with pytest.raises(FileNotFoundError) as exc:
            postgres.pre_up()
        assert "init script" in str(exc.value)


def test_postgres_build_triggers_compose_build():
    """Verify PostgresService.build() calls docker compose build."""
    postgres = get_service("postgres")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert postgres.build() is True
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "build" in cmd
        assert "--env-file" in cmd


def test_macerator_runner_build_dispatch():
    """Verify MaceratorRunner.build() only triggers build on services with Dockerfile."""
    runner = get_node_runner("macerator")
    mock_pg = MagicMock(spec=BaseService)
    mock_pg.name = "postgres"
    mock_pg.has_build = True
    mock_pg.build.return_value = True

    mock_redis = MagicMock(spec=BaseService)
    mock_redis.name = "redis"
    mock_redis.has_build = False

    with patch.object(runner, "_resolve_targets", return_value=[mock_pg, mock_redis]):
        res = runner.build()
        assert res == {"postgres": True}
        mock_pg.build.assert_called_once()
        mock_redis.build.assert_not_called()
