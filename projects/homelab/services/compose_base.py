"""Reusable Docker Compose service lifecycle implementation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from services.base import BaseService


class ComposeService(BaseService):
    """Standard Docker Compose-backed service implementation."""

    @property
    def compose_file(self) -> Path:
        """Return the path to this service's docker-compose.yml."""
        return self.service_dir / "docker-compose.yml"

    def up(self) -> bool:
        """Idempotently prepare environment and bring up Docker Compose stack."""
        self.pre_up()

        if not self.compose_file.exists():
            raise FileNotFoundError(
                f"Compose file not found for {self.name}: {self.compose_file}"
            )

        # Attempt to pull latest images if possible
        subprocess.run(
            ["docker", "compose", "-f", str(self.compose_file), "pull"],
            check=False,
        )

        cmd = [
            "docker",
            "compose",
            "-f",
            str(self.compose_file),
            "up",
            "-d",
        ]
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            self.post_up()
            return True
        return False

    def down(self) -> bool:
        """Gracefully stop containers."""
        if not self.compose_file.exists():
            return True

        cmd = ["docker", "compose", "-f", str(self.compose_file), "down"]
        res = subprocess.run(cmd, check=False)
        return res.returncode == 0

    def restart(self) -> bool:
        """Restart containers in the compose stack."""
        if not self.compose_file.exists():
            return False

        cmd = ["docker", "compose", "-f", str(self.compose_file), "restart"]
        res = subprocess.run(cmd, check=False)
        return res.returncode == 0

    def destroy(self) -> bool:
        """Tear down containers, remove networks, and destroy volumes."""
        if not self.compose_file.exists():
            return True

        cmd = [
            "docker",
            "compose",
            "-f",
            str(self.compose_file),
            "down",
            "-v",
            "--remove-orphans",
        ]
        res = subprocess.run(cmd, check=False)
        return res.returncode == 0

    def status(self) -> dict[str, str]:
        """Fetch running status of containers in this service stack."""
        if not self.compose_file.exists():
            return {"status": "missing_compose_file"}

        cmd = [
            "docker",
            "compose",
            "-f",
            str(self.compose_file),
            "ps",
            "--format",
            "{{.Name}}: {{.Status}}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            status_map: dict[str, str] = {}
            for line in lines:
                if ":" in line:
                    c_name, c_status = line.split(":", 1)
                    status_map[c_name.strip()] = c_status.strip()
                else:
                    status_map[line] = "running"
            return status_map if status_map else {"status": "stopped"}
        return {"status": "error", "message": res.stderr.strip()}

    def ensure_dir(
        self,
        path: Path | str,
        uid: int | None = None,
        gid: int | None = None,
    ) -> None:
        """Idempotently create storage directories and adjust permissions."""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        if uid is not None and gid is not None:
            try:
                os.chown(p, uid, gid)
            except PermissionError:
                subprocess.run(
                    ["sudo", "chown", "-R", f"{uid}:{gid}", str(p)],
                    check=False,
                )
