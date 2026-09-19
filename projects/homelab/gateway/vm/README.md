# Aperio Gateway VM Provisioning

This directory contains the provisioning and runtime configuration for the public gateway VM (`aperio`). It is designed to be **idempotent**, **modular**, and **replayable**.

## Structure

- **`startup.sh`**: The master entrypoint executed on `aperio`. It runs services sequentially in dependency order (`docker` → `wireguard` → `platform`).
- **`deploy.sh`**: The local operator deployment script. Synchronizes this directory and `projects/homelab/.env` to the remote VM via `rsync` over SSH and executes `startup.sh`.
- **`docker/`**: Idempotent installation of Docker Engine and the Docker Compose plugin.
- **`wireguard/`**: WireGuard server endpoint setup (`wg0` on `10.10.0.1/24`), iptables/UFW firewall rules, and IP forwarding.
- **`platform/`**: Traefik reverse proxy (Let's Encrypt SSL, Consul Catalog discovery provider, Authentik ForwardAuth middleware) and HashiCorp Consul Server.

## How to Deploy to Aperio

From `projects/homelab/` (or using `just gateway-deploy`):

```bash
sudo ./gateway/vm/deploy.sh [SSH_USER] [SSH_HOST] [SSH_KEY_PATH]
```

Defaults (inferred from `projects/homelab/.env`):
- User: `ubuntu`
- Host: `GATEWAY_PUBLIC_IP`
- Key: `~/.ssh/id_rsa`

## Adding a New Gateway Component

1. Create a new directory inside `gateway/vm/` (e.g. `gateway/vm/fail2ban/`).
2. Add an idempotent `startup.sh` script inside that folder.
3. Append the service name to the `SERVICES` array in `gateway/vm/startup.sh`.
