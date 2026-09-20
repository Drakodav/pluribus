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

## Phase 4: Node Onboarding & Backbone Connectivity Connector (Active in Issue #17)
- [x] Issue #17: Design & implement Node Connector CLI/script generator (`just node-connect <node>`)
- [x] Issue #17: Apply generated connector configuration on `macerator` to restore WireGuard handshake
- [x] Issue #17: Verify WireGuard backbone handshake & ICMP ping (`10.10.0.1` <-> `10.10.0.2`)
- [ ] Issue #17: Verify workstation ProxyJump SSH access (`just ssh-macerator`)
- [ ] Issue #17: Synchronize consolidated Phase 3 service stacks to `macerator` (`just macerator-sync`)
- [ ] Issue #17: Run Macerator orchestrator (`just macerator-up`) and verify Consul service discovery
- [ ] Issue #17: Generalize onboarding protocol and documentation for future nodes

