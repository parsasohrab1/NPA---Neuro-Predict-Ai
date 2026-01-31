#!/bin/bash
# Dependency Update Script
# بررسی و به‌روزرسانی dependencies با بررسی security

set -e

echo "=========================================="
echo "NeuroPredict-AI Dependency Update"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# Check for outdated packages
echo "Checking for outdated packages..."
pip list --outdated

# Check for security vulnerabilities
echo ""
echo "Checking for security vulnerabilities..."
safety check

# Update requirements.txt if needed
echo ""
echo "To update a package:"
echo "  pip install --upgrade <package-name>"
echo "  pip freeze > requirements.txt"
echo ""
echo "⚠️  Always test after updating dependencies!"

