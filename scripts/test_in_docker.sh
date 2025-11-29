#!/bin/bash
# Test script to run tests inside Docker container

set -e

echo "============================================================"
echo "Running Tests in Docker Container"
echo "============================================================"
echo ""

# Build the Docker image if needed
echo "Building Docker image..."
docker-compose build semanticquark

echo ""
echo "Starting services..."
docker-compose up -d postgres redis

echo ""
echo "Waiting for services to be ready..."
sleep 5

echo ""
echo "Running migration tests..."
docker-compose run --rm semanticquark python3 scripts/test_migration.py

echo ""
echo "Running API functionality tests..."
docker-compose run --rm semanticquark python3 scripts/test_api_functionality.py

echo ""
echo "Running backward compatibility tests..."
docker-compose run --rm semanticquark python3 -c "
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

print('Testing old imports...')
from semantic_layer.connectors import BaseConnector, PostgreSQLConnector
from semantic_layer.query_builder import SQLBuilder
from semantic_layer.engine import QueryEngine
from semantic_layer.metrics import MetricsCollector
from semantic_layer.logging import QueryLogger
print('✅ All old imports work')

print('Testing new imports...')
from semantic_layer.drivers import BaseDriver, PostgresDriver
from semantic_layer.sql import SQLBuilder as NewSQLBuilder
from semantic_layer.orchestrator import QueryEngine as NewQueryEngine
from semantic_layer.monitoring import MetricsCollector as NewMC, QueryLogger as NewQL
print('✅ All new imports work')

print('Testing equivalence...')
assert BaseConnector == BaseDriver
print('✅ Old and new imports point to same classes')

print('')
print('✅ All backward compatibility tests pass!')
"

echo ""
echo "============================================================"
echo "All Docker Tests Complete"
echo "============================================================"

