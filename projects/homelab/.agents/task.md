# Homelab Task Checklist

## Phase 1: Project Setup & Context Scaffolding (Active)
- [x] Issue #13: Scaffold directory layout (`gateway/`, `services/`, `nodes/macerator/`, `.agents/`)
- [x] Issue #13: Author `CONTEXT.md` with domain glossary, architecture, and roadmap
- [x] Issue #13: Document ADR 0001 (Split-Brain Hybrid Cloud)
- [x] Issue #13: Document ADR 0002 (Explicit Consul Service Registration)
- [x] Issue #13: Document ADR 0003 (Centralized Secrets & CI/CD Evolution)
- [x] Issue #13: Author `.env.example` schema covering Aperio, Backbone, and Macerator
- [x] Issue #13: Create local `justfile` with standard monorepo recipes
- [x] Issue #13: Integrate with `CONTEXT-MAP.md` and `pluribus.code-workspace`
- [ ] Issue #13: Run verification gates and obtain user review for commit/merge

## Phase 2: Public Gateway (`aperio`)
- [ ] Issue #TBD: OCI Terraform IaC refactor (VCN, compute, security rules)
- [ ] Issue #TBD: Aperio VM ingress provisioning (WireGuard server, Traefik, Consul server)
- [ ] Issue #TBD: Automated remote deployment runner

## Phase 3: Primary Powerhouse (`macerator`)
- [ ] Issue #TBD: WireGuard client backbone and Consul client agent
- [ ] Issue #TBD: Core data services (PostgreSQL + pgvector, Redis)
- [ ] Issue #TBD: Centralized identity (Authentik SSO + forwardAuth)
- [ ] Issue #TBD: Media and automation stacks (Immich, Home Assistant, Netdata, Cockpit)
- [ ] Issue #TBD: Host runner and storage scaffolding under `/opt/homelab/`
