import shutil
from pathlib import Path

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
        """Ensure Home Assistant and Matter persistent volumes exist with initial configs."""
        target_dir = Path("/opt/homelab/home-assistant")
        self.ensure_dir(target_dir)
        self.ensure_dir("/opt/homelab/matterjs-server", uid=1000, gid=1000)

        config_files = [
            "configuration.yaml",
            "automations.yaml",
            "scenes.yaml",
            "scripts.yaml",
        ]
        for filename in config_files:
            src = self.service_dir / filename
            dst = target_dir / filename
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
