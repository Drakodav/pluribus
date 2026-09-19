#!/bin/bash
set -e

# Ensure we are running as root locally
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./deploy.sh)"
  exit 1
fi

# Detect actual user if running via sudo to find the correct SSH key
REAL_USER="${SUDO_USER:-$USER}"
REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)

# Directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_DIR="~/vm-deployment"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment variables if .env exists in project root
if [ -f "$ROOT_DIR/.env" ]; then
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

# Usage: ./deploy.sh <SSH_USER> <SSH_HOST> <SSH_KEY_PATH>
SSH_USER=${1:-ubuntu}
SSH_HOST=${2:-${GATEWAY_PUBLIC_IP}}
SSH_KEY=${3:-$REAL_HOME/.ssh/id_rsa}

if [ -z "$SSH_HOST" ]; then
    echo "Error: SSH_HOST not provided and GATEWAY_PUBLIC_IP not found in $ROOT_DIR/.env"
    exit 1
fi

echo "=========================================="
echo " Deploying to Aperio Gateway: $SSH_USER@$SSH_HOST"
echo " Using Key: $SSH_KEY"
echo "=========================================="

# 0. Make all .sh files executable locally
echo ">>> Making local scripts executable..."
find "$SCRIPT_DIR" -name "*.sh" -exec chmod +x {} +

# 1. Sync vm folder to remote using rsync
echo ">>> Syncing configuration files..."
rsync -avz -e "ssh -o StrictHostKeyChecking=no -i $SSH_KEY" "$SCRIPT_DIR/" "$SSH_USER@$SSH_HOST:$REMOTE_DIR/"
if [ -f "$ROOT_DIR/.env" ]; then
    echo ">>> Syncing environment variables..."
    rsync -avz -e "ssh -o StrictHostKeyChecking=no -i $SSH_KEY" "$ROOT_DIR/.env" "$SSH_USER@$SSH_HOST:$REMOTE_DIR/.env"
fi

# 2. Execute startup script remotely
echo ">>> Executing remote startup script..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SSH_HOST" "sudo bash $REMOTE_DIR/startup.sh"

echo "=========================================="
echo " Aperio Gateway Deployment Complete"
echo "=========================================="
