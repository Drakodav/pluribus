"""Consul Service Discovery Client."""

from __future__ import annotations

from services.compose_base import ComposeService


class ConsulService(ComposeService):
    """Consul client agent stack."""

    name = "consul"
    consul_name = "consul"
    role = "service-discovery"
    subdomain = "consul"
    upstream_port = 8500
    exposure = "sso"
    auth_middleware = "auth-traefik@docker"
    health_path = "/v1/status/leader"
