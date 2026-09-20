# Macerator Powerhouse Node Orchestration

This directory contains the host bootstrap, shared utilities, and service orchestration runner for the on-premises powerhouse node (**`macerator`** - Dell Inspiron i9).

## Architecture & Responsibilities

- **Host Environment**: Bare-metal Linux running Docker Engine, NVIDIA Container Toolkit, and WireGuard client (`wg0` on `10.10.0.2/24`).
- **Encrypted Backbone**: Connects to the public gateway (`aperio` on `10.10.0.1`) over WireGuard.
- **Service Mesh**: Joins the Aperio Consul cluster via the local `consul-client` agent.
- **Persistent Storage**: All bulk persistent application data is mapped to `/opt/homelab/`.
- **Unified Runner**: `startup.sh` enforces dependencies, validates prerequisites, configures discovery firewalls, initializes storage paths, and boots services.

## Directory Layout

- **`startup.sh`**: Master host runner. Runs all services or a targeted single service.
- **`__shared__/utils.sh`**: Common library for logging, `.env` loading, Docker wrappers, and Consul catalog registration.

## Usage

### Run all services in dependency order:
```bash
./startup.sh
```

### Run a specific service:
```bash
./startup.sh postgres
./startup.sh photos
./startup.sh home-assistant
```

### From Project Root via Just:
```bash
just macerator-up
just macerator-up postgres
```
