"""Main entry point for API server."""

import uvicorn

from semantic_layer.api.app import create_app
from semantic_layer.config import get_settings

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "semantic_layer.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )

