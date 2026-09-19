#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Starting Immich (Photos) stack..."
cd "$BASE_DIR"

if ! check_nvidia; then
    log_warn "NVIDIA check failed. Machine learning container may fail if CUDA driver is missing."
fi

run_compose pull
run_compose up -d

log_info "Registering Immich in Consul..."
consul_register "macerator:photos:2283" "photos" 2283 \
    "traefik.http.routers.photos.rule=Host(\"photos.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.photos.entrypoints=websecure" \
    "traefik.http.routers.photos.tls.certresolver=myresolver" \
    "traefik.http.services.photos.loadbalancer.server.port=2283"

log_info "Immich is up."
