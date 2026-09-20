"""Home Assistant smart home automation stack."""

from __future__ import annotations

from services.compose_base import ComposeService


class HomeAssistantService(ComposeService):
    """Home Assistant Core with Matter integration."""

    name = "home-assistant"
    consul_name = "home-assistant"
    role = "automation"
    subdomain = "home-assistant"
    upstream_port = 8123
    exposure = "sso"
    health_path = "/manifest.json"

    def get_traefik_tags(self, domain: str) -> list[str]:
        """Support both ha.<domain> and home-assistant.<domain> routing rules."""
        tags = super().get_traefik_tags(domain)
        tags.extend(
            [
                f"traefik.http.routers.{self.registered_name}-alias.rule=Host(`home-assistant.{domain}`)",
                f"traefik.http.routers.{self.registered_name}-alias.entrypoints=websecure",
                f"traefik.http.routers.{self.registered_name}-alias.tls.certresolver=myresolver",
                f"traefik.http.routers.{self.registered_name}-alias.service={self.registered_name}",
            ]
        )
        if self.exposure == "sso":
            middleware = self.auth_middleware or f"auth-{self.registered_name}@docker"
            tags.append(
                f"traefik.http.routers.{self.registered_name}-alias.middlewares={middleware}"
            )
        return tags

    def pre_up(self) -> None:
        """Ensure Home Assistant and Matter persistent volumes exist."""
        self.ensure_dir("/opt/homelab/home-assistant")
        self.ensure_dir("/opt/homelab/matterjs-server", uid=1000, gid=1000)
