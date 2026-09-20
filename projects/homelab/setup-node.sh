#!/usr/bin/env bash
# ==============================================================================
# Pluribus Homelab: Universal Node Baseline Provisioning Script
# ==============================================================================
# Supports: Ubuntu / Debian (x86_64, aarch64 / ARM64)
# Targets: Aperio (OCI Gateway), Macerator (Powerhouse), or any fresh homelab node.
# Idempotently installs:
#   - Core system utilities (curl, wget, git, rsync, jq, htop, etc.)
#   - WireGuard mesh tools (wireguard, wireguard-tools, ufw, iptables)
#   - Python 3 environment (python3, pip, venv)
#   - uv (system-wide modern Python package and project manager)
#   - just (command runner interface)
#   - Docker Engine & Docker Compose plugin (with non-root user access)
#   - /opt/homelab storage base
# ==============================================================================

set -euo pipefail

# ANSI color codes
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

log_info() {
    echo -e "${BLUE}${BOLD}>>> [INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}${BOLD}✓ [OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}${BOLD}! [WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}${BOLD}✗ [ERROR]${NC} $1"
}

echo -e "${BOLD}======================================================${NC}"
echo -e "${BOLD} Pluribus Homelab: Universal Node Provisioning${NC}"
echo -e "${BOLD}======================================================${NC}"

# 1. Privilege check & Target User Resolution
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be executed with root privileges."
    echo "Please run: sudo bash $0"
    exit 1
fi

TARGET_USER="${SUDO_USER:-$USER}"
if [ "$TARGET_USER" = "root" ]; then
    # Fallback heuristic: check for standard ubuntu or admin users
    if id "ubuntu" &>/dev/null; then
        TARGET_USER="ubuntu"
    elif id "admin" &>/dev/null; then
        TARGET_USER="admin"
    fi
fi
log_info "Target non-root user resolved to: ${BOLD}${TARGET_USER}${NC}"

# 2. Architecture & OS Verification
ARCH="$(uname -m)"
log_info "Detected Architecture: ${BOLD}${ARCH}${NC}"

if [ ! -f /etc/os-release ]; then
    log_error "Unsupported OS. /etc/os-release not found."
    exit 1
fi

# shellcheck disable=SC1091
. /etc/os-release
OS_ID="${ID:-unknown}"
OS_VERSION_CODENAME="${VERSION_CODENAME:-${UBUNTU_CODENAME:-unknown}}"
log_info "Detected OS: ${BOLD}${PRETTY_NAME:-$OS_ID}${NC} (${OS_VERSION_CODENAME})"

if [[ "$OS_ID" != "ubuntu" && "$OS_ID" != "debian" ]]; then
    log_warn "This script is optimized for Ubuntu/Debian. Proceeding anyway..."
fi

export DEBIAN_FRONTEND=noninteractive

# 3. Base System Utilities
log_info "Updating apt package index..."
apt-get update -y

log_info "Installing core system utilities and WireGuard tools..."
apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    rsync \
    jq \
    htop \
    tar \
    gzip \
    unzip \
    software-properties-common \
    lsb-release \
    gnupg \
    net-tools \
    ufw \
    iptables \
    wireguard \
    wireguard-tools \
    build-essential \
    python3 \
    python3-pip \
    python3-venv

log_success "Base system utilities installed."

# 4. Install uv (Python tool manager) system-wide
if command -v uv &>/dev/null; then
    log_success "uv already installed: $(uv --version)"
else
    log_info "Installing uv system-wide to /usr/local/bin..."
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
    chmod +x /usr/local/bin/uv /usr/local/bin/uvx 2>/dev/null || true
    if command -v uv &>/dev/null; then
        log_success "uv installed successfully: $(uv --version)"
    else
        log_error "Failed to verify uv installation."
        exit 1
    fi
fi

# 5. Install just (Command runner) system-wide
if command -v just &>/dev/null; then
    log_success "just already installed: $(just --version)"
else
    log_info "Installing just system-wide to /usr/local/bin..."
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
    chmod +x /usr/local/bin/just 2>/dev/null || true
    if command -v just &>/dev/null; then
        log_success "just installed successfully: $(just --version)"
    else
        log_error "Failed to verify just installation."
        exit 1
    fi
fi

# 6. Install Docker Engine & Compose Plugin
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    log_success "Docker & Docker Compose already installed: $(docker --version) | $(docker compose version)"
else
    log_info "Configuring official Docker repository..."
    install -m 0755 -d /etc/apt/keyrings
    if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
        curl -fsSL "https://download.docker.com/linux/$OS_ID/gpg" | gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
        chmod a+r /etc/apt/keyrings/docker.gpg
    fi

    DPKG_ARCH="$(dpkg --print-architecture)"
    echo \
      "deb [arch=${DPKG_ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${OS_ID} \
      ${OS_VERSION_CODENAME} stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    log_info "Installing Docker Engine and Compose plugin..."
    apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin \
        docker-buildx-plugin

    log_success "Docker Engine installed: $(docker --version)"
fi

# Enable and start Docker service
systemctl enable docker
systemctl start docker

# Add non-root user to docker group
if [ -n "$TARGET_USER" ] && id "$TARGET_USER" &>/dev/null; then
    if ! id -nG "$TARGET_USER" | grep -qw "docker"; then
        log_info "Adding user '${TARGET_USER}' to the 'docker' group..."
        usermod -aG docker "$TARGET_USER"
        log_success "User '${TARGET_USER}' added to docker group."
    else
        log_success "User '${TARGET_USER}' is already in the docker group."
    fi
fi

# 7. Homelab Storage Baseline
log_info "Ensuring /opt/homelab storage baseline exists..."
mkdir -p /opt/homelab
if [ -n "$TARGET_USER" ] && id "$TARGET_USER" &>/dev/null; then
    chown -R "${TARGET_USER}:${TARGET_USER}" /opt/homelab
fi
log_success "/opt/homelab directory ready."

# 8. Final Baseline Verification Report
echo ""
echo -e "${BOLD}======================================================${NC}"
echo -e "${BOLD} Node Baseline Verification Summary${NC}"
echo -e "${BOLD}======================================================${NC}"
echo -e "  Host:         ${BOLD}$(hostname)${NC}"
echo -e "  OS:           ${PRETTY_NAME:-$OS_ID} ($ARCH)"
echo -e "  Python:       $(python3 --version 2>&1)"
echo -e "  uv:           $(uv --version 2>&1) ($(which uv))"
echo -e "  just:         $(just --version 2>&1) ($(which just))"
echo -e "  Docker:       $(docker --version 2>&1)"
echo -e "  Compose:      $(docker compose version 2>&1)"
echo -e "  WireGuard:    $(wg --version 2>&1 || echo 'wireguard-tools installed')"
echo -e "${BOLD}======================================================${NC}"
log_success "Node baseline setup completed successfully!"
