# ADR 0002: Explicit Consul Catalog Service Registration

* **Status**: Accepted
* **Date**: 2026-09-19
* **Context**: Homelab Service Discovery & Routing

## Context

In our initial iterations of the split-brain architecture, automated container discovery tools (such as Gliderlabs Registrator) were evaluated to listen to Docker daemon events and register running containers into HashiCorp Consul automatically.

However, automated bridge registration surfaced multiple friction points:
1. **Routing Tag Overload**: Traefik relies on Consul catalog tags to construct router rules, middleware attachments (such as Authentik forwardAuth), entrypoints, and load balancer settings. Automated tools either cluttered Consul with every internal container port or required cumbersome Docker labels.
2. **Maintenance & Abandonment**: Registrator is unmaintained and experiences compatibility issues with modern Docker API versions.
3. **Loss of Determinism**: Containers restarting unexpectedly could desynchronize catalog entries or create duplicate registrations under transient IPs.

## Decision

We replace automated Docker-to-Consul bridge tools with **Explicit Service Registration** managed directly via shell orchestration utilities (`local/__shared__/utils.sh` / node startup hooks):

1. **Local Consul Client Agent**: A lightweight Consul client container runs on `macerator` and communicates over the WireGuard backbone with the Consul server on `aperio`.
2. **Controlled Registration (`consul_register`)**: Each service stack's `startup.sh` script explicitly invokes the `consul_register` utility function upon successful container boot.
3. **Explicit Traefik Tags**: Routing rules, TLS resolver directives, and forwardAuth middleware declarations are declared directly as tags passed into the Consul service catalog registration command:
   ```bash
   consul_register "immich" "photos" 2283 \
       "traefik.enable=true" \
       "traefik.http.routers.photos.rule=Host(\`photos.${ROOT_DOMAIN}\`)" \
       "traefik.http.routers.photos.entrypoints=websecure" \
       "traefik.http.routers.photos.tls.certresolver=myresolver"
   ```

## Consequences

### Positive
- **Deterministic Control**: Only explicitly declared services and ports are published to Traefik.
- **Direct Middleware Assignment**: ForwardAuth middleware (Authentik) and domain rules are clearly auditable in code.
- **Zero Third-Party Daemon Overhead**: Eliminates unstable container event listeners.
- **Clean Deregistration**: Services can be deregistered cleanly during maintenance or shutdown without stale catalog traces.

### Negative / Trade-offs
- **Manual Declaration**: Adding a new public-facing service requires declaring its Consul tags in its `startup.sh` script rather than relying purely on Docker container labels.
