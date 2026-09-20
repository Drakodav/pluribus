"""Root declarative homelab topology model and disk loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from models.mesh import MeshConfig
from models.node import ComputeNode, GatewayNode
from models.service import ServiceConfig


class HomelabTopology(BaseModel):
    """Root declarative homelab topology."""

    version: str = "1"
    domain: str = "vlmd.cc"
    mesh: MeshConfig = Field(default_factory=MeshConfig)
    gateways: dict[str, GatewayNode] = Field(default_factory=dict)
    nodes: dict[str, ComputeNode] = Field(default_factory=dict)
    services: dict[str, ServiceConfig] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_integrity(self) -> HomelabTopology:
        """Verify cross-resource references and detect IP address collisions."""
        # 1. Check IP uniqueness
        used_ips: dict[str, str] = {}
        for gw_name, gw in self.gateways.items():
            ip_str = str(gw.backbone_ip)
            if ip_str in used_ips:
                raise ValueError(
                    f"Backbone IP collision: {ip_str} used by both {used_ips[ip_str]} and {gw_name}"
                )
            used_ips[ip_str] = f"gateway '{gw_name}'"

        for node_name, node in self.nodes.items():
            ip_str = str(node.backbone_ip)
            if ip_str in used_ips:
                raise ValueError(
                    f"Backbone IP collision: {ip_str} used by both {used_ips[ip_str]} and {node_name}"
                )
            used_ips[ip_str] = f"node '{node_name}'"

        # 2. Check service references
        for node_name, node in self.nodes.items():
            for svc_name in node.services:
                if svc_name not in self.services:
                    raise ValueError(
                        f"Node '{node_name}' references undeclared service '{svc_name}'. "
                        f"Declared services are: {list(self.services.keys())}"
                    )

        # 3. Check bastion references
        for node_name, node in self.nodes.items():
            if node.ssh.bastion and node.ssh.bastion not in self.gateways:
                raise ValueError(
                    f"Node '{node_name}' specifies unknown bastion gateway '{node.ssh.bastion}'. "
                    f"Declared gateways are: {list(self.gateways.keys())}"
                )

        return self

    @classmethod
    def load(cls, path: Path | str | None = None) -> HomelabTopology:
        """Load and parse topology.yaml from disk."""
        if path is None:
            path = Path(__file__).resolve().parent.parent / "topology.yaml"
        else:
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Topology file not found at: {path}")

        with open(path, encoding="utf-8") as f:
            raw_data: Any = yaml.safe_load(f)

        return cls.model_validate(raw_data)
