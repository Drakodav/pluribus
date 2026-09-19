#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

PRIMARY_USER="${SUDO_USER:-$USER}"

log_info "Ensuring code-server is installed..."
if ! command -v code-server &> /dev/null; then
    curl -fsSL https://code-server.dev/install.sh | sh
fi

log_info "Ensuring code-server user directories..."
mkdir -p "$HOME/.config"
mkdir -p "$HOME/.local"

log_info "Restarting code-server service for user $PRIMARY_USER..."
sudo systemctl restart "code-server@${PRIMARY_USER}.service" 2>/dev/null || true

log_info "Registering code-server in Consul..."
consul_register "macerator:code:4010" "code" 4010 \
    "traefik.enable=true" \
    "traefik.http.routers.code.rule=Host(\"code.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.code.entrypoints=websecure" \
    "traefik.http.routers.code.tls.certresolver=myresolver" \
    "traefik.http.services.code.loadbalancer.server.port=4010" \
    "traefik.http.routers.code.middlewares=auth-code@docker"

log_info "code-server is ready at https://code.${ROOT_DOMAIN}"
