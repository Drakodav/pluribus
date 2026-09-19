#!/bin/bash
set -euo pipefail

# ==============================================================================
# Shared Utility Functions for Macerator Powerhouse Node
# Pluribus Monorepo: projects/homelab/nodes/macerator/__shared__/utils.sh
# ==============================================================================

# Determine base paths portably
__UTILS_DIR__="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$__UTILS_DIR__/../../.." && pwd)"
__IS_ENV_LOADED__="false"

# ANSI Colors for terminal logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}>>> [$(date +'%Y-%m-%dT%H:%M:%S')] INFO: $*${NC}"
}

log_warn() {
    echo -e "${YELLOW}>>> [$(date +'%Y-%m-%dT%H:%M:%S')] WARN: $*${NC}"
}

log_error() {
    echo -e "${RED}>>> [$(date +'%Y-%m-%dT%H:%M:%S')] ERROR: $*${NC}"
}

# ------------------------------------------------------------------------------
# Environment Loading
# ------------------------------------------------------------------------------
load_env() {
    local env_file="$PROJECT_ROOT/.env"

    if [[ "$__IS_ENV_LOADED__" == "true" ]]; then
        return
    fi

    if [ -f "$env_file" ]; then
        __IS_ENV_LOADED__="true"
        log_info "Loading environment from $env_file"
        set -a
        # shellcheck disable=SC1090
        . "$env_file"
        set +a

        # Normalize Latin Distiller variables with legacy fallbacks
        BACKBONE_MACERATOR_IP="${BACKBONE_MACERATOR_IP:-${BACKBONE_POWERHOUSE_IP:-10.10.0.2}}"
        BACKBONE_APERIO_IP="${BACKBONE_APERIO_IP:-${BACKBONE_GATEWAY_IP:-10.10.0.1}}"
        BACKBONE_POWERHOUSE_IP="$BACKBONE_MACERATOR_IP"
        BACKBONE_GATEWAY_IP="$BACKBONE_APERIO_IP"
        export BACKBONE_MACERATOR_IP BACKBONE_APERIO_IP BACKBONE_POWERHOUSE_IP BACKBONE_GATEWAY_IP
    else
        log_warn ".env file not found at $env_file. Proceeding with environment or defaults."
    fi
}

# ------------------------------------------------------------------------------
# System & Runtime Readiness Checks
# ------------------------------------------------------------------------------
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed."
        return 1
    fi
    local docker_cmd="docker"
    if [ "$EUID" -ne 0 ] && ! groups 2>/dev/null | grep -q '\bdocker\b'; then
        docker_cmd="sudo docker"
    fi
    if ! $docker_cmd version &> /dev/null; then
        log_error "Docker is not running or current user lacks permissions."
        return 1
    fi
    log_info "Docker is ready."
}

check_nvidia() {
    if ! command -v nvidia-container-cli &> /dev/null; then
        log_error "NVIDIA Container Toolkit is not installed (nvidia-container-cli not found)."
        return 1
    fi

    # Check for nvidia-persistenced socket required for GPU runtimes
    if [ ! -S /run/nvidia-persistenced/socket ]; then
        log_warn "NVIDIA persistenced socket not found at /run/nvidia-persistenced/socket."
        log_info "Attempting to start nvidia-persistenced service..."
        if sudo systemctl start nvidia-persistenced &> /dev/null; then
            log_info "Successfully started nvidia-persistenced."
        else
            log_error "Failed to start nvidia-persistenced. GPU-enabled containers may fail to start."
            return 1
        fi
    fi

    log_info "NVIDIA Container Toolkit is ready."
}

check_backbone() {
    if ! ip addr show wg0 &> /dev/null; then
        log_warn "WireGuard interface wg0 not found. Backbone might be down."
        return 0
    fi

    local gateway_ip="${BACKBONE_APERIO_IP:-${BACKBONE_GATEWAY_IP:-10.10.0.1}}"
    if [ -n "$gateway_ip" ]; then
        if ping -c 1 -W 2 "$gateway_ip" &> /dev/null; then
            log_info "Backbone gateway ($gateway_ip) is reachable."
        else
            log_warn "Backbone gateway ($gateway_ip) is NOT reachable."
        fi
    fi
}

# ------------------------------------------------------------------------------
# Filesystem Scaffolding
# ------------------------------------------------------------------------------
ensure_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        log_info "Creating directory: $dir"
        run_command mkdir -p "$dir"
        local real_user="${SUDO_USER:-$USER}"
        run_command chown -R "$real_user:$real_user" "$dir"
    fi
}

# ------------------------------------------------------------------------------
# Command & Compose Execution Wrappers
# ------------------------------------------------------------------------------
run_compose() {
    log_info "Running docker compose $*..."
    local env_file="$PROJECT_ROOT/.env"
    local docker_cmd="docker"
    if [ "$EUID" -ne 0 ] && ! groups 2>/dev/null | grep -q '\bdocker\b'; then
        docker_cmd="sudo docker"
    fi

    if [ -f "$env_file" ]; then
        $docker_cmd compose --env-file "$env_file" "$@"
    else
        $docker_cmd compose "$@"
    fi
}

run_command() {
    log_info "Running command: $*"
    if [ "$EUID" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

# ------------------------------------------------------------------------------
# Consul Service Discovery Helpers (ADR 0002)
# ------------------------------------------------------------------------------
consul_register() {
    local id="$1"
    local name="$2"
    local port="$3"
    shift 3

    local address="${BACKBONE_MACERATOR_IP:-${BACKBONE_POWERHOUSE_IP:-10.10.0.2}}"

    log_info "Registering service '$name' (ID: $id) on $address:$port in Consul..."
    consul_deregister "$id"

    local tag_args=()
    for tag in "$@"; do
        tag_args+=("-tag=$tag")
    done

    local docker_cmd="docker"
    if [ "$EUID" -ne 0 ] && ! groups 2>/dev/null | grep -q '\bdocker\b'; then
        docker_cmd="sudo docker"
    fi

    $docker_cmd exec consul-client consul services register \
        -id="$id" \
        -name="$name" \
        -address="$address" \
        -port="$port" \
        "${tag_args[@]}"
}

consul_deregister() {
    local id="$1"
    log_info "Deregistering service ID '$id' from Consul..."
    local docker_cmd="docker"
    if [ "$EUID" -ne 0 ] && ! groups 2>/dev/null | grep -q '\bdocker\b'; then
        docker_cmd="sudo docker"
    fi
    $docker_cmd exec consul-client consul services deregister -id="$id" &> /dev/null || true
}

# Auto-load environment on source
load_env
