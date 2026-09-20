"""Consul Service Discovery client."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import httpx

from models.node import ComputeNode
from models.service import ServiceConfig
from models.topology import HomelabTopology

if TYPE_CHECKING:
    from services.base import BaseService

logger = logging.getLogger(__name__)


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

        # Mandatory Health Check: HTTP if path declared, TCP socket check otherwise
        if service.health_path:
            payload["Check"] = {
                "HTTP": f"http://{node.backbone_ip}:{service.upstream_port}{service.health_path}",
                "Interval": "15s",
                "Timeout": "3s",
                "DeregisterCriticalServiceAfter": "10m",
            }
        else:
            payload["Check"] = {
                "TCP": f"{node.backbone_ip}:{service.upstream_port}",
                "Interval": "15s",
                "Timeout": "3s",
                "DeregisterCriticalServiceAfter": "10m",
            }

        return payload

    def build_service_payload_from_object(
        self,
        service: BaseService,
        node_name: str,
        backbone_ip: str,
        domain: str,
    ) -> dict[str, Any]:
        """Construct registration payload directly from a BaseService instance."""
        tags = [
            f"exposure={service.exposure}",
            f"node={node_name}",
            f"role={service.role}",
            "managed-by=homelab-engine",
        ]
        if service.subdomain:
            tags.append(f"subdomain={service.subdomain}")

        # Inject Traefik router, entrypoint, TLS, and middleware tags
        traefik_tags = service.get_traefik_tags(domain)
        tags.extend(traefik_tags)

        payload: dict[str, Any] = {
            "ID": f"{service.registered_name}-{node_name}",
            "Name": service.registered_name,
            "Tags": tags,
            "Address": backbone_ip,
            "Port": service.upstream_port,
            "Meta": {
                "node": node_name,
                "role": service.role,
                "exposure": service.exposure,
            },
        }

        # Mandatory Health Check: HTTP endpoint check or fallback TCP socket check
        if service.health_path:
            payload["Check"] = {
                "HTTP": f"http://{backbone_ip}:{service.upstream_port}{service.health_path}",
                "Interval": "15s",
                "Timeout": "3s",
                "DeregisterCriticalServiceAfter": "10m",
            }
        else:
            payload["Check"] = {
                "TCP": f"{backbone_ip}:{service.upstream_port}",
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
        """Register a single service configuration to the Consul agent."""
        payload = self.build_service_payload(service_name, service, node_name, node)
        endpoint = f"{self.base_url}/v1/agent/service/register"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.put(endpoint, json=payload)
                return resp.status_code == 200
        except httpx.RequestError as exc:
            logger.warning("Failed to connect to Consul agent at %s: %s", endpoint, exc)
            return False

    def register_service_object(
        self,
        service: BaseService,
        node_name: str,
        backbone_ip: str,
        domain: str,
    ) -> bool:
        """Register a concrete BaseService instance with Traefik tags and health check."""
        payload = self.build_service_payload_from_object(
            service, node_name, backbone_ip, domain
        )
        endpoint = f"{self.base_url}/v1/agent/service/register"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.put(endpoint, json=payload)
                return resp.status_code == 200
        except httpx.RequestError as exc:
            logger.warning(
                "Failed to register %s in Consul at %s: %s", service.name, endpoint, exc
            )
            return False

    def deregister_service(self, service_id: str) -> bool:
        """Deregister a service from the Consul agent by service ID."""
        endpoint = f"{self.base_url}/v1/agent/service/deregister/{service_id}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.put(endpoint)
                return resp.status_code == 200
        except httpx.RequestError as exc:
            logger.warning(
                "Failed to deregister %s from Consul at %s: %s",
                service_id,
                endpoint,
                exc,
            )
            return False

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
