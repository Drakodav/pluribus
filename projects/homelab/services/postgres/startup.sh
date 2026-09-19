#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Ensuring Postgres dependencies..."
if [ ! -f "$BASE_DIR/init-immich.sql" ]; then
    log_error "init-immich.sql not found at $BASE_DIR/init-immich.sql"
    exit 1
fi

log_info "Building and starting Postgres stack..."
cd "$BASE_DIR"
run_compose build --quiet
run_compose up -d

log_info "Registering pgAdmin in Consul..."
consul_register "macerator:pgadmin:80" "pgadmin" 80 \
    "traefik.http.routers.pgadmin.rule=Host(\"pgadmin.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.pgadmin.entrypoints=websecure" \
    "traefik.http.routers.pgadmin.tls.certresolver=myresolver" \
    "traefik.http.services.pgadmin.loadbalancer.server.port=80"

log_info "Postgres stack is up."
