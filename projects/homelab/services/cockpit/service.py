"""Cockpit host management service lifecycle implementation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from services.base import BaseService


class CockpitService(BaseService):
    """Cockpit native host systemd service."""

    name = "cockpit"
    role = "management"
    upstream_port = 9090
    exposure = "sso"
    subdomain = "cockpit"

    def pre_up(self) -> None:
        """Configure PAM and systemd override for no-TLS backend."""
        # Ensure PAM configuration is standard Ubuntu/Debian
        pam_file = Path("/etc/pam.d/cockpit")
        if pam_file.parent.exists():
            pam_content = (
                "#%PAM-1.0\n"
                "@include common-auth\n"
                "@include common-account\n"
                "@include common-password\n"
                "@include common-session\n"
            )
            try:
                pam_file.write_text(pam_content)
            except PermissionError:
                subprocess.run(
                    [
                        "sudo",
                        "bash",
                        "-c",
                        f"cat <<'EOF' > /etc/pam.d/cockpit\n{pam_content}EOF",
                    ],
                    check=False,
                )

        # Systemd Override for non-TLS backend behind Traefik reverse proxy
        override_dir = Path("/etc/systemd/system/cockpit.service.d")
        override_file = override_dir / "no-tls.conf"
        override_content = (
            "[Service]\nExecStart=\nExecStart=/usr/lib/cockpit/cockpit-tls --no-tls\n"
        )
        try:
            override_dir.mkdir(parents=True, exist_ok=True)
            override_file.write_text(override_content)
        except PermissionError:
            subprocess.run(["sudo", "mkdir", "-p", str(override_dir)], check=False)
            subprocess.run(
                [
                    "sudo",
                    "bash",
                    "-c",
                    f"cat <<'EOF' > {override_file}\n{override_content}EOF",
                ],
                check=False,
            )

        # Cockpit WebService Configuration
        cockpit_dir = Path("/etc/cockpit")
        cockpit_conf = cockpit_dir / "cockpit.conf"
        root_domain = os.environ.get("ROOT_DOMAIN", "vlmd.cc")
        conf_content = (
            "[WebService]\n"
            f"Origins = https://manage.{root_domain} https://cockpit.{root_domain} wss://manage.{root_domain} wss://cockpit.{root_domain} http://localhost:9090\n"
            "ProtocolHeader = X-Forwarded-Proto\n"
            "AllowUnsecureLogin = true\n"
            "AllowUnencrypted = true\n"
        )
        try:
            cockpit_dir.mkdir(parents=True, exist_ok=True)
            cockpit_conf.write_text(conf_content)
        except PermissionError:
            subprocess.run(["sudo", "mkdir", "-p", str(cockpit_dir)], check=False)
            subprocess.run(
                [
                    "sudo",
                    "bash",
                    "-c",
                    f"cat <<'EOF' > {cockpit_conf}\n{conf_content}EOF",
                ],
                check=False,
            )
            subprocess.run(
                ["sudo", "chmod", "-R", "a+rX", str(cockpit_dir)], check=False
            )

    def up(self) -> bool:
        """Idempotently configure and start Cockpit systemd service."""
        self.pre_up()
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=False)
        subprocess.run(
            [
                "sudo",
                "systemctl",
                "start",
                "cockpit-wsinstance-http.socket",
                "cockpit-wsinstance-https-factory.socket",
            ],
            check=False,
        )
        subprocess.run(["sudo", "systemctl", "enable", "cockpit.socket"], check=False)
        res1 = subprocess.run(
            ["sudo", "systemctl", "restart", "cockpit.socket"], check=False
        )
        res2 = subprocess.run(["sudo", "systemctl", "restart", "cockpit"], check=False)
        success = res1.returncode == 0 and res2.returncode == 0
        if success:
            self.post_up()
        return success

    def down(self) -> bool:
        """Stop Cockpit service and socket."""
        res = subprocess.run(
            ["sudo", "systemctl", "stop", "cockpit", "cockpit.socket"], check=False
        )
        return res.returncode == 0

    def restart(self) -> bool:
        """Restart Cockpit service."""
        return self.up()

    def destroy(self) -> bool:
        """Stop Cockpit and disable socket."""
        subprocess.run(["sudo", "systemctl", "disable", "cockpit.socket"], check=False)
        res = subprocess.run(
            ["sudo", "systemctl", "stop", "cockpit", "cockpit.socket"], check=False
        )
        return res.returncode == 0

    def status(self) -> dict[str, str]:
        """Check systemd status of cockpit."""
        res = subprocess.run(
            ["systemctl", "is-active", "cockpit"],
            capture_output=True,
            text=True,
            check=False,
        )
        return {"cockpit": res.stdout.strip() if res.returncode == 0 else "inactive"}
