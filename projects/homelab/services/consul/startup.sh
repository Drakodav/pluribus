#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Starting Consul Client..."
cd "$BASE_DIR"

run_compose pull
run_compose up -d

log_info "Verifying Consul connection..."
sleep 5
docker_cmd="docker"
if [ "$EUID" -ne 0 ] && ! groups 2>/dev/null | grep -q '\bdocker\b'; then
    docker_cmd="sudo docker"
fi

if $docker_cmd exec consul-client consul members 2>/dev/null | grep -q "alive"; then
    log_info "Consul cluster joined successfully."
else
    log_warn "Consul cluster not joined yet. Check backbone WireGuard connectivity."
fi
