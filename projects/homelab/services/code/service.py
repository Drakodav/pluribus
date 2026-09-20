"""Code-server host service lifecycle implementation."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from services.base import BaseService


class CodeService(BaseService):
    """Code-server native host systemd service."""

    name = "code"
    role = "development"
    upstream_port = 8443
    exposure = "sso"
    subdomain = "code"

    def _get_primary_user(self) -> str:
        return os.environ.get("SUDO_USER") or os.environ.get("USER", "ubuntu")

    def pre_up(self) -> None:
        """Ensure code-server is installed and user directories exist."""
        if not shutil.which("code-server"):
            # Install code-server if missing
            subprocess.run(
                "curl -fsSL https://code-server.dev/install.sh | sh",
                shell=True,
                check=False,
            )

        home = Path.home()
        (home / ".config").mkdir(parents=True, exist_ok=True)
        (home / ".local").mkdir(parents=True, exist_ok=True)

    def up(self) -> bool:
        """Idempotently install, configure, and start code-server."""
        self.pre_up()
        user = self._get_primary_user()
        service_name = f"code-server@{user}.service"
        subprocess.run(["sudo", "systemctl", "enable", service_name], check=False)
        res = subprocess.run(
            ["sudo", "systemctl", "restart", service_name], check=False
        )
        success = res.returncode == 0
        if success:
            self.post_up()
        return success

    def down(self) -> bool:
        """Stop code-server service."""
        user = self._get_primary_user()
        service_name = f"code-server@{user}.service"
        res = subprocess.run(["sudo", "systemctl", "stop", service_name], check=False)
        return res.returncode == 0

    def restart(self) -> bool:
        """Restart code-server service."""
        return self.up()

    def destroy(self) -> bool:
        """Stop and disable code-server service."""
        user = self._get_primary_user()
        service_name = f"code-server@{user}.service"
        subprocess.run(["sudo", "systemctl", "disable", service_name], check=False)
        res = subprocess.run(["sudo", "systemctl", "stop", service_name], check=False)
        return res.returncode == 0

    def status(self) -> dict[str, str]:
        """Check systemd status of code-server."""
        user = self._get_primary_user()
        service_name = f"code-server@{user}.service"
        res = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
            check=False,
        )
        return {service_name: res.stdout.strip() if res.returncode == 0 else "inactive"}
