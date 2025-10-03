from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend and docs
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
