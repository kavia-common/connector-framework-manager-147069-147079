"""Connectors API routes for managing connector definitions and plugins."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.models.connector import Connector
from src.services.plugin_manager import plugin_manager
from src.api.schemas import ConnectorResponse

router = APIRouter(prefix="/connectors", tags=["connectors"])


# PUBLIC_INTERFACE
@router.get("/", response_model=List[ConnectorResponse])
async def list_connectors(db: Session = Depends(get_db)):
    """
    List all available connectors from plugins and database.
    
    Returns a combined list of connectors from the plugin system
    and any additional connectors stored in the database.
    """
    # Get all available plugins
    plugins = plugin_manager.get_all_plugins()
    
    # Get stored connectors from database
    stored_connectors = db.query(Connector).all()
    stored_keys = {conn.key for conn in stored_connectors}
    
    result = []
    
    # Add stored connectors first
    for connector in stored_connectors:
        plugin = plugin_manager.get_plugin(connector.key)
        result.append(ConnectorResponse(
            id=connector.id,
            key=connector.key,
            name=connector.name,
            config_schema=connector.config_schema,
            supports_oauth=plugin is not None,
            oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
            created_at=connector.created_at
        ))
    
    # Add plugins that aren't in database yet
    for plugin in plugins:
        if plugin.metadata.key not in stored_keys:
            # Create a temporary connector response for plugins not yet stored
            result.append(ConnectorResponse(
                id=0,  # Temporary ID for plugins not in DB
                key=plugin.metadata.key,
                name=plugin.metadata.name,
                config_schema=plugin.get_config_schema(),
                supports_oauth=True,
                oauth_scopes=plugin.metadata.oauth_scopes,
                created_at=datetime.utcnow()
            ))
    
    return result


# PUBLIC_INTERFACE
@router.get("/{connector_key}", response_model=ConnectorResponse)
async def get_connector(connector_key: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific connector.
    
    Args:
        connector_key: Unique identifier for the connector
        
    Returns:
        Detailed connector information including configuration schema
    """
    # Try to get from database first
    stored_connector = db.query(Connector).filter(Connector.key == connector_key).first()
    
    # Get plugin info
    plugin = plugin_manager.get_plugin(connector_key)
    
    if not stored_connector and not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{connector_key}' not found"
        )
    
    if stored_connector:
        return ConnectorResponse(
            id=stored_connector.id,
            key=stored_connector.key,
            name=stored_connector.name,
            config_schema=stored_connector.config_schema,
            supports_oauth=plugin is not None,
            oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
            created_at=stored_connector.created_at
        )
    else:
        # Return plugin info for connectors not yet stored
        from datetime import datetime
        return ConnectorResponse(
            id=0,
            key=plugin.metadata.key,
            name=plugin.metadata.name,
            config_schema=plugin.get_config_schema(),
            supports_oauth=True,
            oauth_scopes=plugin.metadata.oauth_scopes,
            created_at=datetime.utcnow()
        )


# PUBLIC_INTERFACE
@router.post("/", response_model=ConnectorResponse, status_code=status.HTTP_201_CREATED)
async def create_connector(
    connector_data: dict,
    db: Session = Depends(get_db)
):
    """
    Create a new connector in the database.
    
    This endpoint allows storing custom connector configurations
    that extend beyond the built-in plugins.
    
    Args:
        connector_data: Connector configuration data
        
    Returns:
        Created connector information
    """
    # Check if connector key already exists
    existing = db.query(Connector).filter(Connector.key == connector_data.get("key")).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Connector with key '{connector_data.get('key')}' already exists"
        )
    
    # Create new connector
    connector = Connector(
        key=connector_data["key"],
        name=connector_data["name"],
        config_schema=connector_data.get("config_schema")
    )
    
    db.add(connector)
    db.commit()
    db.refresh(connector)
    
    # Get plugin info if available
    plugin = plugin_manager.get_plugin(connector.key)
    
    return ConnectorResponse(
        id=connector.id,
        key=connector.key,
        name=connector.name,
        config_schema=connector.config_schema,
        supports_oauth=plugin is not None,
        oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
        created_at=connector.created_at
    )


# PUBLIC_INTERFACE
@router.put("/{connector_key}", response_model=ConnectorResponse)
async def update_connector(
    connector_key: str,
    connector_data: dict,
    db: Session = Depends(get_db)
):
    """
    Update an existing connector in the database.
    
    Args:
        connector_key: Unique identifier for the connector
        connector_data: Updated connector configuration data
        
    Returns:
        Updated connector information
    """
    connector = db.query(Connector).filter(Connector.key == connector_key).first()
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{connector_key}' not found"
        )
    
    # Update fields
    if "name" in connector_data:
        connector.name = connector_data["name"]
    if "config_schema" in connector_data:
        connector.config_schema = connector_data["config_schema"]
    
    db.commit()
    db.refresh(connector)
    
    # Get plugin info if available
    plugin = plugin_manager.get_plugin(connector.key)
    
    return ConnectorResponse(
        id=connector.id,
        key=connector.key,
        name=connector.name,
        config_schema=connector.config_schema,
        supports_oauth=plugin is not None,
        oauth_scopes=plugin.metadata.oauth_scopes if plugin else [],
        created_at=connector.created_at
    )


# PUBLIC_INTERFACE
@router.delete("/{connector_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connector(connector_key: str, db: Session = Depends(get_db)):
    """
    Delete a connector from the database.
    
    Note: This only removes the database record, not the plugin implementation.
    
    Args:
        connector_key: Unique identifier for the connector
    """
    connector = db.query(Connector).filter(Connector.key == connector_key).first()
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{connector_key}' not found"
        )
    
    db.delete(connector)
    db.commit()
