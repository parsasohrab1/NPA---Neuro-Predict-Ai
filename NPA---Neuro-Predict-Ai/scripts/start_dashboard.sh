#!/bin/bash
# Script to start NeuroPredict-AI Live Dashboard

echo "=========================================="
echo "Starting NeuroPredict-AI Live Dashboard"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")/.."

echo "📦 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Services started!"
echo ""
echo "🌐 Access the dashboards at:"
echo "   - Main Application: http://localhost:3000"
echo "   - Admin Dashboard:  http://localhost:3001"
echo "   - API Documentation: http://localhost:8000/api/docs"
echo "   - Health Check:      http://localhost:8000/health"
echo ""
echo "📊 Monitoring:"
echo "   - Prometheus:       http://localhost:9090"
echo "   - Grafana:          http://localhost:3001 (if using production compose)"
echo ""
echo "To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "To stop services:"
echo "   docker-compose down"
echo ""

