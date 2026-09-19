# ADR 0001: Split-Brain Hybrid Cloud Architecture

* **Status**: Accepted
* **Date**: 2026-09-19
* **Context**: Homelab Infrastructure

## Context

Self-hosting modern applications (such as high-resolution photo libraries with machine learning, home automation, and media streaming) creates competing architectural requirements:
1. **Public Availability**: Services need to be accessible outside the home (e.g. mobile photo sync, dashboards) with valid SSL/TLS certificates and static DNS routing.
2. **Compute & Storage Demands**: Storing hundreds of gigabytes of media and running deep learning inference (Immich facial recognition/clip search) requires substantial RAM and CPU/GPU resources that are prohibitively expensive on public cloud instances.
3. **Data Sovereignty & Cost**: Commercial cloud compute and egress costs scale linearly with storage volume. Commercial cloud storage also relinquishes data custody.
4. **Residential Network Constraints**: Standard residential ISPs often employ dynamic IP allocation, carrier-grade NAT (CGNAT), and firewall policies that make hosting public servers on home routers unreliable or insecure.

## Decision

We adopt a **Split-Brain Hybrid Cloud** pattern across two primary operational zones:

1. **Public Gateway (`aperio`)**:
   - Hosted on an Oracle Cloud Infrastructure (OCI) "Always Free" VM.
   - Operates as the public ingress boundary with a static IPv4 address and DNS records.
   - Handles Let's Encrypt automated SSL/TLS termination and edge routing via Traefik.
   - Runs a HashiCorp Consul catalog discovery server.
2. **Primary Powerhouse (`macerator`)**:
   - Hosted on on-premises bare-metal hardware (Dell Inspiron i9, 32GB RAM) located on the home local area network.
   - Houses persistent storage mounted under `/opt/homelab/` and executes resource-intensive workloads (PostgreSQL with `pgvector`, Redis, Authentik, Immich).
3. **Encrypted Backbone**:
   - A persistent point-to-point WireGuard tunnel (`10.10.0.0/24`) links `aperio` (`10.10.0.1`) and `macerator` (`10.10.0.10`).
   - No public ports are opened on the residential router. All inbound public traffic terminates at `aperio` and is routed internally across the encrypted WireGuard backbone to `macerator`.

## Consequences

### Positive
- **Zero Cloud Infrastructure Cost**: Fully leverages Oracle's Always Free tier for cloud components.
- **Data Custody**: High-capacity photos, databases, and media reside physically on local hardware.
- **Residential Ingress Security**: No port forwarding or exposed home IP addresses; residential NAT is traversed transparently via WireGuard outbound handshakes.
- **High Performance**: Local LAN access to Immich and storage operates at full gigabit/NVMe speeds without internet bandwidth throttling.

### Negative / Trade-offs
- **Backbone Dependency**: If the WireGuard backbone drops, public ingress to local services is interrupted (though local LAN access continues uninterrupted).
- **Two-Node Operational Overhead**: Requires managing configurations across both the cloud VM and the local node.
