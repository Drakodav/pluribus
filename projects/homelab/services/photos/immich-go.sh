#!/bin/bash
set -euo pipefail

# Helper script for running immich-go CLI tool on Macerator
BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$BASE_DIR/../.." && pwd)"

if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$PROJECT_ROOT/.env"
    set +a
fi

API_KEY="${SERVICE_PHOTOS_API_KEY:-}"
IMMICH_GO_DIR="${HOME}/Downloads/immich-go_Linux_x86_64"

if [ -z "$API_KEY" ]; then
    echo "Warning: SERVICE_PHOTOS_API_KEY is not defined in .env"
fi

if [ ! -d "$IMMICH_GO_DIR" ]; then
    echo "Info: immich-go directory not found at $IMMICH_GO_DIR"
    echo "Usage example once installed:"
    echo "  ./immich-go upload from-folder --server=http://localhost:2283 --api-key=\$API_KEY /path/to/photos"
    exit 0
fi

cd "$IMMICH_GO_DIR"
./immich-go "$@"
