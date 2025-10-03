from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.routes import connectors, connections, oauth

# FastAPI app configuration with OpenAPI metadata
app = FastAPI(
    title="Connector Framework Manager API",
    description="API for managing connectors, connections, and OAuth flows for third-party service integrations",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "connectors",
            "description": "Operations for managing connector definitions and plugin information"
        },
        {
            "name": "connections", 
            "description": "Operations for managing user connections to connectors"
        },
        {
            "name": "oauth",
            "description": "OAuth authorization flows for connector authentication"
        }
    ]
)

# CORS middleware configuration
frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
backend_url = os.getenv("BACKEND_BASE_URL", "http://localhost:3001")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, backend_url],  # Frontend and backend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers under /api prefix
app.include_router(connectors.router, prefix="/api")
app.include_router(connections.router, prefix="/api") 
app.include_router(oauth.router, prefix="/api")


# PUBLIC_INTERFACE
@app.get("/", tags=["health"])
def health_check():
    """
    Health check endpoint for monitoring service availability.
    
    Returns:
        Dict: Service health status
    """
    return {"message": "Healthy", "service": "Connector Framework Manager API"}


# PUBLIC_INTERFACE
@app.get("/api", tags=["health"])
def api_health_check():
    """
    API health check endpoint.
    
    Returns:
        Dict: API health status with version info
    """
    return {
        "message": "API is healthy",
        "version": "1.0.0",
        "service": "Connector Framework Manager API"
    }
