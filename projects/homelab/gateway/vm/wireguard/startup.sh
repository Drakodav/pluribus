#!/bin/bash
set -e

# Configuration
WG_DIR="/etc/wireguard"
INTERFACE="wg0"
PRIVATE_KEY_FILE="$WG_DIR/privatekey"
PUBLIC_KEY_FILE="$WG_DIR/publickey"
CONFIG_FILE="$WG_DIR/$INTERFACE.conf"

echo ">>> [WireGuard] Starting setup..."

# 1. Install WireGuard
if ! command -v wg &> /dev/null; then
    echo ">>> [WireGuard] Installing WireGuard..."
    apt-get update
    apt-get install -y wireguard wireguard-tools
else
    echo ">>> [WireGuard] WireGuard already installed."
fi

# 2. Configure Firewall (UFW & iptables)
echo ">>> [WireGuard] Configuring Firewall..."
# Always allow SSH first to prevent lockout
ufw allow 22/tcp
# Allow WireGuard traffic in UFW
ufw allow 51820/udp
# Oracle-specific: Insert iptables rule at the top to bypass default REJECT
iptables -C INPUT -p udp --dport 51820 -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -p udp --dport 51820 -j ACCEPT
iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT
iptables -C INPUT -i wg0 -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -i wg0 -j ACCEPT

# Enable UFW if inactive (non-interactive)
if ! ufw status | grep -q "Status: active"; then
    echo "y" | ufw enable
fi

# 3. Generate Keys (Idempotent)
if [ ! -f "$PRIVATE_KEY_FILE" ]; then
    echo ">>> [WireGuard] Generating keys..."
    umask 077
    wg genkey | tee "$PRIVATE_KEY_FILE" | wg pubkey > "$PUBLIC_KEY_FILE"
    echo ">>> [WireGuard] Keys generated at $WG_DIR"
else
    echo ">>> [WireGuard] Keys already exist. Skipping generation."
fi

# Load environment variables if they exist in the sync directory
ENV_FILE="$(dirname "$(dirname "$0")")/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# 4. Create/Update Config (Always Overwrite)
echo ">>> [WireGuard] Generating configuration for $INTERFACE..."
PRIVATE_KEY=$(cat "$PRIVATE_KEY_FILE")

# Support both new Latin Distiller names and backward-compatible aliases
BACKBONE_APERIO_IP=${BACKBONE_APERIO_IP:-${BACKBONE_GATEWAY_IP:-10.10.0.1}}
BACKBONE_MACERATOR_IP=${BACKBONE_MACERATOR_IP:-${BACKBONE_POWERHOUSE_IP:-10.10.0.10}}
MACERATOR_PUBKEY=${BACKBONE_MACERATOR_PUBLIC_KEY:-${BACKBONE_POWERHOUSE_PUBLIC_KEY}}

# Stop service before overwriting to prevent SaveConfig from reverting changes
systemctl stop "wg-quick@$INTERFACE" || true

cat <<EOF > "$CONFIG_FILE"
[Interface]
Address = $BACKBONE_APERIO_IP/24
ListenPort = 51820
PrivateKey = $PRIVATE_KEY
MTU = 1420
SaveConfig = true
PostUp = ufw route allow in on wg0 out on ens3
PostUp = iptables -t nat -I POSTROUTING -o ens3 -j MASQUERADE
PreDown = ufw route delete allow in on wg0 out on ens3
PreDown = iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE

[Peer]
# Primary Powerhouse (macerator)
PublicKey = $MACERATOR_PUBKEY
AllowedIPs = $BACKBONE_MACERATOR_IP/32
EOF

echo ">>> [WireGuard] Config updated at $CONFIG_FILE"

# 5. Enable IP Forwarding (Required for Gateway)
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    sysctl -p
    echo ">>> [WireGuard] IP Forwarding enabled."
else
    echo ">>> [WireGuard] IP Forwarding already enabled."
fi

# 6. Start Service
if ! systemctl is-active --quiet "wg-quick@$INTERFACE"; then
    echo ">>> [WireGuard] Starting service..."
    systemctl enable "wg-quick@$INTERFACE"
    systemctl start "wg-quick@$INTERFACE"
else
    echo ">>> [WireGuard] Service is running."
fi

echo ">>> [WireGuard] Setup complete."
