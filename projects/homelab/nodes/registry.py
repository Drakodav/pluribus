"""Registry for locating and instantiating Homelab node runners."""

from __future__ import annotations

from pathlib import Path

from nodes.base import BaseNodeRunner
from nodes.macerator.runner import MaceratorRunner

NODE_RUNNERS: dict[str, type[BaseNodeRunner]] = {
    "macerator": MaceratorRunner,
}


def get_default_project_root() -> Path:
    """Return the root path of the projects/homelab directory."""
    return Path(__file__).resolve().parent.parent


def get_node_runner(name: str, project_root: Path | None = None) -> BaseNodeRunner:
    """Instantiate and return a node runner by node name."""
    root = project_root or get_default_project_root()
    runner_cls = NODE_RUNNERS.get(name)
    if not runner_cls:
        valid_nodes = ", ".join(sorted(NODE_RUNNERS.keys()))
        raise ValueError(
            f"No runner implemented for node '{name}'. Available node runners: {valid_nodes}"
        )

    node_dir = root / "nodes" / name
    return runner_cls(node_dir=node_dir, project_root=root)
