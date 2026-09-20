"""Node and SSH connection models."""

from __future__ import annotations

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator

from models.mesh import validate_wireguard_key


class SSHConfig(BaseModel):
    """SSH connection parameters for a host."""

    user: str = "admin"
    port: int = Field(default=22, ge=1, le=65535)
    bastion: str | None = None
    identity_file: str | None = None


class GatewayNode(BaseModel):
    """Public Ingress Gateway node (e.g. Oracle Cloud Always-Free VPS)."""

    provider: str = "oci"
    role: str = "gateway"
    public_ip: IPvAnyAddress
    backbone_ip: IPvAnyAddress
    public_key: str
    ssh: SSHConfig = Field(default_factory=lambda: SSHConfig(user="ubuntu"))

    @field_validator("public_key")
    @classmethod
    def check_pubkey(cls, v: str) -> str:
        return validate_wireguard_key(v)


class ComputeNode(BaseModel):
    """Private compute/storage node (e.g. Dell Inspiron powerhouse, NAS)."""

    hardware: str | None = None
    role: str = "powerhouse"
    backbone_ip: IPvAnyAddress
    public_key: str
    ssh: SSHConfig = Field(default_factory=SSHConfig)
    services: list[str] = Field(default_factory=list)

    @field_validator("public_key")
    @classmethod
    def check_pubkey(cls, v: str) -> str:
        return validate_wireguard_key(v)
