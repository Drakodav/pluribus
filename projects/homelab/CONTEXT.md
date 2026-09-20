---
name: homelab
alias: homelab
description: Split-brain hybrid cloud infrastructure combining an Oracle Cloud VPS gateway (aperio) with an on-premises powerhouse compute/storage node (macerator).
stack: terraform docker bash wireguard consul traefik
---

# Homelab (De-Google Split-Brain Hybrid Cloud)

A private, self-hosted infrastructure platform engineered for privacy, data sovereignty, and zero cloud computing cost. The architecture implements a **Split-Brain Hybrid Cloud** pattern separating public ingress routing from on-premises heavy compute and persistent storage.

```
                      ┌─────────────────────────────────────────┐
                      │             Public Gateway              │
                      │               ("aperio")                │
                      │      Oracle Cloud Always-Free VPS       │
                      │  - Traefik (HTTPS, SSL, Edge Router)    │
                      │  - Consul Server (Catalog Discovery)    │
                      │  - WireGuard Hub Endpoint               │
                      └────────────────────┬────────────────────┘
                                           │
                                   Encrypted Backbone
                                 (WireGuard 10.10.0.0/24)
                                           │
                      ┌────────────────────┴────────────────────┐
                      │            Primary Powerhouse           │
                      │              ("macerator")              │
                      │            i9 / 32GB RAM                │
                      │  - PostgreSQL + pgvector (Custom Alpine)│
                      │  - Redis (Shared Cache)                 │
                      │  - Authentik (SSO & Forward Auth)       │
                      │  - Immich (Photo & Video ML Stack)      │
                      │  - Home Assistant / Netdata / Cockpit   │
                      │  - Consul Client Agent                  │
                      │  - Unified Storage Root: /opt/homelab/  │
                      └─────────────────────────────────────────┘
```

---

## Language & Glossary (Latin Distiller Theme)

**aperio**:
The public edge gateway node hosted on an Oracle Cloud "Always Free" VPS (`10.10.0.1`). Originating from Latin _aperire_ ("to open", the root of _aperitif_), it opens the connection from the public internet, terminates SSL/TLS via Let's Encrypt, and routes requests across the WireGuard tunnel.
_Avoid_: cloud node, vps, proxy server.

**macerator**:
The primary on-premises powerhouse node (`10.10.0.10`) running on bare-metal hardware (Dell Inspiron i9, 32GB RAM) in the local home environment. Named after the botanical steeping process (_maceratio_), it handles heavy extraction, relational databases, vector calculations, and bulk persistent media storage.
_Avoid_: local laptop, server, powerhouse box.

**Backbone**:
The private, persistent WireGuard encrypted overlay network (`10.10.0.0/24`) connecting `aperio` and `macerator` into a single secure local subnet, eliminating the need to expose private home ports or dynamic DNS directly to the public internet.
_Avoid_: VPN tunnel, connection, intranet.

**Consul Catalog Registration**:
The explicit mechanism by which local services on `macerator` declare their presence to Traefik on `aperio`. Services are registered with tags defining routing rules and middleware using the Consul HTTP API/CLI via local startup hooks.
_Avoid_: automated registrator, service mesh.

**Unified Storage Convention**:
The standardized root directory (`/opt/homelab/`) on `macerator` housing all persistent databases, configuration files, and photo media libraries (e.g. `/opt/homelab/immich/`, `/opt/homelab/postgres/`).
_Avoid_: app data, docker volumes root, storage path.

**Modular Startup Pattern**:
The orchestration convention where every service stack maintains an isolated directory containing its `docker-compose.yml` and self-contained `startup.sh`, which can be booted independently or orchestrated sequentially by node runners.
_Avoid_: monolithic compose, master script.

**Forward Auth**:
The security boundary implemented on `aperio` where Traefik delegates incoming requests for internal dashboards (Consul UI, Cockpit, pgAdmin) to Authentik running on `macerator` before allowing traffic through.
_Avoid_: basic auth, gateway security.

---

## Architecture Principles

1. **Decoupled Machine Topologies**:
   - `gateway/`: Contains all cloud-native IaC (Terraform) and gateway VM deployment scripts.
   - `services/`: Houses portable, modular Docker Compose stacks agnostic of host hardware.
   - `nodes/`: Houses bare-metal host runners (starting with `nodes/macerator/`) for storage mounting, GPU hooks, firewall policies, and designated service boots.
2. **Zero Cloud Infrastructure Cost**: Strictly constrained to Oracle Cloud's "Always Free" tier.
3. **Data Sovereignty**: High-capacity data (photos, databases, home telemetry) never leaves physical local storage.
4. **Resilient Portability**: New nodes (e.g. future satellite laptops or low-power servers) can be added to `nodes/` and connected to the Backbone without altering existing service definitions.

---

## Project Roadmap & Checklist

### Phase 1: Skeleton & Context Distillation (Current)

- [x] Issue #13: Establish decoupled directory structure (`gateway/`, `services/`, `nodes/macerator/`)
- [x] Issue #13: Document domain glossary and Latin Distiller machine naming in `CONTEXT.md`
- [x] Issue #13: Record architectural decisions (`docs/adr/0001`, `0002`, `0003`)
- [x] Issue #13: Define comprehensive `.env.example` schema covering Gateway, Backbone, and Services
- [x] Issue #13: Wire project into Pluribus monorepo (`CONTEXT-MAP.md`, `pluribus.code-workspace`, local `justfile`)

### Phase 2: Public Gateway (`aperio` - Issue #15)

- [x] OCI Terraform Infrastructure: Clean, modular VCN, compute, and security lists
- [x] Idempotent VM Provisioning: Automated installation of Docker, WireGuard server, Traefik, and Consul server
- [x] Ingress & SSL: Traefik dynamic routing and Let's Encrypt automated certificate management
- [x] Remote Deployment: Streamlined `deploy.sh` script to sync and apply gateway configuration

### Phase 3: Core Powerhouse (`macerator` - Issue #16)

- [x] WireGuard client endpoint checks and local Consul client agent connectivity (`services/consul/`)
- [x] Shared data foundation: PostgreSQL (custom Alpine + pgvector) and Redis (`services/postgres/`, `services/redis/`)
- [x] Centralized identity: Authentik SSO and Traefik forwardAuth middleware (`services/authentik/`)
- [x] Media & Applications: Immich photo management stack, Home Assistant, Netdata, Cockpit, code-server (`services/`)
- [x] Storage scaffolding, discovery firewalls, and orchestrator under `/opt/homelab/` (`nodes/macerator/`)

### Phase 4: Node Onboarding & Backbone Connectivity Connector (Issue #17)

- [ ] Automated Node Connector CLI & script generator (`just node-connect <node>`)
- [ ] WireGuard handshake restoration on `macerator` (`10.10.0.1` <-> `10.10.0.2`)
- [ ] Live cross-node reachability and workstation ProxyJump SSH verification
- [ ] Service stack synchronization to `macerator` and live container orchestration
- [ ] Repeatable onboarding runbook for future nodes

