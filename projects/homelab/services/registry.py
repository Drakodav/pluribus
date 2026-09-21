"""Registry for locating and instantiating Homelab services."""

from __future__ import annotations

import importlib
from pathlib import Path

from services.authentik.service import AuthentikService
from services.base import BaseService
from services.cockpit.service import CockpitService
from services.code.service import CodeService
from services.consul.service import ConsulService
from services.coolify.service import CoolifyService
from services.komodo.service import KomodoService
from services.netdata.service import NetdataService
from services.photos.service import PhotosService
from services.postgres.service import PgAdminService, PostgresService
from services.redis.service import RedisService


def _get_home_assistant_class() -> type[BaseService]:
    mod = importlib.import_module("services.home-assistant.service")
    return mod.HomeAssistantService  # type: ignore[no-any-return]


SERVICE_CLASSES: dict[str, type[BaseService]] = {
    "authentik": AuthentikService,
    "cockpit": CockpitService,
    "code": CodeService,
    "consul": ConsulService,
    "coolify": CoolifyService,
    "komodo": KomodoService,
    "netdata": NetdataService,
    "pgadmin": PgAdminService,
    "photos": PhotosService,
    "postgres": PostgresService,
    "redis": RedisService,
}

SERVICE_ALIASES: dict[str, str] = {
    "auth": "authentik",
    "manage": "cockpit",
    "monitor": "netdata",
    "pg-admin": "pgadmin",
    "ha": "home-assistant",
    "immich": "photos",
    "fleet": "komodo",
    "paas": "coolify",
}


def get_default_project_root() -> Path:
    """Return the root path of the projects/homelab directory."""
    return Path(__file__).resolve().parent.parent


def get_service(name: str, project_root: Path | None = None) -> BaseService:
    """Instantiate and return a service by name or alias."""
    root = project_root or get_default_project_root()
    canonical_name = SERVICE_ALIASES.get(name, name)

    if canonical_name == "home-assistant":
        service_cls = _get_home_assistant_class()
    else:
        service_cls = SERVICE_CLASSES.get(canonical_name)

    if not service_cls:
        available = sorted([*SERVICE_CLASSES.keys(), "home-assistant"])
        valid_names = ", ".join(available)
        raise ValueError(
            f"Unknown service: '{name}'. Available services: {valid_names}"
        )

    # pgadmin shares directory with postgres
    target_folder = "postgres" if canonical_name == "pgadmin" else canonical_name
    service_dir = root / "services" / target_folder
    return service_cls(service_dir)


def get_all_services(project_root: Path | None = None) -> dict[str, BaseService]:
    """Instantiate and return all registered services keyed by canonical name."""
    root = project_root or get_default_project_root()
    services: dict[str, BaseService] = {}
    for name, cls in SERVICE_CLASSES.items():
        target_folder = "postgres" if name == "pgadmin" else name
        services[name] = cls(root / "services" / target_folder)

    services["home-assistant"] = _get_home_assistant_class()(
        root / "services" / "home-assistant"
    )
    return services
