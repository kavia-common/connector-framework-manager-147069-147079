"""OAuth token model for storing authentication tokens."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.connection import Base


class OAuthToken(Base):
    """
    OAuth token model for storing authentication tokens for connections.
    
    Attributes:
        id: Primary key
        connection_id: Foreign key to connections table
        access_token: OAuth access token
        refresh_token: OAuth refresh token (optional)
        expires_at: Token expiration timestamp
        connection: Relationship to the connection this token belongs to
    """
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    connection = relationship("Connection", back_populates="oauth_tokens")
    
    def __repr__(self):
        return f"<OAuthToken(id={self.id}, connection_id={self.connection_id}, expires_at={self.expires_at})>"
