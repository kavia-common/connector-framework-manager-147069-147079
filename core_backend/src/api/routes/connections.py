"""Connections API routes for managing user connections to connectors."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload

from src.database.connection import get_db
from src.models.user import User
from src.models.connector import Connector
from src.models.connection import Connection
from src.services.plugin_manager import plugin_manager
from src.auth.jwt import get_current_user_optional
from src.api.schemas import (
    ConnectionCreate, 
    ConnectionUpdate, 
    ConnectionResponse,
    ConnectorResponse
)

router = APIRouter(prefix="/connections", tags=["connections"])


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extract current user from authorization header."""
    return get_current_user_optional(authorization)


def require_user(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authenticated user for protected endpoints."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user


# PUBLIC_INTERFACE
@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    current_user: Dict[str, Any] = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    List all connections for the authenticated user.
    
    Returns:
        List of user's connections with connector details
    """
    user_id = current_user["user_id"]
    
    connections = db.query(Connection).options(
        joinedload(Connection.connector),
        joinedload(Connection.oauth_tokens)
    ).filter(Connection.user_id == user_id).all()
    
    result = []
    for connection in connections:
        # Get plugin info for OAuth capabilities
        plugin = plugin_manager.get_plugin(connection.connector.key)
        
        # Check if connection has OAuth tokens
        has_oauth_token = len(connection.oauth_tokens) > 0
        
        result.append(ConnectionResponse(
            id=connection.id,
            user_id=connection.user_id,
            connector_id=connection.connector_id,
            connector=ConnectorResponse(
                id=connection.connector.id,
                key=connection.connector.key,
                name=connection.connector.name,
                config_schema=connection.connector.config_schema,
                supports_oauth=(plugin.metadata.supports_oauth if plugin else False),
                oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
                created_at=connection.connector.created_at
            ),
            config_data=connection.config_data,
            status=connection.status,
            created_at=connection.created_at,
            has_oauth_token=has_oauth_token
        ))
    
    return result


# PUBLIC_INTERFACE
@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: int,
    current_user: Dict[str, Any] = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific connection by ID.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        Connection details
    """
    user_id = current_user["user_id"]
    
    connection = db.query(Connection).options(
        joinedload(Connection.connector),
        joinedload(Connection.oauth_tokens)
    ).filter(
        Connection.id == connection_id,
        Connection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # Get plugin info
    plugin = plugin_manager.get_plugin(connection.connector.key)
    has_oauth_token = len(connection.oauth_tokens) > 0
    
    return ConnectionResponse(
        id=connection.id,
        user_id=connection.user_id,
        connector_id=connection.connector_id,
        connector=ConnectorResponse(
            id=connection.connector.id,
            key=connection.connector.key,
            name=connection.connector.name,
            config_schema=connection.connector.config_schema,
            supports_oauth=(plugin.metadata.supports_oauth if plugin else False),
            oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
            created_at=connection.connector.created_at
        ),
        config_data=connection.config_data,
        status=connection.status,
        created_at=connection.created_at,
        has_oauth_token=has_oauth_token
    )


# PUBLIC_INTERFACE
@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    current_user: Dict[str, Any] = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Create a new connection for the authenticated user.
    
    Args:
        connection_data: Connection creation data
        
    Returns:
        Created connection details
    """
    user_id = current_user["user_id"]
    
    # Ensure user exists in database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Create user if not exists
        user = User(id=user_id, email=current_user["email"])
        db.add(user)
        db.commit()
    
    # Get or create connector
    connector = db.query(Connector).filter(Connector.key == connection_data.connector_key).first()
    if not connector:
        # Check if plugin exists
        plugin = plugin_manager.get_plugin(connection_data.connector_key)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector '{connection_data.connector_key}' not found"
            )
        
        # Create connector from plugin
        connector = Connector(
            key=plugin.metadata.key,
            name=plugin.metadata.name,
            config_schema=plugin.get_config_schema()
        )
        db.add(connector)
        db.commit()
        db.refresh(connector)
    
    # Validate configuration against schema if provided
    if connection_data.config_data and connector.config_schema:
        # Basic validation - in production, use jsonschema library
        required_fields = connector.config_schema.get("required", [])
        
        # Check required fields
        for field in required_fields:
            if field not in connection_data.config_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
    
    # Check if connection already exists
    existing = db.query(Connection).filter(
        Connection.user_id == user_id,
        Connection.connector_id == connector.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Connection already exists for this connector"
        )
    
    # Create connection
    connection = Connection(
        user_id=user_id,
        connector_id=connector.id,
        config_data=connection_data.config_data,
        status="inactive"
    )
    
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    # Load relationships
    db.refresh(connection)
    connection = db.query(Connection).options(
        joinedload(Connection.connector),
        joinedload(Connection.oauth_tokens)
    ).filter(Connection.id == connection.id).first()
    
    # Get plugin info
    plugin = plugin_manager.get_plugin(connector.key)
    
    return ConnectionResponse(
        id=connection.id,
        user_id=connection.user_id,
        connector_id=connection.connector_id,
        connector=ConnectorResponse(
            id=connection.connector.id,
            key=connection.connector.key,
            name=connection.connector.name,
            config_schema=connection.connector.config_schema,
            supports_oauth=(plugin.metadata.supports_oauth if plugin else False),
            oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
            created_at=connection.connector.created_at
        ),
        config_data=connection.config_data,
        status=connection.status,
        created_at=connection.created_at,
        has_oauth_token=False
    )


# PUBLIC_INTERFACE
@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: int,
    connection_data: ConnectionUpdate,
    current_user: Dict[str, Any] = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing connection.
    
    Args:
        connection_id: Connection ID
        connection_data: Connection update data
        
    Returns:
        Updated connection details
    """
    user_id = current_user["user_id"]
    
    connection = db.query(Connection).options(
        joinedload(Connection.connector)
    ).filter(
        Connection.id == connection_id,
        Connection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # Update fields
    if connection_data.config_data is not None:
        # Validate against schema if provided
        if connection.connector.config_schema:
            required_fields = connection.connector.config_schema.get("required", [])
            
            # Check required fields
            for field in required_fields:
                if field not in connection_data.config_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing required field: {field}"
                    )
        
        connection.config_data = connection_data.config_data
    
    if connection_data.status is not None:
        connection.status = connection_data.status
    
    db.commit()
    db.refresh(connection)
    
    # Load relationships for response
    connection = db.query(Connection).options(
        joinedload(Connection.connector),
        joinedload(Connection.oauth_tokens)
    ).filter(Connection.id == connection.id).first()
    
    # Get plugin info
    plugin = plugin_manager.get_plugin(connection.connector.key)
    has_oauth_token = len(connection.oauth_tokens) > 0
    
    return ConnectionResponse(
        id=connection.id,
        user_id=connection.user_id,
        connector_id=connection.connector_id,
        connector=ConnectorResponse(
            id=connection.connector.id,
            key=connection.connector.key,
            name=connection.connector.name,
            config_schema=connection.connector.config_schema,
            supports_oauth=plugin is not None,
            oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
            created_at=connection.connector.created_at
        ),
        config_data=connection.config_data,
        status=connection.status,
        created_at=connection.created_at,
        has_oauth_token=has_oauth_token
    )


# PUBLIC_INTERFACE
@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: int,
    current_user: Dict[str, Any] = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Delete a connection.
    
    Args:
        connection_id: Connection ID
    """
    user_id = current_user["user_id"]
    
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    db.delete(connection)
    db.commit()


# PUBLIC_INTERFACE
@router.post("/{connection_id}/test", response_model=dict)
async def test_connection(
    connection_id: int,
    current_user: Dict[str, Any] = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    Test a connection to verify it's working properly.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        Test result with success status and sample data
    """
    user_id = current_user["user_id"]
    
    connection = db.query(Connection).options(
        joinedload(Connection.connector),
        joinedload(Connection.oauth_tokens)
    ).filter(
        Connection.id == connection_id,
        Connection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # Get plugin
    plugin = plugin_manager.get_plugin(connection.connector.key)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plugin not available for this connector"
        )
    
    try:
        # Prepare token data if available
        token_data = None
        if connection.oauth_tokens:
            token = connection.oauth_tokens[0]  # Get latest token
            token_data = {
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "expires_at": token.expires_at
            }
        
        # Test the connection
        is_connected = await plugin.test_connection(connection.config_data or {}, token_data)
        
        if is_connected:
            # Update connection status
            connection.status = "active"
            db.commit()
            
            # Fetch sample data
            sample_data = await plugin.fetch_sample(connection.config_data or {}, token_data)
            
            return {
                "success": True,
                "message": "Connection test successful",
                "sample_data": sample_data
            }
        else:
            connection.status = "error"
            db.commit()
            
            return {
                "success": False,
                "message": "Connection test failed",
                "sample_data": None
            }
    
    except Exception as e:
        connection.status = "error"
        db.commit()
        
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
            "sample_data": None
        }
