"""PostgreSQL and pgAdmin database stack."""

from __future__ import annotations

from services.compose_base import ComposeService


class PgAdminService(ComposeService):
    """pgAdmin 4 web administration interface."""

    name = "pgadmin"
    consul_name = "pgadmin"
    role = "database-management"
    upstream_port = 80
    exposure = "sso"
    subdomain = "pgadmin"
    health_path = "/misc/ping"


class PostgresService(ComposeService):
    """PostgreSQL 16 with pgvector and pgAdmin 4."""

    name = "postgres"
    consul_name = "postgres"
    role = "database"
    upstream_port = 5432
    exposure = "internal"

    def pre_up(self) -> None:
        """Set strict directory permissions and verify custom Dockerfile and init scripts."""
        dockerfile = self.service_dir / "Dockerfile"
        if not dockerfile.exists():
            raise FileNotFoundError(
                f"Missing required PostgreSQL Dockerfile: {dockerfile}"
            )

        init_sql = self.service_dir / "init-immich.sql"
        if not init_sql.exists():
            raise FileNotFoundError(
                f"Missing required PostgreSQL init script: {init_sql}"
            )

        self.ensure_dir("/opt/homelab/postgres", uid=70, gid=70)
        self.ensure_dir("/opt/homelab/pgadmin", uid=5050, gid=5050)

    def post_up(self) -> None:
        """Register both PostgreSQL and pgAdmin in Consul with health checks."""
        super().post_up()
        from context import AppContext

        ctx = AppContext()
        pgadmin = PgAdminService(self.service_dir)
        ctx.register_service_in_consul(pgadmin)

    def post_down(self) -> None:
        """Deregister both PostgreSQL and pgAdmin from Consul."""
        super().post_down()
        from context import AppContext

        ctx = AppContext()
        pgadmin = PgAdminService(self.service_dir)
        ctx.deregister_service_from_consul(pgadmin)
