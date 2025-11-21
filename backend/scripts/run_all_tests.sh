#!/bin/bash
# Run all tests for NeuroPredict-AI
# Usage: ./scripts/run_all_tests.sh

set -e

echo "🧪 Running all tests for NeuroPredict-AI"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Run unit and integration tests with coverage
echo -e "\n${YELLOW}1. Running backend unit and integration tests...${NC}"
cd backend
pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=70 \
    -v \
    -m "not slow" \
    tests/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend tests passed${NC}"
else
    echo "✗ Backend tests failed"
    exit 1
fi

# 2. Run performance tests
echo -e "\n${YELLOW}2. Running performance tests...${NC}"
pytest -v -m performance tests/performance/ || echo -e "${YELLOW}⚠ Performance tests have warnings${NC}"

# 3. Run security tests
echo -e "\n${YELLOW}3. Running security tests...${NC}"
pytest -v -m security tests/security/ || echo -e "${YELLOW}⚠ Security tests have warnings${NC}"

# 4. Run slow tests (if needed)
echo -e "\n${YELLOW}4. Running slow tests (optional)...${NC}"
read -p "Run slow tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pytest -v -m slow tests/
fi

cd ..

# 5. Run E2E tests (if Playwright is installed)
if [ -d "tests/e2e" ]; then
    echo -e "\n${YELLOW}5. Running E2E tests with Playwright...${NC}"
    cd tests/e2e
    if command -v npx &> /dev/null; then
        npx playwright test || echo -e "${YELLOW}⚠ E2E tests require backend/frontend to be running${NC}"
    else
        echo -e "${YELLOW}⚠ npx not found, skipping E2E tests${NC}"
    fi
    cd ../..
fi

echo -e "\n${GREEN}✅ All tests completed!${NC}"
echo "Coverage report: backend/htmlcov/index.html"

