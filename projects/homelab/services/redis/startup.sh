#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Ensuring Redis host prerequisites..."
if command -v sysctl &> /dev/null; then
    if [ "$(sysctl -n vm.overcommit_memory 2>/dev/null || echo 0)" != "1" ]; then
        log_info "Setting vm.overcommit_memory to 1..."
        sudo sysctl -w vm.overcommit_memory=1 || true

        if [ -f /etc/sysctl.conf ] && ! grep -q "^vm.overcommit_memory.*=.*1" /etc/sysctl.conf; then
            log_info "Persisting vm.overcommit_memory=1 in /etc/sysctl.conf..."
            echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf > /dev/null || true
        fi
    fi
fi

log_info "Starting Redis stack..."
cd "$BASE_DIR"
run_compose pull
run_compose up -d

log_info "Redis is up."
