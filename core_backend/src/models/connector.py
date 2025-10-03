"""Connector model for third-party service definitions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from src.database.connection import Base


class Connector(Base):
    """
    Connector model for defining third-party service integrations.

    Attributes:
        id: Primary key
        key: Unique identifier for the connector (e.g., 'jira', 'slack')
        name: Display name for the connector
        config_schema: JSON schema defining required configuration parameters (uses JSONB on Postgres via migration)
        created_at: Timestamp when connector was created
        connections: Relationship to user connections using this connector
    """
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    # JSON used at model level to stay dialect-agnostic; migration upgrades to JSONB when on Postgres
    config_schema = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    connections = relationship("Connection", back_populates="connector", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Connector(id={self.id}, key='{self.key}', name='{self.name}')>"
