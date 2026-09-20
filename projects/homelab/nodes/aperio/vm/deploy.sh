#!/bin/bash
set -e

# Resolve user home directory portably (Linux, macOS, and CI)
REAL_USER="$USER"
REAL_HOME="${HOME:-$(eval echo "~$USER")}"

# Directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_DIR="~/vm-deployment"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Load environment variables if .env exists in project root
if [ -f "$ROOT_DIR/.env" ]; then
    set -a
    . "$ROOT_DIR/.env"
    set +a
fi

# Usage: ./deploy.sh [SSH_USER] [SSH_HOST] [SSH_KEY_PATH]
SSH_USER=${1:-${NODE_APERIO_SSH_USER}}
SSH_HOST=${2:-${NODE_APERIO_PUBLIC_IP}}
SSH_KEY=${3:-${NODE_APERIO_SSH_KEY}}
SSH_KEY="${SSH_KEY/#\~/$REAL_HOME}"

if [ -z "$SSH_HOST" ]; then
    echo "Error: SSH_HOST not provided and NODE_APERIO_PUBLIC_IP not found in $ROOT_DIR/.env"
    exit 1
fi

if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH private key not found at '$SSH_KEY'"
    echo "To fix this, either:"
    echo "  1. Copy your private key to: $SSH_KEY"
    echo "  2. Or set NODE_APERIO_SSH_KEY in $ROOT_DIR/.env to point to your key"
    echo "  3. Or pass it as argument: ./deploy.sh $SSH_USER $SSH_HOST /path/to/key"
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
