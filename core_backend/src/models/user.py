"""User model for authentication and user management."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from src.database.connection import Base


class User(Base):
    """
    User model for storing user information.
    
    Attributes:
        id: Primary key
        email: User's email address (unique)
        created_at: Timestamp when user was created
        connections: Relationship to user's connector connections
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    connections = relationship("Connection", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
