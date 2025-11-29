#!/bin/bash

# Test setup script for SemanticQuark

set -e

echo "🚀 Setting up SemanticQuark test environment..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Start services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check PostgreSQL health
echo "🔍 Checking PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U semanticquark > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check Redis health
echo "🔍 Checking Redis..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo "   Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

# Wait for application to be ready
echo "⏳ Waiting for application to start..."
sleep 5

# Check application health
echo "🔍 Checking application health..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Application is ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Application failed to start"
    docker-compose logs semanticquark
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📊 Services:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - API: http://localhost:8000"
echo ""
echo "📝 Test endpoints:"
echo "   - Health: curl http://localhost:8000/health"
echo "   - Schema: curl http://localhost:8000/api/v1/schema"
echo "   - Query: curl -X POST http://localhost:8000/api/v1/query -H 'Content-Type: application/json' -d '{\"measures\": [\"orders.count\"]}'"
echo ""
echo "📚 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"

