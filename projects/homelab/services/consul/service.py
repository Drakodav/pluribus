"""Consul Service Discovery Client."""

from __future__ import annotations

from services.compose_base import ComposeService


class ConsulService(ComposeService):
    """Consul client agent stack."""

    name = "consul"
    role = "service-discovery"
    upstream_port = 8500
    exposure = "internal"
    health_path = "/v1/status/leader"
