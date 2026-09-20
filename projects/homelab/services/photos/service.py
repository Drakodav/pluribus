"""Immich high-performance photo and video backup stack."""

from __future__ import annotations

from services.compose_base import ComposeService


class PhotosService(ComposeService):
    """Immich photos and machine learning service stack."""

    name = "photos"
    role = "media"
    subdomain = "photos"
    upstream_port = 2283
    exposure = "sso"
    health_path = "/api/server-info/ping"

    def pre_up(self) -> None:
        """Ensure Immich upload library and database directories exist."""
        self.ensure_dir("/opt/homelab/immich/library")
        self.ensure_dir("/opt/homelab/immich/db")
