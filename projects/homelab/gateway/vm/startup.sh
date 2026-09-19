#!/bin/bash
set -e

# Base directory where this script is located
BASE_DIR="$(dirname "$(realpath "$0")")"

echo "=========================================="
echo " Starting Aperio VM Provisioning Sequence"
echo "=========================================="

# Ensure we are running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo bash startup.sh)"
  exit 1
fi

# Update system base first
echo ">>> [System] Updating package lists..."
apt-get update

# List of services to setup in dependency order
SERVICES=("docker" "wireguard" "platform")

for SERVICE in "${SERVICES[@]}"; do
    SERVICE_SCRIPT="$BASE_DIR/$SERVICE/startup.sh"
    
    if [ -f "$SERVICE_SCRIPT" ]; then
        echo "------------------------------------------"
        echo " Setting up: $SERVICE"
        echo "------------------------------------------"
        chmod +x "$SERVICE_SCRIPT"
        "$SERVICE_SCRIPT"
    else
        echo "!!! Warning: Startup script for $SERVICE not found at $SERVICE_SCRIPT"
    fi
done

echo "=========================================="
echo " Aperio VM Provisioning Complete"
echo "=========================================="
