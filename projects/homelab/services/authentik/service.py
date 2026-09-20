"""Authentik Identity and SSO provider."""

from __future__ import annotations

from services.compose_base import ComposeService


class AuthentikService(ComposeService):
    """Authentik Server and Worker identity stack."""

    name = "authentik"
    role = "identity"
    subdomain = "auth"
    upstream_port = 9000
    exposure = "public"
    health_path = "/-/health/ready/"

    def pre_up(self) -> None:
        """Ensure Authentik media, custom templates, and certificate directories exist."""
        self.ensure_dir("/opt/homelab/authentik/media")
        self.ensure_dir("/opt/homelab/authentik/custom-templates")
        self.ensure_dir("/opt/homelab/authentik/certs")
