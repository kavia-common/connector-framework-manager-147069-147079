"""OAuth utilities for handling authorization flows."""
import os
import secrets
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse, parse_qs


class OAuthHelper:
    """Helper class for OAuth operations."""
    
    def __init__(self):
        """Initialize OAuth helper with base redirect URL."""
        self.redirect_base = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:3001")
    
    # PUBLIC_INTERFACE
    def generate_state(self) -> str:
        """
        Generate a secure random state parameter for OAuth.
        
        Returns:
            str: Secure random state string
        """
        return secrets.token_urlsafe(32)
    
    # PUBLIC_INTERFACE
    def build_redirect_uri(self, provider: str) -> str:
        """
        Build OAuth redirect URI for a specific provider.
        
        Args:
            provider: Provider key (e.g., 'jira', 'slack')
            
        Returns:
            str: Complete redirect URI for the provider
        """
        return f"{self.redirect_base}/api/auth/oauth/{provider}/callback"
    
    # PUBLIC_INTERFACE
    def build_authorize_url(self, base_url: str, params: Dict[str, Any]) -> str:
        """
        Build authorization URL with parameters.
        
        Args:
            base_url: Base authorization URL
            params: Query parameters to append
            
        Returns:
            str: Complete authorization URL
        """
        query_string = urlencode(params)
        return f"{base_url}?{query_string}"
    
    # PUBLIC_INTERFACE
    def validate_state(self, received_state: str, expected_state: str) -> bool:
        """
        Validate OAuth state parameter to prevent CSRF attacks.
        
        Args:
            received_state: State received from OAuth callback
            expected_state: Expected state value
            
        Returns:
            bool: True if state is valid, False otherwise
        """
        return received_state == expected_state
    
    # PUBLIC_INTERFACE
    def parse_callback_params(self, callback_url: str) -> Dict[str, Any]:
        """
        Parse parameters from OAuth callback URL.
        
        Args:
            callback_url: Complete callback URL with parameters
            
        Returns:
            Dict: Parsed callback parameters
        """
        parsed_url = urlparse(callback_url)
        params = parse_qs(parsed_url.query)
        
        # Convert single-item lists to strings
        result = {}
        for key, value_list in params.items():
            if value_list:
                result[key] = value_list[0]
        
        return result
    
    # PUBLIC_INTERFACE
    def handle_callback_error(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Handle OAuth callback errors.
        
        Args:
            params: Callback parameters
            
        Returns:
            str: Error message if error exists, None otherwise
        """
        error = params.get("error")
        if error:
            error_description = params.get("error_description", "Unknown OAuth error")
            return f"OAuth error: {error} - {error_description}"
        return None


# Global OAuth helper instance
oauth_helper = OAuthHelper()


# PUBLIC_INTERFACE
def create_oauth_session_data(provider: str, state: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Create session data for OAuth flow.
    
    Args:
        provider: OAuth provider key
        state: OAuth state parameter
        user_id: Optional user ID if user is authenticated
        
    Returns:
        Dict: Session data for OAuth flow
    """
    return {
        "provider": provider,
        "state": state,
        "user_id": user_id,
        "created_at": "placeholder_timestamp"  # Would use actual timestamp
    }


# PUBLIC_INTERFACE
def validate_oauth_callback(params: Dict[str, Any], expected_state: str) -> Dict[str, Any]:
    """
    Validate OAuth callback parameters.
    
    Args:
        params: Callback parameters from OAuth provider
        expected_state: Expected state value
        
    Returns:
        Dict: Validation result with success status and data/error
    """
    # Check for errors
    error_msg = oauth_helper.handle_callback_error(params)
    if error_msg:
        return {"success": False, "error": error_msg}
    
    # Validate state
    received_state = params.get("state")
    if not received_state or not oauth_helper.validate_state(received_state, expected_state):
        return {"success": False, "error": "Invalid state parameter"}
    
    # Check for authorization code
    code = params.get("code")
    if not code:
        return {"success": False, "error": "Missing authorization code"}
    
    return {
        "success": True,
        "code": code,
        "state": received_state
    }
