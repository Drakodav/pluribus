"""Unit tests for declarative Homelab models and schema validation."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from models.topology import HomelabTopology


def test_load_production_topology():
    """Verify that the repository's topology.yaml loads cleanly and passes all checks."""
    topo_path = Path(__file__).resolve().parent.parent / "topology.yaml"
    topo = HomelabTopology.load(topo_path)

    assert topo.domain == "vlmd.cc"
    assert "aperio" in topo.gateways
    assert "macerator" in topo.nodes
    assert len(topo.services) >= 9

    aperio = topo.gateways["aperio"]
    assert str(aperio.backbone_ip) == "10.10.0.1"
    assert str(aperio.public_ip) == "143.47.250.74"

    macerator = topo.nodes["macerator"]
    assert str(macerator.backbone_ip) == "10.10.0.2"
    assert macerator.ssh.user == "admin"
    assert macerator.ssh.bastion == "aperio"


def test_invalid_wireguard_key_length():
    """Ensure that invalid key length triggers a ValidationError."""
    raw = {
        "domain": "example.com",
        "gateways": {
            "gw": {
                "public_ip": "1.2.3.4",
                "backbone_ip": "10.10.0.1",
                "public_key": "tooshort=",
            }
        },
    }
    with pytest.raises(ValidationError) as exc:
        HomelabTopology.model_validate(raw)
    assert "WireGuard public key must be exactly 44 characters" in str(exc.value)


def test_backbone_ip_collision():
    """Ensure that two nodes sharing the same backbone IP fails validation."""
    raw = {
        "domain": "example.com",
        "gateways": {
            "gw": {
                "public_ip": "1.2.3.4",
                "backbone_ip": "10.10.0.1",
                "public_key": "pYy7pFu8OG4R3OLgKkw58RmhXxlsQwLER1OEtX2JRTM=",
            }
        },
        "nodes": {
            "node1": {
                "backbone_ip": "10.10.0.1",  # Collision!
                "public_key": "9sDaXK7HWMJCDvdwOfskPuutpS7oQXjkvoB+EJ2BnXs=",
            }
        },
    }
    with pytest.raises(ValidationError) as exc:
        HomelabTopology.model_validate(raw)
    assert "Backbone IP collision" in str(exc.value)


def test_undeclared_service_reference():
    """Ensure that assigning an undeclared service to a node raises validation error."""
    raw = {
        "domain": "example.com",
        "gateways": {
            "gw": {
                "public_ip": "1.2.3.4",
                "backbone_ip": "10.10.0.1",
                "public_key": "pYy7pFu8OG4R3OLgKkw58RmhXxlsQwLER1OEtX2JRTM=",
            }
        },
        "nodes": {
            "node1": {
                "backbone_ip": "10.10.0.2",
                "public_key": "9sDaXK7HWMJCDvdwOfskPuutpS7oQXjkvoB+EJ2BnXs=",
                "services": ["non_existent_service"],
            }
        },
    }
    with pytest.raises(ValidationError) as exc:
        HomelabTopology.model_validate(raw)
    assert "references undeclared service" in str(exc.value)
