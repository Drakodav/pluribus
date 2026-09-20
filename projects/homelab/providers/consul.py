"""Consul Service Discovery client."""

from __future__ import annotations

from typing import Any

import httpx

from models.node import ComputeNode
from models.service import ServiceConfig
from models.topology import HomelabTopology


class ConsulClient:
    """Type-safe client for Consul Agent and Catalog HTTP APIs."""

    def __init__(self, base_url: str = "http://10.10.0.1:8500", timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def build_service_payload(
        self,
        service_name: str,
        service: ServiceConfig,
        node_name: str,
        node: ComputeNode,
    ) -> dict[str, Any]:
        """Construct the canonical Consul Agent service registration JSON payload."""
        tags = [
            f"exposure={service.exposure}",
            f"node={node_name}",
            f"role={service.role}",
            "managed-by=homelab-engine",
        ]
        if service.subdomain:
            tags.append(f"subdomain={service.subdomain}")

        payload: dict[str, Any] = {
            "ID": f"{service_name}-{node_name}",
            "Name": service_name,
            "Tags": tags,
            "Address": str(node.backbone_ip),
            "Port": service.upstream_port,
            "Meta": {
                "node": node_name,
                "role": service.role,
                "exposure": service.exposure,
            },
        }

        if service.health_path:
            payload["Check"] = {
                "HTTP": f"http://{node.backbone_ip}:{service.upstream_port}{service.health_path}",
                "Interval": "15s",
                "Timeout": "3s",
                "DeregisterCriticalServiceAfter": "10m",
            }

        return payload

    def register_service(
        self,
        service_name: str,
        service: ServiceConfig,
        node_name: str,
        node: ComputeNode,
    ) -> bool:
        """Register a single service to the Consul agent."""
        payload = self.build_service_payload(service_name, service, node_name, node)
        endpoint = f"{self.base_url}/v1/agent/service/register"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.put(endpoint, json=payload)
            return resp.status_code == 200

    def sync_node_services(
        self,
        node_name: str,
        topology: HomelabTopology,
    ) -> dict[str, bool]:
        """Synchronize all services assigned to a node with Consul."""
        if node_name not in topology.nodes:
            raise ValueError(f"Node '{node_name}' not found in topology.")

        node = topology.nodes[node_name]
        results: dict[str, bool] = {}

        for svc_name in node.services:
            svc_config = topology.services[svc_name]
            try:
                success = self.register_service(svc_name, svc_config, node_name, node)
                results[svc_name] = success
            except Exception:
                results[svc_name] = False

        return results

    def list_catalog_services(self) -> dict[str, list[str]]:
        """Query all registered services and their tags from Consul."""
        endpoint = f"{self.base_url}/v1/catalog/services"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(endpoint)
            resp.raise_for_status()
            return resp.json()
