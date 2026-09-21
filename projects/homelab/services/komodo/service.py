"""Komodo multi-server fleet management and monitoring service."""

from __future__ import annotations

from services.compose_base import ComposeService


class KomodoService(ComposeService):
    """Komodo Core multi-server fleet manager and cluster monitor."""

    name = "komodo"
    consul_name = "komodo"
    role = "fleet-ops"
    upstream_port = 9120
    exposure = "public"
    subdomain = "komodo"
    health_path = "/"

    def pre_up(self) -> None:
        """Ensure Komodo persistent storage directories exist under /opt/homelab/komodo."""
        self.ensure_dir("/opt/homelab/komodo/mongo")
        self.ensure_dir("/opt/homelab/komodo/mongo-config")
        self.ensure_dir("/opt/homelab/komodo/keys")
        self.ensure_dir("/opt/homelab/komodo/backups")
