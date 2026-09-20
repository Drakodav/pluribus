"""Macerator powerhouse node orchestrator and service runner."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from nodes.base import BaseNodeRunner
from services.base import BaseService
from services.registry import get_service

ORDERED_SERVICES = [
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


class MaceratorRunner(BaseNodeRunner):
    """Host setup and service lifecycle runner for the Macerator powerhouse node."""

    name = "macerator"
    role = "powerhouse"

    def setup_host(self) -> bool:
        """Idempotently prepare host storage directories, permissions, and firewall rules."""
        # 1. Storage Scaffolding
        storage_dirs = [
            Path("/opt/homelab"),
            Path("/opt/homelab/postgres"),
            Path("/opt/homelab/pgadmin"),
            Path("/opt/homelab/authentik/media"),
            Path("/opt/homelab/authentik/custom-templates"),
            Path("/opt/homelab/authentik/certs"),
            Path("/opt/homelab/immich/library"),
            Path("/opt/homelab/immich/db"),
            Path("/opt/homelab/netdata"),
            Path("/opt/homelab/home-assistant"),
            Path("/opt/homelab/matterjs-server"),
        ]

        for d in storage_dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                subprocess.run(["sudo", "mkdir", "-p", str(d)], check=False)

        # Permissions: PostgreSQL (UID 70 on Alpine) and pgAdmin (UID 5050)
        pg_dir = Path("/opt/homelab/postgres")
        if pg_dir.exists():
            try:
                os.chown(pg_dir, 70, 70)
            except PermissionError:
                subprocess.run(
                    ["sudo", "chown", "-R", "70:70", str(pg_dir)], check=False
                )

        pgadmin_dir = Path("/opt/homelab/pgadmin")
        if pgadmin_dir.exists():
            try:
                os.chown(pgadmin_dir, 5050, 5050)
            except PermissionError:
                subprocess.run(
                    ["sudo", "chown", "-R", "5050:5050", str(pgadmin_dir)], check=False
                )

        # 2. Host Networking & Discovery Firewall Configuration (iptables)
        if shutil.which("iptables"):
            # Set FORWARD policy to ACCEPT if currently DROP
            subprocess.run(["sudo", "iptables", "-P", "FORWARD", "ACCEPT"], check=False)

            # mDNS (5353 UDP) and SSDP (1900 UDP) rules for local device discovery
            rules = [
                ("INPUT", "5353"),
                ("OUTPUT", "5353"),
                ("INPUT", "1900"),
                ("OUTPUT", "1900"),
            ]
            for chain, port in rules:
                check_cmd = [
                    "sudo",
                    "iptables",
                    "-C",
                    chain,
                    "-p",
                    "udp",
                    "--dport",
                    port,
                    "-j",
                    "ACCEPT",
                ]
                res = subprocess.run(check_cmd, capture_output=True, check=False)
                if res.returncode != 0:
                    add_cmd = [
                        "sudo",
                        "iptables",
                        "-A",
                        chain,
                        "-p",
                        "udp",
                        "--dport",
                        port,
                        "-j",
                        "ACCEPT",
                    ]
                    subprocess.run(add_cmd, check=False)

        return True

    def get_services(self) -> list[BaseService]:
        """Return the list of services assigned to Macerator in dependency order."""
        return [get_service(s, self.project_root) for s in ORDERED_SERVICES]

    def _resolve_targets(self, service_name: str | None = None) -> list[BaseService]:
        if service_name:
            # Handle alias 'ha'
            canonical = "home-assistant" if service_name == "ha" else service_name
            if canonical not in ORDERED_SERVICES:
                valid = ", ".join(ORDERED_SERVICES)
                raise ValueError(
                    f"Service '{service_name}' is not assigned to macerator. Valid: {valid}"
                )
            return [get_service(canonical, self.project_root)]
        return self.get_services()

    def up(self, service_name: str | None = None) -> dict[str, bool]:
        """Prepare host prerequisites and bring up services in order."""
        self.setup_host()
        targets = self._resolve_targets(service_name)
        results: dict[str, bool] = {}
        for svc in targets:
            results[svc.name] = svc.up()
        return results

    def down(self, service_name: str | None = None) -> dict[str, bool]:
        """Gracefully stop services (in reverse order if stopping all)."""
        targets = self._resolve_targets(service_name)
        if not service_name:
            targets = list(reversed(targets))
        results: dict[str, bool] = {}
        for svc in targets:
            results[svc.name] = svc.down()
        return results

    def restart(self, service_name: str | None = None) -> dict[str, bool]:
        """Restart services."""
        targets = self._resolve_targets(service_name)
        results: dict[str, bool] = {}
        for svc in targets:
            results[svc.name] = svc.restart()
        return results

    def destroy(self, service_name: str | None = None) -> dict[str, bool]:
        """Tear down services and purge ephemeral resources."""
        targets = self._resolve_targets(service_name)
        if not service_name:
            targets = list(reversed(targets))
        results: dict[str, bool] = {}
        for svc in targets:
            results[svc.name] = svc.destroy()
        return results

    def status(self, service_name: str | None = None) -> dict[str, Any]:
        """Query runtime status of services."""
        targets = self._resolve_targets(service_name)
        return {svc.name: svc.status() for svc in targets}
