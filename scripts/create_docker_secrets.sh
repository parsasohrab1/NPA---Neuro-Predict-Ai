#!/bin/bash
# Script to create Docker secrets for production
# Usage: ./scripts/create_docker_secrets.sh

set -e

echo "🔐 Creating Docker secrets for NeuroPredict-AI Production"
echo "=========================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo -e "${YELLOW}⚠ Docker Swarm is not active. Initializing...${NC}"
    docker swarm init
fi

# Function to create secret if it doesn't exist
create_secret() {
    local secret_name=$1
    local prompt_text=$2
    local is_password=$3
    
    if docker secret ls | grep -q "$secret_name"; then
        echo -e "${YELLOW}Secret $secret_name already exists. Skipping...${NC}"
        return
    fi
    
    if [ "$is_password" = "true" ]; then
        # Read password without showing on screen
        read -sp "$prompt_text: " secret_value
        echo
        read -sp "Confirm $prompt_text: " secret_confirm
        echo
        
        if [ "$secret_value" != "$secret_confirm" ]; then
            echo -e "${RED}✗ Passwords do not match!${NC}"
            exit 1
        fi
    else
        read -p "$prompt_text: " secret_value
    fi
    
    if [ -z "$secret_value" ]; then
        echo -e "${RED}✗ Value cannot be empty!${NC}"
        exit 1
    fi
    
    echo "$secret_value" | docker secret create "$secret_name" -
    echo -e "${GREEN}✓ Secret $secret_name created${NC}"
}

# Generate secret key if needed
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32
}

echo -e "\n${YELLOW}Creating secrets...${NC}\n"

# 1. Secret Key for JWT
if docker secret ls | grep -q "neuropredict_secret_key"; then
    echo -e "${YELLOW}Secret neuropredict_secret_key already exists.${NC}"
    read -p "Generate new secret key? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker secret rm neuropredict_secret_key 2>/dev/null || true
        secret_key=$(generate_secret_key)
        echo "$secret_key" | docker secret create neuropredict_secret_key -
        echo -e "${GREEN}✓ Secret neuropredict_secret_key created (auto-generated)${NC}"
    fi
else
    secret_key=$(generate_secret_key)
    echo "$secret_key" | docker secret create neuropredict_secret_key -
    echo -e "${GREEN}✓ Secret neuropredict_secret_key created (auto-generated)${NC}"
fi

# 2. Database Password
create_secret "neuropredict_database_password" "Database password" true

# 3. Redis Password (optional)
read -p "Create Redis password secret? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_secret "neuropredict_redis_password" "Redis password" true
fi

# 4. Grafana Admin Password
create_secret "neuropredict_grafana_password" "Grafana admin password" true

echo -e "\n${GREEN}✅ All secrets created successfully!${NC}\n"

echo "Listing created secrets:"
docker secret ls | grep neuropredict

echo -e "\n${YELLOW}⚠ Important: Save these secrets in a secure password manager!${NC}"
echo -e "${YELLOW}⚠ Secrets cannot be retrieved once created.${NC}\n"

echo "To use these secrets in production:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"

