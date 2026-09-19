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
- [ ] Issue #15: Live human operator review & deployment verification (Part 2)

## Phase 3: Primary Powerhouse (`macerator`)
- [ ] Issue #TBD: WireGuard client backbone and Consul client agent
- [ ] Issue #TBD: Core data services (PostgreSQL + pgvector, Redis)
- [ ] Issue #TBD: Centralized identity (Authentik SSO + forwardAuth)
- [ ] Issue #TBD: Media and automation stacks (Immich, Home Assistant, Netdata, Cockpit)
- [ ] Issue #TBD: Host runner and storage scaffolding under `/opt/homelab/`
