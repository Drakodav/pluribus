"""Abstract Base Class for Homelab services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal


class BaseService(ABC):
    """Abstract Base Class defining the service lifecycle contract."""

    name: str
    role: str
    upstream_port: int
    exposure: Literal["public", "sso", "internal"] = "internal"
    subdomain: str | None = None
    health_path: str | None = None

    def __init__(self, service_dir: Path) -> None:
        self.service_dir = service_dir

    @abstractmethod
    def up(self) -> bool:
        """Idempotently bring up the service. Always update to the latest version if possible"""
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

    def pre_up(self) -> None:
        """Hook called before bringing containers up (permissions, directories)."""
        pass

    def post_up(self) -> None:
        """Hook called after containers are up (e.g. Consul registration)."""
        pass
