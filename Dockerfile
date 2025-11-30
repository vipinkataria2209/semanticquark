FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest pytest-asyncio httpx

# Copy all necessary files
COPY setup.py ./
COPY README.md* ./
COPY semantic_layer/ ./semantic_layer/
COPY models/ ./models/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Install the package (handle missing README gracefully)
RUN if [ -f README.md ]; then pip install -e .; else pip install --no-deps -e . || pip install .; fi

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "semantic_layer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

