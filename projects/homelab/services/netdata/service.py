"""Netdata real-time monitoring and telemetry agent."""

from __future__ import annotations

from services.compose_base import ComposeService


class NetdataService(ComposeService):
    """Netdata host and container observability stack."""

    name = "netdata"
    consul_name = "monitor"
    role = "observability"
    subdomain = "monitor"
    upstream_port = 19999
    exposure = "sso"
    auth_middleware = "auth-traefik@docker"
    health_path = "/api/v1/info"

    def get_traefik_tags(self, domain: str) -> list[str]:
        """Support both monitor.<domain> and netdata.<domain> routing rules."""
        tags = super().get_traefik_tags(domain)
        tags.extend(
            [
                f"traefik.http.routers.{self.registered_name}-alias.rule=Host(`netdata.{domain}`)",
                f"traefik.http.routers.{self.registered_name}-alias.entrypoints=websecure",
                f"traefik.http.routers.{self.registered_name}-alias.tls.certresolver=myresolver",
                f"traefik.http.routers.{self.registered_name}-alias.service={self.registered_name}",
                f"traefik.http.routers.{self.registered_name}-alias.middlewares={self.auth_middleware}",
            ]
        )
        return tags

    def pre_up(self) -> None:
        """Ensure Netdata persistent storage directory exists."""
        self.ensure_dir("/opt/homelab/netdata")
