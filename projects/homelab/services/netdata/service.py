"""Netdata real-time monitoring and telemetry agent."""

from __future__ import annotations

from services.compose_base import ComposeService


class NetdataService(ComposeService):
    """Netdata host and container observability stack."""

    name = "netdata"
    role = "observability"
    subdomain = "netdata"
    upstream_port = 19999
    exposure = "sso"

    def pre_up(self) -> None:
        """Ensure Netdata persistent storage directory exists."""
        self.ensure_dir("/opt/homelab/netdata")
