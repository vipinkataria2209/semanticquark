FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for dependency resolution
COPY pyproject.toml .
COPY setup.py .

# Install package with postgres and redis support for Docker
# This installs core + postgres + redis + dev dependencies
RUN pip install --no-cache-dir -e ".[postgres,redis,dev]"

# Copy all necessary files
COPY README.md* ./
COPY semantic_layer/ ./semantic_layer/
COPY models/ ./models/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "semantic_layer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

