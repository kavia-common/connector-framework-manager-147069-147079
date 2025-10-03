"""JWT utilities for authentication and authorization."""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status


class JWTManager:
    """Manager for JWT token operations."""
    
    def __init__(self):
        """Initialize JWT manager with secret from environment."""
        self.secret_key = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # Warn if using default secret
        if self.secret_key == "dev-secret-key-change-in-production":
            print("WARNING: Using default JWT secret. Set JWT_SECRET environment variable for production.")
    
    # PUBLIC_INTERFACE
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time, defaults to 30 minutes
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    # PUBLIC_INTERFACE
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dict: Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # PUBLIC_INTERFACE
    def create_user_token(self, user_id: int, email: str) -> str:
        """
        Create a JWT token for a user.
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            str: JWT token for the user
        """
        return self.create_access_token(
            data={"sub": str(user_id), "email": email, "type": "access"}
        )


# Global JWT manager instance
jwt_manager = JWTManager()


# PUBLIC_INTERFACE
def get_current_user_optional(token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token (optional dependency).
    
    Args:
        token: Bearer token from Authorization header
        
    Returns:
        Dict containing user info if token is valid, None otherwise
    """
    if not token:
        return None
    
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = jwt_manager.verify_token(token)
        return {
            "user_id": int(payload.get("sub")),
            "email": payload.get("email"),
            "token_type": payload.get("type")
        }
    except HTTPException:
        return None
