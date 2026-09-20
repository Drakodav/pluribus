"""Root declarative homelab topology model assembled dynamically from Python code."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from models.mesh import MeshConfig
from models.node import ComputeNode, GatewayNode, SSHConfig
from models.service import ServiceConfig


class HomelabTopology(BaseModel):
    """Root declarative homelab topology model."""

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
    def build(cls, project_root: Path | None = None) -> HomelabTopology:
        """Dynamically assemble cluster topology directly from registered Python code."""
        from context import AppContext
        from nodes.registry import get_all_nodes
        from services.registry import get_all_services

        ctx = AppContext(project_root)
        domain = ctx.root_domain

        # 1. Gather all registered services
        services_map = get_all_services(project_root)
        services_dict: dict[str, ServiceConfig] = {}
        for s_name, svc in services_map.items():
            services_dict[s_name] = ServiceConfig(
                role=svc.role,
                subdomain=svc.subdomain,
                upstream_port=svc.upstream_port,
                exposure=svc.exposure,
                health_path=svc.health_path,
            )

        # 2. Gather all registered nodes
        nodes_map = get_all_nodes(project_root)
        gateways_dict: dict[str, GatewayNode] = {}
        nodes_dict: dict[str, ComputeNode] = {}

        for n_name, runner in nodes_map.items():
            if runner.role == "gateway":
                gateways_dict[n_name] = GatewayNode(
                    provider=runner.provider or "oci",
                    role=runner.role,
                    public_ip=runner.public_ip or "[IP_ADDRESS]",  # type: ignore[arg-type]
                    backbone_ip=runner.backbone_ip,  # type: ignore[arg-type]
                    public_key=runner.public_key,
                    ssh=SSHConfig(
                        user=runner.ssh_user,
                        port=runner.ssh_port,
                        bastion=runner.ssh_bastion,
                    ),
                )
            else:
                assigned_svcs = [s.name for s in runner.get_services()]
                nodes_dict[n_name] = ComputeNode(
                    hardware=runner.hardware,
                    role=runner.role,
                    backbone_ip=runner.backbone_ip,  # type: ignore[arg-type]
                    public_key=runner.public_key,
                    ssh=SSHConfig(
                        user=runner.ssh_user,
                        port=runner.ssh_port,
                        bastion=runner.ssh_bastion,
                    ),
                    services=assigned_svcs,
                )

        return cls(
            version="1",
            domain=domain,
            mesh=MeshConfig(),
            gateways=gateways_dict,
            nodes=nodes_dict,
            services=services_dict,
        )

    @classmethod
    def load(cls, path: Path | str | None = None) -> HomelabTopology:
        """Load topology directly from code, with optional fallback to YAML if specified."""
        if path is not None:
            p = Path(path)
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    raw_data: Any = yaml.safe_load(f)
                return cls.model_validate(raw_data)

        # Default: Pure Python Code-as-Configuration assembly
        return cls.build()

    def to_dict(self) -> dict[str, Any]:
        """Serialize topology model to plain dictionary."""
        return self.model_dump(mode="json")

    def to_yaml(self) -> str:
        """Export dynamic cluster topology to YAML formatted string."""
        return yaml.dump(self.to_dict(), sort_keys=False)
