"""Coolify developer PaaS orchestration service."""

from __future__ import annotations

from services.compose_base import ComposeService


class CoolifyService(ComposeService):
    """Coolify developer PaaS for automated git builds, previews, and microservices."""

    name = "coolify"
    consul_name = "coolify"
    role = "developer-paas"
    upstream_port = 8000
    exposure = "public"
    subdomain = "coolify"
    health_path = "/"

    def pre_up(self) -> None:
        """Ensure Coolify persistent storage directories exist under /opt/homelab/coolify."""
        self.ensure_dir("/opt/homelab/coolify/data", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/db", uid=70, gid=70)
        self.ensure_dir("/opt/homelab/coolify/redis", uid=999, gid=999)
        self.ensure_dir("/opt/homelab/coolify/ssh", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/ssh/keys", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/ssh/mux", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/applications", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/databases", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/services", uid=9999, gid=0)
        self.ensure_dir("/opt/homelab/coolify/backups", uid=9999, gid=0)
