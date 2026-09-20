"""WireGuard mesh and network models."""

from __future__ import annotations

import base64

from pydantic import BaseModel, Field


def validate_wireguard_key(key: str) -> str:
    """Validate that a string is a 44-character base64-encoded WireGuard key."""
    key = key.strip()
    if len(key) != 44:
        raise ValueError(
            f"WireGuard public key must be exactly 44 characters (received {len(key)})"
        )
    try:
        decoded = base64.b64decode(key)
        if len(decoded) != 32:
            raise ValueError(
                f"Decoded WireGuard key must be 32 bytes (got {len(decoded)})"
            )
    except Exception as exc:
        raise ValueError(f"Invalid base64 encoding for WireGuard key: {exc}") from exc
    return key


class MeshConfig(BaseModel):
    """WireGuard encrypted backbone overlay network settings."""

    subnet: str = "10.10.0.0/24"
    port: int = Field(default=51820, ge=1, le=65535)
    keepalive: int = Field(default=25, ge=5, le=300)
    mtu: int = Field(default=1420, ge=1280, le=1500)
    dns: list[str] = Field(default_factory=lambda: ["1.1.1.1"])
