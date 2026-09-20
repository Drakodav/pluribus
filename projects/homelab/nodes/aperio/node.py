"""Aperio public gateway node definition and orchestrator."""

from __future__ import annotations

import subprocess
from typing import Any

from nodes.base import BaseNodeRunner
from services.base import BaseService


class AperioNode(BaseNodeRunner):
    """Aperio Oracle Cloud Always-Free public ingress gateway."""

    name = "aperio"
    role = "gateway"
    provider = "oci"
    ssh_bastion = None

    @property
    def ssh_user(self) -> str:
        """SSH user for Aperio gateway."""
        from context import AppContext

        return AppContext().get_required_env("NODE_APERIO_SSH_USER")

    @property
    def ssh_port(self) -> int:
        """SSH port for Aperio gateway."""
        from context import AppContext

        return int(AppContext().get_required_env("NODE_APERIO_SSH_PORT"))

    @property
    def public_ip(self) -> str:
        """Public IPv4 address assigned to the gateway."""
        from context import AppContext

        return AppContext().get_required_env("NODE_APERIO_PUBLIC_IP")

    @property
    def backbone_ip(self) -> str:
        """WireGuard backbone mesh IP for Aperio."""
        from context import AppContext

        return AppContext().backbone_aperio_ip

    @property
    def public_key(self) -> str:
        """WireGuard public key for Aperio."""
        from context import AppContext

        return AppContext().get_required_env("NODE_APERIO_PUBLIC_KEY")

    def setup_host(self) -> bool:
        """Aperio host provisioning is handled via Terraform and cloud-init."""
        return True

    def get_services(self) -> list[BaseService]:
        """Aperio platform services are deployed as an integrated gateway stack."""
        return []

    def up(self, service_name: str | None = None) -> dict[str, bool]:
        """Deploy or synchronize Aperio gateway platform compose stack."""
        platform_compose = self.node_dir / "vm" / "platform" / "docker-compose.yml"
        if not platform_compose.exists():
            return {"aperio-platform": False}

        cmd = ["docker", "compose", "-f", str(platform_compose), "up", "-d"]
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def down(self, service_name: str | None = None) -> dict[str, bool]:
        """Stop Aperio gateway platform compose stack."""
        platform_compose = self.node_dir / "vm" / "platform" / "docker-compose.yml"
        if not platform_compose.exists():
            return {"aperio-platform": True}

        cmd = ["docker", "compose", "-f", str(platform_compose), "down"]
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def restart(self, service_name: str | None = None) -> dict[str, bool]:
        """Restart Aperio gateway platform compose stack."""
        platform_compose = self.node_dir / "vm" / "platform" / "docker-compose.yml"
        if not platform_compose.exists():
            return {"aperio-platform": False}

        cmd = ["docker", "compose", "-f", str(platform_compose), "restart"]
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def destroy(self, service_name: str | None = None) -> dict[str, bool]:
        """Tear down Aperio gateway platform compose stack."""
        platform_compose = self.node_dir / "vm" / "platform" / "docker-compose.yml"
        if not platform_compose.exists():
            return {"aperio-platform": True}

        cmd = ["docker", "compose", "-f", str(platform_compose), "down", "-v"]
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def status(self, service_name: str | None = None) -> dict[str, Any]:
        """Query status of Aperio platform stack."""
        platform_compose = self.node_dir / "vm" / "platform" / "docker-compose.yml"
        if not platform_compose.exists():
            return {"aperio-platform": "missing_compose_file"}

        cmd = [
            "docker",
            "compose",
            "-f",
            str(platform_compose),
            "ps",
            "--format",
            "{{.Name}}: {{.Status}}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            return {"aperio-platform": lines if lines else "stopped"}
        return {"aperio-platform": "error"}
