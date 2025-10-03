"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ConnectorResponse(BaseModel):
    """Response model for connector information."""
    id: int
    key: str
    name: str
    config_schema: Optional[Dict[str, Any]] = None
    supports_oauth: bool
    oauth_scopes: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ConnectionCreate(BaseModel):
    """Request model for creating a connection."""
    connector_key: str = Field(..., description="Connector key identifier")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Connector configuration data")


class ConnectionUpdate(BaseModel):
    """Request model for updating a connection."""
    config_data: Optional[Dict[str, Any]] = Field(None, description="Connector configuration data")
    status: Optional[str] = Field(None, description="Connection status")


class ConnectionResponse(BaseModel):
    """Response model for connection information."""
    id: int
    user_id: int
    connector_id: int
    connector: ConnectorResponse
    config_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    has_oauth_token: bool = False

    class Config:
        from_attributes = True


class OAuthAuthorizeResponse(BaseModel):
    """Response model for OAuth authorization initiation."""
    authorization_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback handling."""
    code: str
    state: str
    connection_id: Optional[int] = None


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback completion."""
    success: bool
    message: str
    connection_id: Optional[int] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    error_code: Optional[str] = None
