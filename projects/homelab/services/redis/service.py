"""Redis cache service stack."""

from __future__ import annotations

from services.compose_base import ComposeService


class RedisService(ComposeService):
    """Redis high-performance in-memory cache."""

    name = "redis"
    role = "cache"
    upstream_port = 6379
    exposure = "internal"
