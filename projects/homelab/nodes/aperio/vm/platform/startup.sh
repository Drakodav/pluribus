#!/bin/bash
set -e

# Base directory for this service
BASE_DIR="$(dirname "$(realpath "$0")")"

echo ">>> [Platform] Starting Traefik and Consul stack..."

# Ensure we are in the correct directory
cd "$BASE_DIR"

# 1. Prepare Let's Encrypt storage
mkdir -p letsencrypt
touch letsencrypt/acme.json
chmod 600 letsencrypt/acme.json

# 2. Start the stack
# Load env vars for compose interpolation
if [ -f "../.env" ]; then
    set -a
    . "../.env"
    set +a
fi

docker compose pull
docker compose up -d

echo ">>> [Platform] Stack deployed."
echo ">>> [Platform] Consul UI should be available at http://localhost:8500 (tunnel needed for public access)"
