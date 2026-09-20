"""Unit tests for WireGuard, Consul, and SSH providers."""

from pathlib import Path

from models.topology import HomelabTopology
from providers.consul import ConsulClient
from providers.ssh import build_ssh_command
from providers.wireguard import (
    generate_gateway_wg_conf,
    generate_node_connect_script,
    generate_node_wg_conf,
)


def test_wireguard_conf_generation():
    """Ensure WireGuard configuration strings are cleanly formatted."""
    topo_path = Path(__file__).resolve().parent.parent / "topology.yaml"
    topo = HomelabTopology.load(topo_path)

    node_conf = generate_node_wg_conf(
        "macerator", topo.nodes["macerator"], topo.gateways["aperio"], topo
    )
    assert "Address = 10.10.0.2/24" in node_conf
    assert "Endpoint = 143.47.250.74:51820" in node_conf
    assert "PublicKey = pYy7pFu8OG4R3OLgKkw58RmhXxlsQwLER1OEtX2JRTM=" in node_conf

    gw_conf = generate_gateway_wg_conf("aperio", topo.gateways["aperio"], topo)
    assert "Address = 10.10.0.1/24" in gw_conf
    assert "PublicKey = 9sDaXK7HWMJCDvdwOfskPuutpS7oQXjkvoB+EJ2BnXs=" in gw_conf
    assert "AllowedIPs = 10.10.0.2/32" in gw_conf


def test_node_connect_script_generation():
    """Ensure the generated connect script is valid bash and includes keys."""
    topo_path = Path(__file__).resolve().parent.parent / "topology.yaml"
    topo = HomelabTopology.load(topo_path)

    script = generate_node_connect_script("macerator", topo)
    assert "#!/bin/bash" in script
    assert "10.10.0.2" in script
    assert "143.47.250.74" in script
    assert "systemctl restart wg-quick@wg0" in script


def test_consul_service_payload_builder():
    """Ensure Consul payload includes correct tags, address, port, and healthcheck."""
    topo_path = Path(__file__).resolve().parent.parent / "topology.yaml"
    topo = HomelabTopology.load(topo_path)

    client = ConsulClient()
    svc = topo.services["authentik"]
    node = topo.nodes["macerator"]

    payload = client.build_service_payload("authentik", svc, "macerator", node)
    assert payload["ID"] == "authentik-macerator"
    assert payload["Address"] == "10.10.0.2"
    assert payload["Port"] == 9000
    assert "exposure=public" in payload["Tags"]
    assert "Check" in payload
    assert "10.10.0.2:9000/-/health/ready/" in payload["Check"]["HTTP"]


def test_ssh_command_builder_proxyjump():
    """Ensure SSH builder configures ProxyJump through Aperio for Macerator."""
    topo_path = Path(__file__).resolve().parent.parent / "topology.yaml"
    topo = HomelabTopology.load(topo_path)

    cmd = build_ssh_command("macerator", topo)
    assert "ssh" in cmd
    assert "-J" in cmd
    assert "ubuntu@143.47.250.74" in cmd
    assert "admin@10.10.0.2" in cmd
