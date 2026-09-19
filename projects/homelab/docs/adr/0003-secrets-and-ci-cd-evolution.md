# ADR 0003: Secrets Management and CI/CD Deployment Evolution

* **Status**: Accepted
* **Date**: 2026-09-19
* **Context**: Homelab Infrastructure Deployment & Secrets

## Context

Managing environment variables and sensitive credentials (database passwords, Authentik encryption keys, WireGuard private keys, and OCI API keys) in a hybrid cloud monorepo presents security and operational challenges:
1. **Accidental Exposure**: Committing credentials to version control poses a major security risk.
2. **Machine Confinement**: Historically, deployments relied on running manual SSH commands (`cloud/vm/deploy.sh`, `local/startup.sh`) while physically located at a specific terminal or using a static `.env` file on disk.
3. **CI/CD Scalability**: The long-term architectural goal is to enable automated validation, updates, and deployments through GitHub Actions or central dispatch, allowing infrastructure updates from any device without requiring manual SSH access.

## Decision

We adopt a two-stage secrets and deployment strategy:

### Stage 1: Strict Local Isolation (Current Implementation)
- A comprehensive `.env.example` serves as the authoritative schema for all configuration parameters.
- Active credentials live in `projects/homelab/.env`, which is strictly excluded from version control via both root and project-level `.gitignore` files.
- Scripts source `.env` locally using non-leaking scoping patterns.

### Stage 2: Centralized Secrets & Automated CI/CD (Target Evolution)
- Infrastructure secrets and environment variables will be migrated to a centralized store (e.g. GitHub Repository/Environment Secrets or a vault solution).
- Continuous Integration / Continuous Deployment (CI/CD) pipelines will authenticate via OCI dynamic groups or short-lived credentials to provision Terraform changes automatically.
- Remote node updates on `aperio` and `macerator` will be triggered via automated GitHub Actions runners or webhook agents, deprecating manual ad-hoc SSH dependencies.

## Consequences

### Positive
- **Guaranteed Isolation Today**: Strict gitignore rules prevent credential leakage during the skeleton setup and monorepo migration.
- **Clear Schema**: The `.env.example` template documents all variables across gateway, backbone, and services in a single standardized location.
- **Architectural Readiness**: Prepares the codebase for unattended automated CI/CD deployment without requiring rewrites of service definitions.

### Negative / Trade-offs
- **Initial Manual Sync**: During Stage 1, `.env` values must be maintained manually on the development and host machines until CI/CD automation is implemented.
