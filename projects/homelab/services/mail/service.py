"""Postfix transactional mail relay service stack."""

from __future__ import annotations

from services.compose_base import ComposeService


class MailRelayService(ComposeService):
    """Postfix transactional mail relay for internal homelab services."""

    name = "mail"
    consul_name = "mail"
    role = "relay"
    upstream_port = 25
    exposure = "internal"

    def pre_up(self) -> None:
        """Ensure mail spool storage directory exists before launching container."""
        self.ensure_dir("/opt/homelab/mail/spool")
