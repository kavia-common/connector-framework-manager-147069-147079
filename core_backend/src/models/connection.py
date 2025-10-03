"""Connection model for user-connector relationships."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.database.connection import Base


class Connection(Base):
    """
    Connection model representing a user's configured connection to a specific connector.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        connector_id: Foreign key to connectors table
        config_data: JSON data containing connector-specific configuration
        status: Connection status (active, inactive, error)
        created_at: Timestamp when connection was created
        user: Relationship to the user who owns this connection
        connector: Relationship to the connector this connection uses
        oauth_tokens: Relationship to OAuth tokens for this connection
    """
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    config_data = Column(JSON, nullable=True)  # Connector-specific configuration data
    status = Column(String, default="inactive", nullable=False)  # active, inactive, error
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="connections")
    connector = relationship("Connector", back_populates="connections")
    oauth_tokens = relationship("OAuthToken", back_populates="connection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Connection(id={self.id}, user_id={self.user_id}, connector_id={self.connector_id}, status='{self.status}')>"
