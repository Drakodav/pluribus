#!/bin/bash
set -euo pipefail

# ==============================================================================
# Macerator Powerhouse Node Master Orchestrator
# Pluribus Monorepo: projects/homelab/nodes/macerator/startup.sh
# ==============================================================================

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
SHARED_UTILS="$BASE_DIR/__shared__/utils.sh"

if [ -f "$SHARED_UTILS" ]; then
    # shellcheck source=nodes/macerator/__shared__/utils.sh
    source "$SHARED_UTILS"
else
    echo "Error: Shared utilities not found at $SHARED_UTILS"
    exit 1
fi

echo "=========================================="
echo " Macerator Powerhouse Startup Sequence"
echo "=========================================="

# 1. Global Prerequisites
load_env
check_docker
check_backbone

# 2. Host Networking & Discovery Firewall Configuration
log_info "Checking current iptables FORWARD policy..."
if command -v iptables &> /dev/null; then
    CURRENT_FORWARD_POLICY=$(sudo iptables -L FORWARD -v -n --line-numbers 2>/dev/null | grep "Chain FORWARD (policy" | awk '{print $NF}' | sed 's/)//' || true)

    if [ "$CURRENT_FORWARD_POLICY" = "DROP" ]; then
        log_warn "Current iptables FORWARD policy is DROP. Setting to ACCEPT for Docker host networking."
        sudo iptables -P FORWARD ACCEPT
    else
        log_info "Current iptables FORWARD policy is ${CURRENT_FORWARD_POLICY:-ACCEPT}."
    fi

    # Open mDNS (5353 UDP) and SSDP (1900 UDP) for local device discovery
    log_info "Ensuring iptables rules for mDNS (5353) and SSDP (1900)..."
    if ! sudo iptables -C INPUT -p udp --dport 5353 -j ACCEPT &> /dev/null; then
        sudo iptables -A INPUT -p udp --dport 5353 -j ACCEPT
    fi
    if ! sudo iptables -C OUTPUT -p udp --dport 5353 -j ACCEPT &> /dev/null; then
        sudo iptables -A OUTPUT -p udp --dport 5353 -j ACCEPT
    fi
    if ! sudo iptables -C INPUT -p udp --dport 1900 -j ACCEPT &> /dev/null; then
        sudo iptables -A INPUT -p udp --dport 1900 -j ACCEPT
    fi
    if ! sudo iptables -C OUTPUT -p udp --dport 1900 -j ACCEPT &> /dev/null; then
        sudo iptables -A OUTPUT -p udp --dport 1900 -j ACCEPT
    fi
fi

# 3. Storage Scaffolding
log_info "Ensuring persistent storage scaffolding under /opt/homelab/..."
ensure_dir "/opt/homelab"
ensure_dir "/opt/homelab/postgres"
ensure_dir "/opt/homelab/pgadmin"
ensure_dir "/opt/homelab/authentik/media"
ensure_dir "/opt/homelab/authentik/custom-templates"
ensure_dir "/opt/homelab/authentik/certs"
ensure_dir "/opt/homelab/immich/library"
ensure_dir "/opt/homelab/immich/db"
ensure_dir "/opt/homelab/netdata"
ensure_dir "/opt/homelab/home-assistant"
ensure_dir "/opt/homelab/matterjs-server"

# Set strict permissions for PostgreSQL (UID 70 on Alpine) and pgAdmin (UID 5050)
if [ -d "/opt/homelab/postgres" ]; then
    run_command chown -R 70:70 "/opt/homelab/postgres" 2>/dev/null || true
fi
if [ -d "/opt/homelab/pgadmin" ]; then
    run_command chown -R 5050:5050 "/opt/homelab/pgadmin" 2>/dev/null || true
fi

# 4. Service Orchestration
# Ordered by dependency: mesh -> caches -> databases -> identity -> applications
SERVICES=("consul" "redis" "postgres" "authentik" "photos" "cockpit" "home-assistant" "netdata" "code")

# Targeted single service execution
if [ -n "${1:-}" ]; then
    TARGET_SERVICE="$1"
    if [ "$TARGET_SERVICE" = "ha" ]; then
        TARGET_SERVICE="home-assistant"
    fi

    VALID_SERVICE=false
    for S in "${SERVICES[@]}"; do
        if [ "$S" = "$TARGET_SERVICE" ]; then
            VALID_SERVICE=true
            break
        fi
    done

    if [ "$VALID_SERVICE" = true ]; then
        SERVICES=("$TARGET_SERVICE")
        log_info "Targeting single service: $TARGET_SERVICE"
    else
        log_error "Service '$TARGET_SERVICE' is not recognized."
        echo "Valid services are: ${SERVICES[*]}"
        exit 1
    fi
fi

for SERVICE in "${SERVICES[@]}"; do
    SERVICE_DIR="$PROJECT_ROOT/services/$SERVICE"
    SERVICE_SCRIPT="$SERVICE_DIR/startup.sh"

    if [ -d "$SERVICE_DIR" ]; then
        echo "------------------------------------------"
        echo " Starting Service: $SERVICE"
        echo "------------------------------------------"

        if [ -f "$SERVICE_SCRIPT" ]; then
            chmod +x "$SERVICE_SCRIPT"
            bash "$SERVICE_SCRIPT"
        else
            log_warn "Service $SERVICE has no startup.sh. Bringing up compose directly..."
            cd "$SERVICE_DIR"
            run_compose pull
            run_compose up -d
        fi
    else
        log_error "Service directory $SERVICE_DIR not found."
    fi
done

echo "=========================================="
echo " Macerator Powerhouse Services are Up"
echo "=========================================="
