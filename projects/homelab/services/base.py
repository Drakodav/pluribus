"""Abstract Base Class for Homelab services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal


class BaseService(ABC):
    """Abstract Base Class defining the service lifecycle contract."""

    name: str
    consul_name: str | None = None
    role: str
    upstream_port: int
    exposure: Literal["public", "sso", "internal"] = "internal"
    subdomain: str | None = None
    health_path: str | None = None
    auth_middleware: str | None = None

    def __init__(self, service_dir: Path) -> None:
        self.service_dir = service_dir

    @property
    def registered_name(self) -> str:
        """Service name used for Consul registration and Traefik routing."""
        return self.consul_name or self.name

    def build(self) -> bool:
        """Build custom container images if required. Default implementation is a no-op."""
        return True

    @abstractmethod
    def up(self) -> bool:
        """Idempotently bring up the service. Always update to the latest version if possible."""
        ...

    @abstractmethod
    def down(self) -> bool:
        """Gracefully stop the service."""
        ...

    @abstractmethod
    def restart(self) -> bool:
        """Restart service containers."""
        ...

    @abstractmethod
    def destroy(self) -> bool:
        """DANGEROUS: Tear down containers and clean up ephemeral resources."""
        ...

    @abstractmethod
    def status(self) -> dict[str, str]:
        """Query container runtime status and health."""
        ...

    def get_traefik_tags(self, domain: str) -> list[str]:
        """Generate Traefik router, service, TLS, and middleware tags for ingress routing."""
        if not self.subdomain or self.exposure == "internal":
            return []

        svc_name = self.registered_name
        tags = [
            "traefik.enable=true",
            f"traefik.http.routers.{svc_name}.rule=Host(`{self.subdomain}.{domain}`)",
            f"traefik.http.routers.{svc_name}.entrypoints=websecure",
            f"traefik.http.routers.{svc_name}.tls.certresolver=myresolver",
            f"traefik.http.services.{svc_name}.loadbalancer.server.port={self.upstream_port}",
        ]
        if self.exposure == "sso":
            middleware = self.auth_middleware or f"auth-{svc_name}@docker"
            tags.append(f"traefik.http.routers.{svc_name}.middlewares={middleware}")
        return tags

    def pre_up(self) -> None:
        """Hook called before bringing containers up (permissions, directories)."""
        pass

    def post_up(self) -> None:
        """Hook called after containers are up (registers in Consul with health check)."""
        from context import AppContext

        ctx = AppContext()
        ctx.register_service_in_consul(self)

    def post_down(self) -> None:
        """Hook called after containers are stopped (deregisters from Consul)."""
        from context import AppContext

        ctx = AppContext()
        ctx.deregister_service_from_consul(self)
