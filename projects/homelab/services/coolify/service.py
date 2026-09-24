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

    def get_traefik_tags(self, domain: str) -> list[str]:
        """Generate Traefik tags for Coolify UI, Soketi real-time, and terminal WebSockets."""
        tags = super().get_traefik_tags(domain)
        if not tags or not self.subdomain:
            return tags

        svc_name = self.registered_name
        subdomain = self.subdomain

        # Explicitly link base router to base service
        tags.append(f"traefik.http.routers.{svc_name}.service={svc_name}")

        # Real-time WebSockets (/app -> Soketi on port 6001)
        tags.extend(
            [
                f"traefik.http.routers.{svc_name}-realtime.rule=Host(`{subdomain}.{domain}`) && PathPrefix(`/app`)",
                f"traefik.http.routers.{svc_name}-realtime.entrypoints=websecure",
                f"traefik.http.routers.{svc_name}-realtime.tls.certresolver=myresolver",
                f"traefik.http.routers.{svc_name}-realtime.priority=100",
                f"traefik.http.routers.{svc_name}-realtime.service={svc_name}-realtime",
                f"traefik.http.services.{svc_name}-realtime.loadbalancer.server.port=6001",
            ]
        )

        # Web Terminal WebSockets (/terminal/ws -> Terminal server on port 6002)
        tags.extend(
            [
                f"traefik.http.routers.{svc_name}-terminal.rule=Host(`{subdomain}.{domain}`) && PathPrefix(`/terminal/ws`)",
                f"traefik.http.routers.{svc_name}-terminal.entrypoints=websecure",
                f"traefik.http.routers.{svc_name}-terminal.tls.certresolver=myresolver",
                f"traefik.http.routers.{svc_name}-terminal.priority=100",
                f"traefik.http.routers.{svc_name}-terminal.service={svc_name}-terminal",
                f"traefik.http.services.{svc_name}-terminal.loadbalancer.server.port=6002",
            ]
        )
        return tags
