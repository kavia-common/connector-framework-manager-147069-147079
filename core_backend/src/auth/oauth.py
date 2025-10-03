"""OAuth utilities for handling authorization flows."""
import base64
import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse, parse_qs

from src.config import settings


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class OAuthHelper:
    """Helper class for OAuth operations with signed state support."""
    def __init__(self):
        """Initialize using env-driven settings."""
        self.frontend_base = settings.frontend_base_url
        self.jwt_secret = settings.jwt_secret.encode("utf-8")

    # PUBLIC_INTERFACE
    def generate_state(self, connector_key: Optional[str] = None, connection_id: Optional[int] = None, ttl_seconds: int = 600) -> str:
        """
        Generate a signed, expiring OAuth state token.

        Args:
            connector_key: Optional connector key for context
            connection_id: Optional connection id to bind
            ttl_seconds: Token validity in seconds

        Returns:
            str: Signed state token
        """
        now = datetime.now(timezone.utc)
        payload = {
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
            "nonce": _b64url(hashlib.sha256(str(now.timestamp()).encode()).digest()[:12]),
        }
        if connector_key:
            payload["connector"] = connector_key
        if connection_id is not None:
            payload["connection_id"] = connection_id

        header = {"alg": "HS256", "typ": "STATE"}
        encoded_header = _b64url(json.dumps(header, separators=(",", ":")).encode())
        encoded_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{encoded_header}.{encoded_payload}".encode()
        signature = hmac.new(self.jwt_secret, signing_input, hashlib.sha256).digest()
        encoded_sig = _b64url(signature)
        return f"{encoded_header}.{encoded_payload}.{encoded_sig}"

    # PUBLIC_INTERFACE
    def verify_state(self, state: str) -> Dict[str, Any]:
        """
        Verify a signed state token and return its payload.

        Args:
            state: State token

        Returns:
            Dict[str, Any]: Decoded and verified payload

        Raises:
            ValueError: If invalid signature or expired
        """
        try:
            parts = state.split(".")
            if len(parts) != 3:
                raise ValueError("Malformed state")
            header_b64, payload_b64, sig_b64 = parts
            signing_input = f"{header_b64}.{payload_b64}".encode()
            expected_sig = hmac.new(self.jwt_secret, signing_input, hashlib.sha256).digest()
            if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
                raise ValueError("Invalid state signature")
            payload = json.loads(_b64url_decode(payload_b64))
            now = int(datetime.now(timezone.utc).timestamp())
            if payload.get("exp") is not None and now > int(payload["exp"]):
                raise ValueError("State expired")
            return payload
        except Exception as e:
            raise ValueError(f"State verification failed: {e}")

    # PUBLIC_INTERFACE
    def build_redirect_uri(self, provider: str) -> str:
        """
        Build OAuth redirect URI for a specific provider.

        Uses FRONTEND_BASE_URL + '/oauth/callback' (frontend) as default.

        Args:
            provider: Provider key (e.g., 'jira', 'slack')

        Returns:
            str: Redirect URI expected by providers (frontend callback)
        """
        # Unified frontend callback; provider can be passed in state if needed by FE
        return f"{self.frontend_base}/oauth/callback"

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
        query_string = urlencode(params, doseq=True)
        return f"{base_url}?{query_string}"

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
    Create session data for OAuth flow. (Stateless signed state used.)

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
    }


# PUBLIC_INTERFACE
def validate_oauth_callback(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate OAuth callback parameters using signed state only.

    Args:
        params: Callback parameters from OAuth provider

    Returns:
        Dict: Validation result with success status and data/error
    """
    # Check for errors
    error_msg = oauth_helper.handle_callback_error(params)
    if error_msg:
        return {"success": False, "error": error_msg}

    state = params.get("state")
    code = params.get("code")
    if not state or not code:
        return {"success": False, "error": "Missing required OAuth parameters"}

    try:
        payload = oauth_helper.verify_state(state)
        return {
            "success": True,
            "code": code,
            "state": state,
            "payload": payload,
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
