"""PostgreSQL and pgAdmin database stack."""

from __future__ import annotations

from services.compose_base import ComposeService


class PostgresService(ComposeService):
    """PostgreSQL 16 with pgvector and pgAdmin 4."""

    name = "postgres"
    role = "database"
    upstream_port = 5432
    exposure = "internal"

    def pre_up(self) -> None:
        """Set strict directory permissions for PostgreSQL (UID 70) and pgAdmin (UID 5050)."""
        self.ensure_dir("/opt/homelab/postgres", uid=70, gid=70)
        self.ensure_dir("/opt/homelab/pgadmin", uid=5050, gid=5050)
