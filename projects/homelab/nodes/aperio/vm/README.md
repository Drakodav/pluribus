# Aperio Gateway Architecture

This directory contains the platform configuration for the public gateway node (`aperio`).

Lifecycle and provisioning are managed natively in pure Python by `AperioNode` (`nodes/aperio/node.py`) and orchestrated via the unified Homelab CLI.

## Structure

- **`platform/docker-compose.yml`**: Docker Compose definition for the core gateway platform stack:
  - **Traefik**: Ingress reverse proxy with automatic Let's Encrypt SSL, Consul service catalog discovery provider, and Authentik ForwardAuth middleware.
  - **Consul Server**: Ingress service discovery server bound to the WireGuard backbone (`10.10.0.1:8500`).

## Lifecycle Management

### From Workstation
All operations can be dispatched directly using `just cli`:

```bash
# 1. Synchronize repository to Aperio
just cli node sync aperio

# 2. Provision host (WireGuard, iptables, storage permissions)
just cli node run aperio setup

# 3. Deploy platform services (Traefik + Consul Server)
just cli node run aperio up

# 4. Check platform status
just cli node run aperio status
```

### On Aperio Directly
When logged into the node:

```bash
# Provision host networking and permissions
just cli host setup

# Bring up platform stack
just cli host up

# Check status
just cli host status
```
