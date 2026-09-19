#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"
# shellcheck source=nodes/macerator/__shared__/utils.sh
source "$PROJECT_ROOT/nodes/macerator/__shared__/utils.sh"

log_info "Configuring Cockpit on host..."

# 1. Ensure PAM configuration is standard Ubuntu/Debian
log_info "Verifying PAM configuration for Cockpit..."
sudo bash -c 'cat <<EOF > /etc/pam.d/cockpit
#%PAM-1.0
@include common-auth
@include common-account
@include common-password
@include common-session
EOF'

# 2. Systemd Override for non-TLS backend behind Traefik reverse proxy
log_info "Applying systemd override for cockpit-tls --no-tls..."
sudo mkdir -p /etc/systemd/system/cockpit.service.d
sudo bash -c 'cat <<EOF > /etc/systemd/system/cockpit.service.d/no-tls.conf
[Service]
ExecStart=
ExecStart=/usr/lib/cockpit/cockpit-tls --no-tls
EOF'

# 3. Cockpit WebService Configuration
ensure_dir "/etc/cockpit"
sudo bash -c "cat <<EOF > /etc/cockpit/cockpit.conf
[WebService]
Origins = https://manage.${ROOT_DOMAIN} wss://manage.${ROOT_DOMAIN} http://localhost:9090
ProtocolHeader = X-Forwarded-Proto
AllowUnsecureLogin = true
AllowUnencrypted = true
EOF"
sudo chmod -R a+rX /etc/cockpit

# 4. Reload and Restart Services
log_info "Restarting Cockpit sockets and services..."
sudo systemctl daemon-reload
sudo systemctl start cockpit-wsinstance-http.socket cockpit-wsinstance-https-factory.socket 2>/dev/null || true
sudo systemctl enable cockpit.socket 2>/dev/null || true
sudo systemctl restart cockpit.socket
sudo systemctl restart cockpit || true

# 5. Consul Service Registration
log_info "Registering Cockpit in Consul..."
consul_register "macerator:manage:9090" "manage" 9090 \
    "traefik.enable=true" \
    "traefik.http.routers.manage.rule=Host(\"manage.${ROOT_DOMAIN}\")" \
    "traefik.http.routers.manage.entrypoints=websecure" \
    "traefik.http.routers.manage.tls.certresolver=myresolver" \
    "traefik.http.services.manage.loadbalancer.server.port=9090" \
    "traefik.http.routers.manage.middlewares=auth-cockpit@docker"

log_info "Cockpit is configured and registered at https://manage.${ROOT_DOMAIN}"
