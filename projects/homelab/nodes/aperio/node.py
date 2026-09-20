"""Aperio public gateway node definition and orchestrator."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from nodes.base import BaseNodeRunner
from services.base import BaseService


class AperioNode(BaseNodeRunner):
    """Aperio Oracle Cloud Always-Free public ingress gateway."""

    name = "aperio"
    role = "gateway"
    provider = "oci"
    ssh_bastion = None

    @property
    def ssh_user(self) -> str:
        """SSH user for Aperio gateway."""
        from context import AppContext

        return AppContext().get_required_env("NODE_APERIO_SSH_USER")

    @property
    def ssh_port(self) -> int:
        """SSH port for Aperio gateway."""
        from context import AppContext

        return int(AppContext().get_required_env("NODE_APERIO_SSH_PORT"))

    @property
    def public_ip(self) -> str:
        """Public IPv4 address assigned to the gateway."""
        from context import AppContext

        return AppContext().get_required_env("NODE_APERIO_PUBLIC_IP")

    @property
    def backbone_ip(self) -> str:
        """WireGuard backbone mesh IP for Aperio."""
        from context import AppContext

        return AppContext().backbone_aperio_ip

    @property
    def public_key(self) -> str:
        """WireGuard public key for Aperio."""
        from context import AppContext

        return AppContext().get_required_env("NODE_APERIO_PUBLIC_KEY")

    @property
    def platform_compose(self) -> Path:
        """Return the path to Aperio platform stack docker-compose.yml."""
        return self.node_dir / "vm" / "platform" / "docker-compose.yml"

    def setup_host(self) -> bool:
        """Idempotently prepare Aperio host, WireGuard backbone, firewall, and ACME storage."""
        from context import AppContext
        from providers.wireguard import generate_gateway_wg_conf

        ctx = AppContext()
        use_sudo = not ctx.runtime.is_root
        sudo_prefix = ["sudo"] if use_sudo else []

        # 1. Base storage directories
        storage_dir = Path("/opt/homelab")
        if not storage_dir.exists():
            subprocess.run([*sudo_prefix, "mkdir", "-p", str(storage_dir)], check=False)

        # 2. Let's Encrypt storage preparation
        letsencrypt_dir = self.platform_compose.parent / "letsencrypt"
        acme_file = letsencrypt_dir / "acme.json"
        try:
            letsencrypt_dir.mkdir(parents=True, exist_ok=True)
            acme_file.touch(mode=0o600, exist_ok=True)
            acme_file.chmod(0o600)
        except PermissionError:
            subprocess.run(
                [*sudo_prefix, "mkdir", "-p", str(letsencrypt_dir)], check=False
            )
            subprocess.run([*sudo_prefix, "touch", str(acme_file)], check=False)
            subprocess.run([*sudo_prefix, "chmod", "600", str(acme_file)], check=False)

        # 3. WireGuard Directory & Keys
        wg_dir = Path("/etc/wireguard")
        if not wg_dir.exists():
            subprocess.run([*sudo_prefix, "mkdir", "-p", str(wg_dir)], check=False)
            subprocess.run([*sudo_prefix, "chmod", "700", str(wg_dir)], check=False)

        privkey_file = wg_dir / "privatekey"
        pubkey_file = wg_dir / "publickey"

        privkey = ""
        if privkey_file.exists():
            try:
                privkey = privkey_file.read_text(encoding="utf-8").strip()
            except PermissionError:
                res = subprocess.run(
                    [*sudo_prefix, "cat", str(privkey_file)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode == 0:
                    privkey = res.stdout.strip()

        if not privkey:
            try:
                priv_proc = subprocess.run(
                    ["wg", "genkey"], capture_output=True, text=True, check=True
                )
                privkey = priv_proc.stdout.strip()
                pub_proc = subprocess.run(
                    ["wg", "pubkey"],
                    input=privkey,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                pubkey = pub_proc.stdout.strip()

                subprocess.run(
                    [
                        *sudo_prefix,
                        "sh",
                        "-c",
                        f"echo '{privkey}' > {privkey_file} && chmod 600 {privkey_file} && echo '{pubkey}' > {pubkey_file}",
                    ],
                    check=False,
                )
            except Exception:
                pass

        # 4. Generate & Write /etc/wireguard/wg0.conf
        topology = ctx.topology
        if "aperio" in topology.gateways:
            gw_node = topology.gateways["aperio"]
            wg_conf_content = generate_gateway_wg_conf(
                gateway_name="aperio",
                gateway=gw_node,
                topology=topology,
                private_key_placeholder=privkey or "$PRIVATE_KEY",
            )
            conf_file = wg_dir / "wg0.conf"
            subprocess.run(
                [
                    *sudo_prefix,
                    "sh",
                    "-c",
                    f"cat <<'EOF' > {conf_file}\n{wg_conf_content}\nEOF\nchmod 600 {conf_file}",
                ],
                check=False,
            )

        # 5. OCI Firewall (iptables rules at index 1 to bypass default REJECT)
        firewall_rules = [
            ["-p", "udp", "--dport", "51820"],
            ["-p", "tcp", "--dport", "80"],
            ["-p", "tcp", "--dport", "443"],
            ["-i", "wg0"],
        ]
        for rule in firewall_rules:
            check_cmd = [*sudo_prefix, "iptables", "-C", "INPUT", *rule, "-j", "ACCEPT"]
            res = subprocess.run(check_cmd, capture_output=True, check=False)
            if res.returncode != 0:
                insert_cmd = [
                    *sudo_prefix,
                    "iptables",
                    "-I",
                    "INPUT",
                    "1",
                    *rule,
                    "-j",
                    "ACCEPT",
                ]
                subprocess.run(insert_cmd, check=False)

        # 6. Enable IP Forwarding
        subprocess.run(
            [*sudo_prefix, "sysctl", "-w", "net.ipv4.ip_forward=1"], check=False
        )

        # 7. Start / Restart wg-quick@wg0 service
        subprocess.run(
            [*sudo_prefix, "systemctl", "enable", "wg-quick@wg0"], check=False
        )
        subprocess.run(
            [*sudo_prefix, "systemctl", "restart", "wg-quick@wg0"], check=False
        )

        return True

    def get_services(self) -> list[BaseService]:
        """Aperio platform services are deployed as an integrated gateway stack."""
        return []

    def up(self, service_name: str | None = None) -> dict[str, bool]:
        """Deploy or synchronize Aperio gateway platform compose stack."""
        if not self.platform_compose.exists():
            return {"aperio-platform": False}

        from context import AppContext
        from providers.docker import build_docker_compose_cmd

        ctx = AppContext()

        # Ensure acme.json exists with 600 permissions
        letsencrypt_dir = self.platform_compose.parent / "letsencrypt"
        acme_file = letsencrypt_dir / "acme.json"
        try:
            letsencrypt_dir.mkdir(parents=True, exist_ok=True)
            acme_file.touch(mode=0o600, exist_ok=True)
            acme_file.chmod(0o600)
        except PermissionError:
            use_sudo = not ctx.runtime.is_root
            sudo_prefix = ["sudo"] if use_sudo else []
            subprocess.run(
                [*sudo_prefix, "mkdir", "-p", str(letsencrypt_dir)], check=False
            )
            subprocess.run([*sudo_prefix, "touch", str(acme_file)], check=False)
            subprocess.run([*sudo_prefix, "chmod", "600", str(acme_file)], check=False)

        # Pull latest images
        pull_cmd = build_docker_compose_cmd(
            self.platform_compose, "pull", env_file=ctx.env_file
        )
        subprocess.run(pull_cmd, check=False)

        # Launch platform stack
        up_cmd = build_docker_compose_cmd(
            self.platform_compose, "up", "-d", env_file=ctx.env_file
        )
        res = subprocess.run(up_cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def down(self, service_name: str | None = None) -> dict[str, bool]:
        """Stop Aperio gateway platform compose stack."""
        if not self.platform_compose.exists():
            return {"aperio-platform": True}

        from context import AppContext
        from providers.docker import build_docker_compose_cmd

        ctx = AppContext()
        cmd = build_docker_compose_cmd(
            self.platform_compose, "down", env_file=ctx.env_file
        )
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def restart(self, service_name: str | None = None) -> dict[str, bool]:
        """Restart Aperio gateway platform compose stack."""
        if not self.platform_compose.exists():
            return {"aperio-platform": False}

        from context import AppContext
        from providers.docker import build_docker_compose_cmd

        ctx = AppContext()
        cmd = build_docker_compose_cmd(
            self.platform_compose, "restart", env_file=ctx.env_file
        )
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def destroy(self, service_name: str | None = None) -> dict[str, bool]:
        """Tear down Aperio gateway platform compose stack."""
        if not self.platform_compose.exists():
            return {"aperio-platform": True}

        from context import AppContext
        from providers.docker import build_docker_compose_cmd

        ctx = AppContext()
        cmd = build_docker_compose_cmd(
            self.platform_compose,
            "down",
            "-v",
            "--remove-orphans",
            env_file=ctx.env_file,
        )
        res = subprocess.run(cmd, check=False)
        return {"aperio-platform": res.returncode == 0}

    def status(self, service_name: str | None = None) -> dict[str, Any]:
        """Query status of Aperio platform stack."""
        if not self.platform_compose.exists():
            return {"aperio-platform": "missing_compose_file"}

        from context import AppContext
        from providers.docker import build_docker_compose_cmd

        ctx = AppContext()
        cmd = build_docker_compose_cmd(
            self.platform_compose,
            "ps",
            "--format",
            "{{.Name}}: {{.Status}}",
            env_file=ctx.env_file,
        )
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            return {"aperio-platform": lines if lines else "stopped"}
        return {"aperio-platform": "error"}
