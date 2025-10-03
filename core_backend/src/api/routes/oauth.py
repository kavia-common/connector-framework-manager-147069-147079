"""OAuth API routes for handling OAuth authorization flows."""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session, joinedload

from src.database.connection import get_db
from src.models.connection import Connection
from src.models.oauth_token import OAuthToken
from src.services.plugin_manager import plugin_manager
from src.auth.jwt import get_current_user_optional
from src.auth.oauth import oauth_helper, validate_oauth_callback
from src.api.schemas import (
    OAuthAuthorizeResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse
)

router = APIRouter(prefix="/oauth", tags=["oauth"])


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extract current user from authorization header."""
    return get_current_user_optional(authorization)


# PUBLIC_INTERFACE
@router.get("/{connector_key}/authorize", response_model=OAuthAuthorizeResponse, summary="Initiate OAuth", description="Initiate OAuth authorization flow for a connector and return authorization URL and signed state.", operation_id="initiate_oauth")
async def initiate_oauth(
    connector_key: str,
    connection_id: Optional[int] = Query(None, description="Existing connection ID to associate with OAuth"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate OAuth authorization flow for a connector.

    Args:
        connector_key: Connector key identifier
        connection_id: Optional existing connection ID to associate OAuth with

    Returns:
        Authorization URL and state parameter for OAuth flow
    """
    plugin = plugin_manager.get_plugin(connector_key)
    if not plugin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Connector '{connector_key}' not found")

    # Validate connection if provided
    if connection_id and current_user:
        connection = db.query(Connection).filter(
            Connection.id == connection_id,
            Connection.user_id == current_user["user_id"]
        ).first()
        if not connection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    try:
        # Signed state includes connector and optional connection_id
        state = oauth_helper.generate_state(connector_key=connector_key, connection_id=connection_id)
        redirect_uri = oauth_helper.build_redirect_uri(connector_key)
        auth_url = plugin.authorize_url(redirect_uri, state)
        return OAuthAuthorizeResponse(authorization_url=auth_url, state=state)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to initiate OAuth flow: {str(e)}")


# PUBLIC_INTERFACE
@router.get("/{connector_key}/callback", summary="Handle OAuth callback GET", description="Handle OAuth callback via GET with code and state", operation_id="handle_oauth_callback_get")
async def handle_oauth_callback_get(
    connector_key: str,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback (GET method) from OAuth provider.
    """
    return await _process_oauth_callback(
        connector_key=connector_key,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
        db=db
    )


# PUBLIC_INTERFACE
@router.post("/{connector_key}/callback", response_model=OAuthCallbackResponse, summary="Handle OAuth callback POST", description="Handle OAuth callback via POST with code and state", operation_id="handle_oauth_callback_post")
async def handle_oauth_callback_post(
    connector_key: str,
    callback_data: OAuthCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback (POST method) from OAuth provider.
    """
    return await _process_oauth_callback(
        connector_key=connector_key,
        code=callback_data.code,
        state=callback_data.state,
        connection_id=callback_data.connection_id,
        db=db
    )


async def _process_oauth_callback(
    connector_key: str,
    code: Optional[str],
    state: Optional[str],
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    connection_id: Optional[int] = None,
    db: Session = None
) -> OAuthCallbackResponse:
    """
    Process OAuth callback for both GET and POST methods.
    """
    if error:
        error_msg = error_description or f"OAuth error: {error}"
        return OAuthCallbackResponse(success=False, message=error_msg)

    if not code or not state:
        return OAuthCallbackResponse(success=False, message="Missing required OAuth parameters")

    plugin = plugin_manager.get_plugin(connector_key)
    if not plugin:
        return OAuthCallbackResponse(success=False, message=f"Connector '{connector_key}' not found")

    # Validate signed state
    validation = validate_oauth_callback({"code": code, "state": state})
    if not validation.get("success"):
        return OAuthCallbackResponse(success=False, message=validation.get("error", "Invalid state"))

    state_payload = validation.get("payload", {})
    # If connection_id not explicitly given, try from state
    if connection_id is None:
        connection_id = state_payload.get("connection_id")

    try:
        token_data = await plugin.handle_oauth_callback(code, state)
        if connection_id:
            connection = db.query(Connection).filter(Connection.id == connection_id).first()
            if connection:
                db.query(OAuthToken).filter(OAuthToken.connection_id == connection_id).delete()
                oauth_token = OAuthToken(
                    connection_id=connection_id,
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token"),
                    expires_at=token_data.get("expires_at")
                )
                db.add(oauth_token)
                connection.status = "active"
                db.commit()
                return OAuthCallbackResponse(success=True, message="OAuth authorization successful", connection_id=connection_id)

        return OAuthCallbackResponse(success=True, message="OAuth authorization successful (tokens not stored - no connection specified)")
    except Exception as e:
        return OAuthCallbackResponse(success=False, message=f"OAuth callback failed: {str(e)}")


# PUBLIC_INTERFACE
@router.delete("/{connector_key}/revoke/{connection_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke OAuth token", description="Revoke stored OAuth tokens for a specific connection", operation_id="revoke_oauth_token")
async def revoke_oauth_token(
    connector_key: str,
    connection_id: int,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke OAuth tokens for a connection.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    connection = db.query(Connection).options(joinedload(Connection.connector)).filter(
        Connection.id == connection_id, Connection.user_id == current_user["user_id"]
    ).first()

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    if connection.connector.key != connector_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Connector key mismatch")

    db.query(OAuthToken).filter(OAuthToken.connection_id == connection_id).delete()
    connection.status = "inactive"
    db.commit()
