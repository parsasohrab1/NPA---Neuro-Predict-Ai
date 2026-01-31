#!/bin/bash
# Script to run all tests with coverage

set -e

echo "=========================================="
echo "NeuroPredict-AI Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Run tests
echo -e "${YELLOW}Running Unit Tests...${NC}"
pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-report=html -m unit

echo ""
echo -e "${YELLOW}Running Integration Tests...${NC}"
pytest tests/integration/ -v -m integration

echo ""
echo -e "${YELLOW}Running E2E Tests...${NC}"
pytest tests/e2e/ -v -m e2e

echo ""
echo -e "${YELLOW}Running Performance Tests...${NC}"
pytest tests/performance/ -v -m performance

echo ""
echo -e "${YELLOW}Running Security Tests...${NC}"
pytest tests/security/ -v -m security

echo ""
echo -e "${GREEN}=========================================="
echo "All tests completed!"
echo "Coverage report: htmlcov/index.html"
echo "==========================================${NC}"

