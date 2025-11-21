#!/bin/bash
# Script to fix security vulnerabilities in npm packages
# Usage: ./scripts/fix_security_vulnerabilities.sh

set -e

echo "🔒 Fixing Security Vulnerabilities in NeuroPredict-AI"
echo "======================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to fix vulnerabilities in a directory
fix_vulnerabilities() {
    local dir=$1
    local name=$2
    
    echo -e "\n${YELLOW}Checking ${name}...${NC}"
    cd "$dir"
    
    if [ -f "package.json" ]; then
        echo -e "${YELLOW}Running npm audit in ${name}...${NC}"
        npm audit
        
        echo -e "${YELLOW}Running npm audit fix...${NC}"
        if npm audit fix; then
            echo -e "${GREEN}✓ Vulnerabilities fixed in ${name}${NC}"
        else
            echo -e "${YELLOW}⚠ Some vulnerabilities may require manual intervention${NC}"
        fi
        
        echo -e "${YELLOW}Verifying fixes...${NC}"
        npm audit
    else
        echo -e "${RED}✗ package.json not found in ${dir}${NC}"
    fi
    
    cd ..
}

# Fix frontend
if [ -d "frontend" ]; then
    fix_vulnerabilities "frontend" "Frontend"
else
    echo -e "${RED}✗ Frontend directory not found${NC}"
fi

# Fix admin-dashboard
if [ -d "admin-dashboard" ]; then
    fix_vulnerabilities "admin-dashboard" "Admin Dashboard"
else
    echo -e "${YELLOW}⚠ Admin Dashboard directory not found${NC}"
fi

echo -e "\n${GREEN}✅ Security vulnerability fix process completed!${NC}"
echo -e "${YELLOW}⚠ Note: Some vulnerabilities may only affect development mode${NC}"
echo -e "${YELLOW}⚠ Production builds are typically not affected${NC}\n"

