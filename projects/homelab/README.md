# Homelab: Split-Brain Hybrid Cloud & Declarative Orchestration Engine

A private, self-hosted cloud infrastructure platform engineered for privacy, data sovereignty, and zero ongoing cloud compute cost. 

This project implements a **Split-Brain Hybrid Cloud** pattern that pairs a cloud edge gateway on Oracle Cloud Infrastructure (OCI) with a high-capacity, on-premises bare-metal compute powerhouse, connected over an encrypted WireGuard mesh and orchestrated by a strongly typed Python configuration engine.

---

## 1. Architectural Overview

```
                          ┌──────────────────────────────────────────────┐
                          │             Public Edge Gateway              │
                          │                  ("aperio")                  │
                          │         Oracle Cloud Always-Free VM          │
                          │   Public IP: Let's Encrypt TLS Termination   │
                          │  - Traefik: Dynamic Ingress Edge Router      │
                          │  - Consul Server: Discovery Catalog Cluster  │
                          │  - WireGuard Hub: Mesh Overlay Endpoint      │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                         Encrypted Backbone
                                    WireGuard (10.10.0.0/24)
                                                 │
                          ┌──────────────────────┴───────────────────────┐
                          │              Compute Powerhouse              │
                          │                ("macerator")                 │
                          │            Bare-Metal Dell i9 / 32GB         │
                          │  - PostgreSQL 16 + pgvector (Custom Alpine)  │
                          │  - Redis (Shared Persistent Cache)           │
                          │  - Authentik (Central Identity Provider)     │
                          │  - Immich (Photo & Video ML Storage Stack)   │
                          │  - Home Assistant Core & Matter Server       │
                          │  - Netdata, Cockpit, code-server, pgAdmin    │
                          │  - Consul Client Agent                       │
                          │  - Unified Storage Root: /opt/homelab/       │
                          └──────────────────────────────────────────────┘
```

### The Problem It Solves
1. **Cloud Compute Costs**: Running high-RAM, GPU/ML workloads (photo indexing, computer vision, vector databases) in commercial clouds incurs heavy monthly recurring costs.
2. **Home Network Security**: Exposing home servers directly via residential dynamic DNS and router port forwarding risks IP disclosure, DDoS vulnerability, and ISP port blocking.
3. **Configuration Sprawl**: Traditional self-hosted setups often devolve into brittle bash scripts, conflicting reverse proxy configurations, and unversioned runtime secrets.

### The Solution
- **Zero Cloud Spend**: Infrastructure is strictly constrained to the Oracle Cloud "Always Free" tier for public ingress, while all compute-heavy workloads run locally on bare-metal hardware.
- **Total Network Isolation**: No ports are ever forwarded on the home router. The powerhouse initiates an outbound-only, persistent WireGuard mesh connection to the cloud gateway.
- **Code-as-Configuration**: The entire cluster topology, service definitions, environment variables, and node lifecycles are modeled as strongly typed Python classes with Pydantic V2 validation.

---

## 2. Machine Profiles & Nomenclature

Following a botanical distillery naming theme (*Ex Pluribus Unum*), nodes are partitioned by responsibility:

### `aperio` (The Public Gateway)
- **Etymology**: From Latin *aperire* ("to open", root of *aperitif*).
- **Environment**: Oracle Cloud Infrastructure (OCI) Always-Free VM (`Ubuntu 24.04 LTS`).
- **Internal IP**: `10.10.0.1`
- **Role**: Edge ingress, automated Let's Encrypt SSL/TLS certificates, WireGuard mesh hub, and Consul Server leader.
- **Provisioning**: Managed via modular Terraform IaC in [`nodes/aperio/terraform/`](nodes/aperio/terraform/).

### `macerator` (The Local Powerhouse)
- **Etymology**: From Latin *maceratio* (the steeping/extraction of botanical essence).
- **Environment**: Bare-metal Dell Inspiron i9, 32GB RAM, local NVMe/SSD storage.
- **Internal IP**: `10.10.0.2`
- **Role**: Heavy data storage, machine learning, vector embeddings, relational databases, home automation, and internal developer workspaces.
- **Orchestration**: Managed via Python node runner in [`nodes/macerator/runner.py`](nodes/macerator/runner.py).

### The Backbone Mesh
- **Subnet**: `10.10.0.0/24` (WireGuard interface `wg0`).
- **Function**: Secure overlay network enabling direct, peer-to-peer TCP/UDP communication between `aperio` and `macerator` as if they were co-located on the same physical switch.

---

## 3. Ingress & Authentication Routing Architecture

Traffic enters `aperio` on ports 80/443, where Traefik dynamically routes requests to the appropriate service running on `macerator` using tags populated by the **Consul Catalog**.

### The Authentication Boundary: Native OIDC vs. ForwardAuth SSO

A key architectural insight in this homelab is the strict separation between services requiring **Public Ingress** versus those requiring **ForwardAuth SSO**:

1. **Native OAuth2 / OpenID Connect (`exposure = "public"`)**:
   - Services such as **Immich**, **Home Assistant**, and **pgAdmin** have first-class multi-user authentication, native mobile companion apps, or background synchronization APIs.
   - Placing a Traefik ForwardAuth proxy in front of these services breaks mobile sync, intercepts WebSocket connections, and results in `404 Not Found (Powered by authentik)` errors because Authentik treats them as OIDC applications, not Outpost proxies.
   - These services route directly through Traefik with TLS termination, delegating authentication natively to Authentik via standard OIDC authorization flows.

2. **ForwardAuth SSO (`exposure = "sso"`)**:
   - Services like **Cockpit**, **Netdata**, **code-server**, **Consul UI**, and **Traefik Dashboard** lack robust native multi-user access control.
   - Traefik intercepts unauthenticated requests to these subdomains and delegates authentication to Authentik's ForwardAuth Outpost before allowing traffic to proceed.

### Ingress Routing Matrix

| Subdomain | Target Service | Port | Health Check Path | Exposure | Auth Strategy |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `auth.vlmd.cc` | Authentik Server | `9000` | `/-/health/ready/` | `public` | Native Authentik Web UI / IdP |
| `photos.vlmd.cc` | Immich Web & API | `2283` | `/api/server/ping` | `public` | Native Authentik OAuth2 (Web + Mobile App) |
| `home-assistant.vlmd.cc` | Home Assistant Core | `8123` | `/manifest.json` | `public` | Native OpenID Connect (Web + Mobile App) |
| `pgadmin.vlmd.cc` | pgAdmin 4 Web | `80` | `/misc/ping` | `public` | Native Authentik OAuth2 (`ProxyFix` enabled) |
| `code.vlmd.cc` | code-server (VS Code) | `8443` | `/healthz` | `sso` | Traefik ForwardAuth (`auth-code`) |
| `manage.vlmd.cc` | Cockpit Host Admin | `9090` | `/ping` | `sso` | Traefik ForwardAuth (`auth-cockpit`) |
| `monitor.vlmd.cc` | Netdata Telemetry | `19999`| `/api/v1/info` | `sso` | Traefik ForwardAuth (`auth-traefik`) |
| `consul.vlmd.cc` | Consul Web UI | `8500` | `/v1/status/leader`| `sso` | Traefik ForwardAuth (`auth-traefik`) |
| `traefik.vlmd.cc` | Traefik Dashboard | `8080` | `/ping` | `sso` | Traefik ForwardAuth (`auth-traefik`) |
| *Internal Only* | Shared PostgreSQL | `5432` | TCP `pg_isready` | `internal`| Internal cluster network (`shared_postgres`) |
| *Internal Only* | Shared Redis | `6379` | TCP `redis-cli ping`| `internal`| Internal cluster network (`shared_redis`) |

---

## 4. Python Declarative Orchestration Engine

Instead of disjointed shell scripts, the homelab is driven by a type-safe Python package located in [`projects/homelab/`](.):

```
projects/homelab/
├── cli/                        # Typer CLI subcommands (node, service, mesh, consul, host)
│   ├── main.py                 # Main CLI entrypoint (uv run homelab)
│   ├── node.py                 # Remote node orchestration (ssh, sync, deploy, copy-id)
│   └── service.py              # Individual service lifecycle dispatchers
├── context.py                  # AppContext singleton (host detection, env resolution)
├── models/                     # Pydantic V2 declarative schema models
│   ├── mesh.py                 # WireGuard mesh topologies and peer configs
│   ├── node.py                 # Node hardware, SSH, and bastion models
│   ├── service.py              # Service ports, exposure policies, and health models
│   └── topology.py             # Root HomelabTopology declarative engine
├── nodes/                      # Symmetrical node implementations
│   ├── aperio/                 # Gateway Terraform configs and VM platform compose
│   └── macerator/              # Powerhouse service runner and host bootstrap
├── providers/                  # Transport, discovery, and runtime adapters
│   ├── consul.py               # Consul HTTP API registration and health client
│   ├── docker.py               # Compose runner with automatic sudo detection
│   ├── ssh.py                  # SSH and Rsync with automatic bastion ProxyJump
│   └── wireguard.py            # Dynamic wg0 configuration renderer
├── services/                   # Modular service stacks (each with isolated compose)
│   ├── authentik/              # Authentik Server & Worker
│   ├── base.py                 # BaseService abstract lifecycle class
│   ├── cockpit/                # Native systemd Cockpit host manager
│   ├── code/                   # code-server native systemd integration
│   ├── compose_base.py         # ComposeService Docker Compose lifecycle adapter
│   ├── consul/                 # Consul client agent
│   ├── home-assistant/         # Home Assistant & MatterJS stack
│   ├── netdata/                # Netdata monitoring container
│   ├── photos/                 # Immich server & machine learning
│   ├── postgres/               # PostgreSQL 16 + pgvector Dockerfile & pgAdmin
│   ├── redis/                  # Shared Redis cache
│   └── registry.py             # Central service factory and alias resolution
└── tests/                      # Comprehensive pytest test suite (33 passing tests)
```

### Core Engine Design Principles
- **Strict OOP Service Lifecycle**: Every service subclassing `BaseService` or `ComposeService` implements standard lifecycle methods:
  - `pre_up()`: Idempotently prepares host directories, permissions, and initial SQL scripts.
  - `up()`: Builds custom images and brings up containers with project-scoped `--env-file`.
  - `post_up()`: Registers the service in the Consul catalog with Traefik routing tags and health checks.
  - `status()`: Queries live container health states.
  - `down()` / `post_down()`: Stops containers and deregisters tags from Consul.
- **AppContext Singleton**: Thread-safe runtime introspection (`context.py`) dynamically detects if the code is executing on `macerator`, `aperio`, or a local workstation, resolving paths and secrets cleanly.
- **SSH Multiplexing**: Sockets configured with `ControlMaster=auto`, `ControlPersist=10m`, and `ControlPath=~/.ssh/cm-%C` enable instant, multiplexed execution and rsync syncs without repeated password prompts.

---

## 5. Storage Architecture & Directory Layout

All persistent application data on `macerator` is strictly centralized under `/opt/homelab/` with deterministic Unix user/group ownership to prevent permission collisions:

```
/opt/homelab/
├── authentik/
│   ├── certs/                 # TLS certificates for Authentik services
│   ├── custom-templates/      # Branded authentication templates
│   └── media/                 # Avatars and user media
├── home-assistant/            # Configuration files, sqlite db, and custom components
├── immich/
│   └── library/               # Primary photo and video media repository
├── matterjs-server/           # Matter integration state (UID 1000:1000)
├── netdata/                   # Netdata telemetry database and cache
├── pgadmin/                   # pgAdmin 4 SQLite configuration database (UID 5050:5050)
└── postgres/                  # PostgreSQL 16 database cluster (UID 70:70)
```

---

## 6. Operational Quickstart & Command Reference

The repository provides a uniform `just` command interface:

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (Python package installer and execution engine)
- [just](https://github.com/casey/just) (Command runner)
- [Docker Engine & Compose Plugin](https://docs.docker.com/engine/)

### Essential Commands

#### 1. Pre-Commit Quality Gate
Runs code formatting, ruff linting, ty type checking, pytest unit tests, and validates all Docker Compose stacks:
```bash
just pre-commit
```

#### 2. Declarative Topology Validation
Validates topology models, schema constraints, and all Compose YAML files:
```bash
just validate
```

#### 3. Deploying a Remote Node
Orchestrates an end-to-end sync, host directory preparation, image building, container boot, and health verification:
```bash
just cli node deploy macerator
```

#### 4. Authorizing SSH Keys
Distributes your local workstation SSH public key through the Aperio bastion to enable passwordless deployments:
```bash
just cli node copy-id macerator
```

#### 5. Managing Individual Services
Lifecycle management for any registered service:
```bash
# Query status of all macerator services
just cli node status macerator

# Restart a specific service (e.g., pgadmin or immich)
just cli service restart pgadmin

# Build custom container images (e.g. Postgres with pgvector)
just cli service build postgres
```

#### 6. Exporting Runtime Topology
Dumps the dynamically computed Python cluster topology to YAML:
```bash
just cli export-topology
```

---

## 7. Custom Container Builds: PostgreSQL 16 + pgvector

The database stack ([`services/postgres/Dockerfile`](services/postgres/Dockerfile)) builds the `pgvector` extension directly from source on an Alpine Linux base with LLVM JIT compilation safely disabled (`with_llvm=no`) to avoid toolchain bloat and DNS build timeouts:

```dockerfile
FROM postgres:16-alpine
RUN apk add --no-cache --virtual .build-deps git build-base clang19 llvm19 ... \
    && cd /tmp && git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git \
    && cd pgvector && make with_llvm=no OPTFLAGS="" && make with_llvm=no install \
    && apk del .build-deps && rm -rf /tmp/pgvector
```

Extension verification query:
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
-- vector | 0.7.4 | public | vector data type and ivfflat and hnsw access methods
```

---

## 8. License & Privacy

This project is maintained inside the **Pluribus** monorepo under the terms of the repository's root [LICENSE](../../LICENSE). No private credentials, tokens, or encryption keys are committed to version control.
