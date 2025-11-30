#!/bin/bash
# Script to run tests in Docker container

set -e  # Exit on error

echo "=========================================="
echo "Building Docker image for SemanticQuark"
echo "=========================================="

cd /Users/vkataria/vipin_github/community_contribution/semantic_quark/semanticquark

# Build Docker image
docker build -t semanticquark-test:latest -f Dockerfile .

echo ""
echo "=========================================="
echo "Running tests in Docker container"
echo "=========================================="

# Run tests in Docker
docker run --rm \
  -v "$(pwd):/app" \
  -w /app \
  semanticquark-test:latest \
  python -m pytest tests/test_query_types.py tests/test_logical_filters_and_relative_dates.py -v --tb=short

echo ""
echo "=========================================="
echo "Test execution complete!"
echo "=========================================="

