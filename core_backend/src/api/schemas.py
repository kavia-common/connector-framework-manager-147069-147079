"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ConnectorResponse(BaseModel):
    """Response model for connector information."""
    id: int = Field(..., description="Connector ID")
    key: str = Field(..., description="Connector unique key")
    name: str = Field(..., description="Connector display name")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for connector configuration")
    supports_oauth: bool = Field(..., description="Whether the connector supports OAuth")
    oauth_scopes: List[str] = Field(default_factory=list, description="List of OAuth scopes required by connector")
    created_at: datetime = Field(..., description="Creation timestamp")

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
    id: int = Field(..., description="Connection ID")
    user_id: int = Field(..., description="Owner user ID")
    connector_id: int = Field(..., description="Associated connector ID")
    connector: ConnectorResponse = Field(..., description="Connector details")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Saved connector configuration")
    status: str = Field(..., description="Connection status")
    created_at: datetime = Field(..., description="Creation timestamp")
    has_oauth_token: bool = Field(default=False, description="Whether an OAuth token is stored for this connection")

    class Config:
        from_attributes = True


class OAuthAuthorizeResponse(BaseModel):
    """Response model for OAuth authorization initiation."""
    authorization_url: str = Field(..., description="URL to redirect the user for OAuth")
    state: str = Field(..., description="Signed state token for OAuth CSRF protection")


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback handling."""
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State token returned by provider")
    connection_id: Optional[int] = Field(None, description="Optional connection to attach tokens to")


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback completion."""
    success: bool = Field(..., description="Whether the OAuth process succeeded")
    message: str = Field(..., description="Human-readable status message")
    connection_id: Optional[int] = Field(None, description="Connection ID if tokens were stored")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Optional machine-readable error code")
