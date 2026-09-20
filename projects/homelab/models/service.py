"""Service configuration and exposure policy models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ServiceConfig(BaseModel):
    """Service stack configuration and exposure routing policy."""

    role: str
    subdomain: str | None = None
    upstream_port: int = Field(ge=1, le=65535)
    exposure: Literal["public", "sso", "internal"] = "internal"
    health_path: str | None = None
