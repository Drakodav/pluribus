"""Abstract Base Class for Homelab node runners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from services.base import BaseService


class BaseNodeRunner(ABC):
    """Abstract orchestrator for node provisioning, host setup, and service dispatch."""

    name: str
    role: str

    def __init__(self, node_dir: Path, project_root: Path | None = None) -> None:
        self.node_dir = node_dir
        self.project_root = project_root or node_dir.parent.parent

    @abstractmethod
    def setup_host(self) -> bool:
        """Configure host-level prerequisites, directories, and firewall."""
        ...

    @abstractmethod
    def get_services(self) -> list[BaseService]:
        """Return ordered list of services assigned to this node."""
        ...

    @abstractmethod
    def up(self, service_name: str | None = None) -> dict[str, bool]:
        """Idempotently prepare host and start assigned services in dependency order."""
        ...

    @abstractmethod
    def down(self, service_name: str | None = None) -> dict[str, bool]:
        """Gracefully stop assigned services."""
        ...

    @abstractmethod
    def restart(self, service_name: str | None = None) -> dict[str, bool]:
        """Restart assigned services."""
        ...

    @abstractmethod
    def destroy(self, service_name: str | None = None) -> dict[str, bool]:
        """Tear down services and purge ephemeral resources."""
        ...

    @abstractmethod
    def status(self, service_name: str | None = None) -> dict[str, Any]:
        """Query runtime status of node host prerequisites and assigned services."""
        ...
