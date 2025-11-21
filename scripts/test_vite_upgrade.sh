#!/bin/bash
# Script to test Vite 7.x upgrade
# Usage: ./scripts/test_vite_upgrade.sh

set -e

echo "🧪 Testing Vite 7.x Upgrade"
echo "============================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Test results
PASSED=0
FAILED=0

# Function to test command
test_command() {
    local name=$1
    local command=$2
    
    echo -e "\n${YELLOW}Testing: $name${NC}"
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name passed${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test Frontend
echo -e "\n${YELLOW}=== Testing Frontend ===${NC}"
cd frontend

# Check Vite version
VITE_VERSION=$(npm list vite | grep vite@ | cut -d'@' -f2 | cut -d' ' -f1 || echo "not found")
echo "Vite version: $VITE_VERSION"

if [[ $VITE_VERSION == 7.* ]]; then
    echo -e "${GREEN}✓ Vite 7.x installed${NC}"
else
    echo -e "${RED}✗ Vite 7.x not installed (found: $VITE_VERSION)${NC}"
    ((FAILED++))
fi

# Install dependencies
test_command "npm install" "npm install"

# Build test
test_command "Build" "npm run build"

# Check build output
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo -e "${GREEN}✓ Build output exists${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Build output missing${NC}"
    ((FAILED++))
fi

cd ..

# Test Admin Dashboard
echo -e "\n${YELLOW}=== Testing Admin Dashboard ===${NC}"
cd admin-dashboard

# Check Vite version
VITE_VERSION=$(npm list vite | grep vite@ | cut -d'@' -f2 | cut -d' ' -f1 || echo "not found")
echo "Vite version: $VITE_VERSION"

if [[ $VITE_VERSION == 7.* ]]; then
    echo -e "${GREEN}✓ Vite 7.x installed${NC}"
else
    echo -e "${RED}✗ Vite 7.x not installed (found: $VITE_VERSION)${NC}"
    ((FAILED++))
fi

# Install dependencies
test_command "npm install" "npm install"

# Build test
test_command "Build" "npm run build"

# Check build output
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo -e "${GREEN}✓ Build output exists${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Build output missing${NC}"
    ((FAILED++))
fi

cd ..

# Summary
echo -e "\n${YELLOW}=== Test Summary ===${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
    exit 1
fi

