"""Code-server host service lifecycle implementation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from services.base import BaseService


class CodeService(BaseService):
    """Code-server native host systemd service."""

    name = "code"
    consul_name = "code"
    role = "development"
    upstream_port = 8443
    exposure = "sso"
    subdomain = "code"
    auth_middleware = "auth-code@docker"
    health_path = "/healthz"

    def _get_primary_user(self) -> str:
        from context import AppContext

        ctx = AppContext()
        return ctx.runtime.user or "ubuntu"

    def pre_up(self) -> None:
        """Ensure code-server is installed, configured for SSO on upstream_port, and user directories exist."""
        if not shutil.which("code-server"):
            # Install code-server if missing
            subprocess.run(
                "curl -fsSL https://code-server.dev/install.sh | sh",
                shell=True,
                check=False,
            )

        user = self._get_primary_user()
        user_home = Path(f"/home/{user}") if user != "root" else Path("/root")
        config_dir = user_home / ".config" / "code-server"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.yaml"
        config_content = (
            f"bind-addr: 0.0.0.0:{self.upstream_port}\nauth: none\ncert: false\n"
        )
        try:
            config_file.write_text(config_content)
        except PermissionError:
            subprocess.run(
                [
                    "sudo",
                    "bash",
                    "-c",
                    f"cat <<'EOF' > {config_file}\n{config_content}EOF",
                ],
                check=False,
            )
        subprocess.run(
            ["sudo", "chown", "-R", f"{user}:{user}", str(user_home / ".config")],
            check=False,
        )
        (user_home / ".local").mkdir(parents=True, exist_ok=True)

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
        if res.returncode == 0:
            self.post_down()
            return True
        return False

    def restart(self) -> bool:
        """Restart code-server service."""
        return self.up()

    def destroy(self) -> bool:
        """Stop and disable code-server service."""
        user = self._get_primary_user()
        service_name = f"code-server@{user}.service"
        subprocess.run(["sudo", "systemctl", "disable", service_name], check=False)
        res = subprocess.run(["sudo", "systemctl", "stop", service_name], check=False)
        if res.returncode == 0:
            self.post_down()
            return True
        return False

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
