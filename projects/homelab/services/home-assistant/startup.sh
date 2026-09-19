#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Starting Home Assistant stack..."
cd "$BASE_DIR"

# Ensure config directory exists and has the base configuration
CONFIG_DIR="/opt/homelab/home-assistant"
ensure_dir "$CONFIG_DIR"
for file in configuration.yaml scripts.yaml scenes.yaml automations.yaml; do
    if [ ! -f "$CONFIG_DIR/$file" ]; then
        log_info "Initializing $file..."
        if [ -f "$BASE_DIR/$file" ]; then
            run_command cp "$BASE_DIR/$file" "$CONFIG_DIR/$file"
            if [ -n "${ROOT_DOMAIN:-}" ] && [ "$file" = "configuration.yaml" ]; then
                run_command sed -i "s/example.com/${ROOT_DOMAIN}/g" "$CONFIG_DIR/configuration.yaml"
            fi
        else
            run_command touch "$CONFIG_DIR/$file"
        fi
        local_user="${SUDO_USER:-$USER}"
        run_command chown "$local_user:$local_user" "$CONFIG_DIR/$file"
    fi
done

# Ensure matter directory exists
MATTER_DIR="/opt/homelab/matterjs-server"
ensure_dir "$MATTER_DIR"
run_command chmod 755 "$MATTER_DIR"

run_compose pull
run_compose up -d --remove-orphans

log_info "Registering Home Assistant in Consul..."
consul_register "macerator:home-assistant:8123" "home-assistant" 8123 \
    "traefik.http.routers.home-assistant.rule=Host(\"home-assistant.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.home-assistant.entrypoints=websecure" \
    "traefik.http.routers.home-assistant.tls.certresolver=myresolver" \
    "traefik.http.services.home-assistant.loadbalancer.server.port=8123"

# Bootstrap HACS if not already present
HACS_DIR="/opt/homelab/home-assistant/custom_components/hacs"
if [ ! -d "$HACS_DIR" ]; then
    log_info "HACS not found. Installing..."
    sleep 5
    docker_cmd="docker"
    if [ "$EUID" -ne 0 ] && ! groups 2>/dev/null | grep -q '\bdocker\b'; then
        docker_cmd="sudo docker"
    fi
    $docker_cmd exec home_assistant bash -c "wget -O - https://get.hacs.xyz | bash -" || true
    log_info "HACS installed. Restarting Home Assistant container..."
    run_compose restart
else
    log_info "HACS is already installed."
fi

log_info "Home Assistant is up."
