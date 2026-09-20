"""Application Context and Runtime Detection Singleton for Homelab."""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import TYPE_CHECKING, Any

from models.topology import HomelabTopology
from providers.consul import ConsulClient

if TYPE_CHECKING:
    from services.base import BaseService


class RuntimeInfo:
    """Inspected host environment and runtime privileges."""

    def __init__(self, hostname: str, topology: HomelabTopology | None = None) -> None:
        self.hostname = hostname.lower()
        self.is_root = (os.geteuid() == 0) if hasattr(os, "geteuid") else False
        self.user = os.environ.get("SUDO_USER") or os.environ.get("USER", "unknown")

        # Determine current node identity
        self.node_name: str | None = None
        if "macerator" in self.hostname:
            self.node_name = "macerator"
        elif "aperio" in self.hostname:
            self.node_name = "aperio"
        elif topology:
            for node_name in topology.nodes:
                if node_name in self.hostname:
                    self.node_name = node_name
                    break
            if not self.node_name:
                for gw_name in topology.gateways:
                    if gw_name in self.hostname:
                        self.node_name = gw_name
                        break

        # Allow explicit override via HOMELAB_NODE
        env_node = os.environ.get("HOMELAB_NODE")
        if env_node:
            self.node_name = env_node

    @property
    def is_macerator(self) -> bool:
        """True if executing natively on the Macerator powerhouse node."""
        return self.node_name == "macerator"

    @property
    def is_aperio(self) -> bool:
        """True if executing natively on the Aperio public gateway."""
        return self.node_name == "aperio"

    @property
    def is_local_workstation(self) -> bool:
        """True if executing on an operator workstation outside the mesh nodes."""
        return not self.is_macerator and not self.is_aperio


class AppContext:
    """Thread-safe singleton holding project configuration, runtime state, and clients."""

    _instance: AppContext | None = None
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> AppContext:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, project_root: Path | None = None) -> None:
        if self._initialized:
            return

        self.project_root = (
            project_root.resolve() if project_root else Path(__file__).resolve().parent
        )
        self.env_file = self.project_root / ".env"
        self.topology_file = self.project_root / "topology.yaml"
        self.services_dir = self.project_root / "services"
        self.nodes_dir = self.project_root / "nodes"

        # Load environment variables from disk into dictionary and os.environ
        self.env: dict[str, str] = self._load_env_file()

        # Topology (lazy initialized)
        self._topology: HomelabTopology | None = None

        # Inspect host runtime
        hostname = socket.gethostname()
        self.runtime = RuntimeInfo(hostname, topology=self._safe_load_topology())

        # Consul Client
        consul_url = os.environ.get(
            "CONSUL_HTTP_ADDR",
            self.get_consul_endpoint(self.runtime.node_name),
        )
        self.consul = ConsulClient(base_url=consul_url)

        self._initialized = True

    def _safe_load_topology(self) -> HomelabTopology | None:
        try:
            return HomelabTopology.build(self.project_root)
        except Exception:
            return None

    @property
    def topology(self) -> HomelabTopology:
        """Declarative topology model assembled from code and cached for the lifecycle."""
        if self._topology is None:
            self._topology = HomelabTopology.build(self.project_root)
        return self._topology

    @property
    def node_profiles(self) -> dict[str, dict[str, Any]]:
        """Resolved dictionary mapping known nodes to their roles, IPs, and Consul endpoints."""
        gw_ip = "10.10.0.1"
        mac_ip = "10.10.0.2"
        topo = self._safe_load_topology()
        if topo:
            if "aperio" in topo.gateways:
                gw_ip = str(topo.gateways["aperio"].backbone_ip)
            if "macerator" in topo.nodes:
                mac_ip = str(topo.nodes["macerator"].backbone_ip)

        return {
            "aperio": {
                "role": "gateway",
                "backbone_ip": gw_ip,
                "consul_endpoint": "http://127.0.0.1:8500",
                "fallback_consul_endpoint": f"http://{gw_ip}:8500",
            },
            "macerator": {
                "role": "powerhouse",
                "backbone_ip": mac_ip,
                "consul_endpoint": "http://127.0.0.1:8500",
                "fallback_consul_endpoint": f"http://{gw_ip}:8500",
            },
        }

    def get_consul_endpoint(self, node_name: str | None = None) -> str:
        """Determine the target Consul agent HTTP endpoint for a given node or runtime."""
        target = node_name or self.runtime.node_name
        if target in self.node_profiles:
            # If executing directly on that node, talk to local agent
            if self.runtime.node_name == target:
                return str(self.node_profiles[target]["consul_endpoint"])
            # If remote, talk to the node's backbone agent or gateway fallback
            return str(self.node_profiles[target]["fallback_consul_endpoint"])
        return "http://10.10.0.1:8500"

    def get_required_env(self, key: str) -> str:
        """Retrieve required environment variable or raise KeyError if missing."""
        val = os.environ.get(key, self.env.get(key, ""))
        if not val:
            raise KeyError(
                f"Required environment variable '{key}' is missing. "
                f"Please define it in '{self.env_file}' or host environment."
            )
        return val

    def get_env(self, key: str, default: str | None = None) -> str:
        """Get an environment variable from os.environ or loaded .env file."""
        return os.environ.get(key, self.env.get(key, default or ""))

    def __getitem__(self, key: str) -> str:
        """Access environment variables directly using dictionary syntax: ctx['KEY']."""
        return self.get_required_env(key)

    @property
    def root_domain(self) -> str:
        """Declared root domain from GLOBAL_ROOT_DOMAIN."""
        return self.get_required_env("GLOBAL_ROOT_DOMAIN")

    @property
    def backbone_macerator_ip(self) -> str:
        """WireGuard backbone IP for Macerator from NODE_MACERATOR_BACKBONE_IP."""
        return self.get_required_env("NODE_MACERATOR_BACKBONE_IP")

    @property
    def backbone_aperio_ip(self) -> str:
        """WireGuard backbone IP for Aperio from NODE_APERIO_BACKBONE_IP."""
        return self.get_required_env("NODE_APERIO_BACKBONE_IP")

    @property
    def acme_email(self) -> str:
        """Let's Encrypt ACME notification email from GLOBAL_ACME_EMAIL."""
        return self.get_required_env("GLOBAL_ACME_EMAIL")

    @property
    def mesh_subnet(self) -> str:
        """WireGuard mesh subnet CIDR from GLOBAL_MESH_SUBNET."""
        return self.get_required_env("GLOBAL_MESH_SUBNET")

    @property
    def mesh_port(self) -> int:
        """WireGuard mesh port from GLOBAL_MESH_PORT."""
        return int(self.get_required_env("GLOBAL_MESH_PORT"))

    def _load_env_file(self) -> dict[str, str]:
        env_map: dict[str, str] = {}
        if self.env_file.exists():
            for line in self.env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    env_map[k] = v
                    if k not in os.environ:
                        os.environ[k] = v
        return env_map

    def register_service_in_consul(
        self,
        service: BaseService,
        node_name: str | None = None,
    ) -> bool:
        """Register a service instance in Consul agent with Traefik tags and health checks."""
        target_node = node_name or self.runtime.node_name or "macerator"
        node_meta = self.node_profiles.get(target_node, {})
        backbone_ip = node_meta.get(
            "backbone_ip",
            self.backbone_macerator_ip
            if target_node == "macerator"
            else self.backbone_aperio_ip,
        )

        return self.consul.register_service_object(
            service=service,
            node_name=target_node,
            backbone_ip=backbone_ip,
            domain=self.root_domain,
        )

    def deregister_service_from_consul(
        self,
        service: BaseService,
        node_name: str | None = None,
    ) -> bool:
        """Deregister a service instance from Consul agent upon shutdown."""
        target_node = node_name or self.runtime.node_name or "macerator"
        service_id = f"{service.name}-{target_node}"
        return self.consul.deregister_service(service_id)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (primarily for testing and reloads)."""
        cls._instance = None
        cls._initialized = False
