#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Starting Authentik stack..."
cd "$BASE_DIR"

run_compose pull
run_compose up -d

log_info "Registering Authentik in Consul..."
consul_register "macerator:auth:9000" "auth" 9000 \
    "traefik.http.routers.auth.rule=Host(\"auth.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.auth.entrypoints=websecure" \
    "traefik.http.routers.auth.tls.certresolver=myresolver" \
    "traefik.http.services.auth.loadbalancer.server.port=9000"

log_info "Authentik is up."
