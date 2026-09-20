#!/bin/bash
set -e

echo ">>> [Docker] Starting setup..."

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo ">>> [Docker] Installing Docker..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release

    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
else
    echo ">>> [Docker] Docker already installed."
fi

# 2. Start and Enable Docker
systemctl enable docker
systemctl start docker

# 3. Verify Docker Compose (plugin)
if docker compose version &> /dev/null; then
    echo ">>> [Docker] Docker Compose is available."
else
    echo ">>> [Docker] Warning: Docker Compose plugin not found, attempting to install..."
    apt-get install -y docker-compose-plugin
fi

echo ">>> [Docker] Setup complete."
