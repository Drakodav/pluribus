#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Starting Netdata monitoring service..."

if ! check_nvidia; then
    log_warn "NVIDIA check failed. Netdata will start without GPU monitoring."
fi

cd "$BASE_DIR"
run_compose pull
run_compose up -d

log_info "Registering Netdata in Consul..."
consul_register "macerator:monitor:19999" "monitor" 19999 \
    "traefik.http.routers.monitor.rule=Host(\"monitor.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.monitor.entrypoints=websecure" \
    "traefik.http.routers.monitor.tls.certresolver=myresolver" \
    "traefik.http.services.monitor.loadbalancer.server.port=19999" \
    "traefik.http.routers.monitor.middlewares=auth-traefik@docker"

log_info "Netdata is up."
