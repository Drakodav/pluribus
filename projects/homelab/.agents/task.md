# Homelab Task Checklist

## Phase 1: Project Setup & Context Scaffolding (Completed in PR #14)
- [x] Issue #13: Scaffold directory layout (`gateway/`, `services/`, `nodes/macerator/`, `.agents/`)
- [x] Issue #13: Author `CONTEXT.md` with domain glossary, architecture, and roadmap
- [x] Issue #13: Document ADR 0001 (Split-Brain Hybrid Cloud)
- [x] Issue #13: Document ADR 0002 (Explicit Consul Service Registration)
- [x] Issue #13: Document ADR 0003 (Centralized Secrets & CI/CD Evolution)
- [x] Issue #13: Author `.env.example` schema covering Aperio, Backbone, and Macerator
- [x] Issue #13: Create local `justfile` with standard monorepo recipes
- [x] Issue #13: Integrate with `CONTEXT-MAP.md` and `pluribus.code-workspace`

## Phase 2: Public Gateway (`aperio` - Active in Issue #15)
- [x] Issue #15: Consolidate OCI Terraform modules (`networking`, `compute`, `prod`) in `gateway/terraform/`
- [x] Issue #15: Migrate VM provisioning scripts (`docker`, `wireguard`, `platform`, `startup.sh`, `deploy.sh`) in `gateway/vm/`
- [x] Issue #15: Update `justfile` with gateway commands (`gateway-fmt`, `gateway-lint`, `gateway-validate`, `gateway-deploy`)
- [x] Issue #15: Pass automated static verification gates (Part 1)
- [x] Issue #15: Live human operator review & deployment verification (Part 2)

## Phase 3: Primary Powerhouse (`macerator` - Active in Issue #16)
- [x] Issue #16: WireGuard client backbone checks and Consul client agent in `services/consul/`
- [x] Issue #16: Core data services (PostgreSQL 16 + pgvector, Redis) in `services/postgres/` and `services/redis/`
- [x] Issue #16: Centralized identity (Authentik SSO + forwardAuth) in `services/authentik/`
- [x] Issue #16: Media, automation & observability stacks (Immich, Home Assistant, Netdata, Cockpit, code-server) in `services/`
- [x] Issue #16: Host runner, discovery firewall, and storage scaffolding under `/opt/homelab/` in `nodes/macerator/`
- [x] Issue #16: Update `justfile` with Macerator service recipes (`services-validate`, `macerator-up`, `macerator-down`, `macerator-status`, `macerator-sync`)
- [x] Issue #16: Pass automated static verification gates (Part 1)
- [ ] Issue #16: Live human operator review & synchronization verification (Part 2)

## Phase 4: Node Onboarding & Backbone Connectivity Connector (Completed in Issue #17)
- [x] Issue #17: Design & implement Node Connector CLI/script generator (`just node-connect <node>`)
- [x] Issue #17: Apply generated connector configuration on `macerator` to restore WireGuard handshake
- [x] Issue #17: Verify WireGuard backbone handshake & ICMP ping (`10.10.0.1` <-> `10.10.0.2`)
- [x] Issue #17: Verify workstation ProxyJump SSH access through Aperio bastion
- [x] Issue #17: Conclude bash-based connector milestone and transition to Phase 5 declarative architecture

## Phase 5: Python Code-as-Configuration & Type-Safe Orchestrator (Active in Issue #18)
- [x] Issue #18: Scaffold Python project tooling with Astral `uv` (`pyproject.toml`, `ruff`, `ty`, `pytest`) adhering to `.agents/rules/python.md`
- [x] Issue #18: Implement strictly typed Pydantic models with schema validation (IPs, ports, base64 keys, domains)
- [x] Issue #18: Evolve to 100% Code-as-Configuration (remove `topology.yaml`, dynamic `HomelabTopology.build()`, `homelab export-topology`)
- [x] Issue #18: Implement centralized `AppContext` singleton with host detection (`is_macerator`, `is_aperio`, `is_local_workstation`)
- [x] Issue #18: Implement modular domain providers (WireGuard mesh, Consul API discovery, Traefik routing, Docker Runner, SSH ProxyJump)
- [x] Issue #18: Enforce Docker Compose `--env-file` passing across all compose operations
- [x] Issue #18: Transition services to OOP lifecycle classes (`BaseService`, `ComposeService`, `services/registry.py`)
- [x] Issue #18: Transition node runners to Python orchestrator (`BaseNodeRunner`, `MaceratorRunner`, `AperioNode`, `nodes/registry.py`)
- [x] Issue #18: Eliminate legacy `startup.sh` bash scripts across all services and nodes
- [x] Issue #18: Configure explicit HTTP health checks across all 8 ingress services (`auth`, `code`, `consul`, `home-assistant`, `manage`, `monitor`, `pgadmin`, `photos`)
- [x] Issue #18: Add container health checks (`pg_isready`, `redis-cli ping`) with automatic Consul TCP socket fallbacks for database/cache
- [x] Issue #18: Wire `homelab service`, `homelab node`, `homelab mesh`, `homelab consul`, and `homelab export-topology` CLI commands
- [x] Issue #18: Build thin task runner interface (`justfile`) backed by `uv run homelab <cmd>`
- [x] Issue #18: Implement comprehensive unit tests (`tests/`) and pass all quality gates (`just pre-commit`: 19/19 tests, ruff, ty, validation)
- [x] Issue #18: Commit and push changes to `origin/homelab/unified` (commit `ddead72`)
- [ ] Issue #18: Verify live synchronization and orchestration on `macerator` with human operator


