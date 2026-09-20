"""PostgreSQL and pgAdmin database stack."""

from __future__ import annotations

import subprocess

from services.compose_base import ComposeService


class PgAdminService(ComposeService):
    """pgAdmin 4 web administration interface."""

    name = "pgadmin"
    consul_name = "pgadmin"
    role = "database-management"
    upstream_port = 80
    exposure = "public"
    subdomain = "pgadmin"
    health_path = "/misc/ping"

    def pre_up(self) -> None:
        """Ensure pgAdmin persistent volume exists with UID 5050 permissions."""
        self.ensure_dir("/opt/homelab/pgadmin", uid=5050, gid=5050)

    def up(self) -> bool:
        """Bring up pgAdmin container specifically."""
        self.pre_up()
        cmd = self._build_compose_cmd("up", "-d", "pgadmin")
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            self.post_up()
            return True
        return False

    def down(self) -> bool:
        """Stop pgAdmin container without affecting postgres."""
        cmd = self._build_compose_cmd("stop", "pgadmin")
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            self.post_down()
            return True
        return False

    def restart(self) -> bool:
        """Restart pgAdmin container."""
        cmd = self._build_compose_cmd("restart", "pgadmin")
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            self.post_up()
            return True
        return False

    def status(self) -> dict[str, str]:
        """Fetch running status of pgAdmin container only."""
        full_status = super().status()
        return {k: v for k, v in full_status.items() if "pgadmin" in k}


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

    def status(self) -> dict[str, str]:
        """Fetch running status of Postgres container only."""
        full_status = super().status()
        return {k: v for k, v in full_status.items() if "postgres" in k}
