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
    exposure = "public"
    health_path = "/manifest.json"

    def pre_up(self) -> None:
        """Ensure Home Assistant and Matter persistent volumes exist."""
        self.ensure_dir("/opt/homelab/home-assistant")
        self.ensure_dir("/opt/homelab/matterjs-server", uid=1000, gid=1000)
