#!/bin/bash
# Script to run tests with coverage report

echo "🧪 Running NeuroPredict-AI Tests"
echo "================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
echo "Running tests with coverage..."
pytest \
    --cov=app \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --cov-report=xml \
    -v \
    tests/

# Check coverage threshold
COVERAGE=$(coverage report | grep TOTAL | awk '{print $NF}' | sed 's/%//')
echo ""
echo "📊 Test Coverage: ${COVERAGE}%"

if (( $(echo "$COVERAGE < 60" | bc -l) )); then
    echo "⚠️  Warning: Coverage is below 60%"
    exit 1
else
    echo "✅ Coverage meets minimum threshold (60%)"
fi

echo ""
echo "📁 Coverage report generated in htmlcov/index.html"

