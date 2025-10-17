"""OAuth2 authentication with Microsoft Entra ID using MSAL."""

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import httpx
import msal
from jose import JWTError, jwt
from pydantic import BaseModel

from .config import Config


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""



class TokenInfo(BaseModel):
    """Token information model."""

    access_token: str
    id_token: str
    expires_at: datetime
    user_info: Dict[str, Any]


class EntraIDAuth:
    """OAuth2 authentication handler for Microsoft Entra ID."""

    def __init__(self, config: Config) -> None:
        """Initialize the authentication handler.

        Args:
            config: Configuration object with OAuth settings
        """
        self.config = config
        self.app = msal.PublicClientApplication(
            client_id=config.client_id,
            authority=config.authority,
        )

    def generate_pkce_pair(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge pair.

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(
            "utf-8"
        )
        # Remove padding
        code_verifier = code_verifier.rstrip("=")

        # Generate code challenge
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.rstrip("=")

        return code_verifier, code_challenge

    def get_authorization_url(self, state: str, code_challenge: str) -> str:
        """Get the authorization URL for OAuth2 flow.

        Args:
            state: Random state parameter for security
            code_challenge: PKCE code challenge

        Returns:
            Authorization URL
        """
        auth_url = self.app.get_authorization_request_url(
            scopes=self.config.scopes,
            redirect_uri=self.config.redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )
        return auth_url

    async def exchange_code_for_tokens(
        self, authorization_code: str, code_verifier: str
    ) -> TokenInfo:
        """Exchange authorization code for access tokens.

        Args:
            authorization_code: Authorization code from callback
            code_verifier: PKCE code verifier

        Returns:
            Token information

        Raises:
            AuthenticationError: If token exchange fails
        """
        try:
            result = self.app.acquire_token_by_authorization_code(
                code=authorization_code,
                scopes=self.config.scopes,
                redirect_uri=self.config.redirect_uri,
                code_verifier=code_verifier,
            )

            if "error" in result:
                raise AuthenticationError(
                    f"Token exchange failed: {result.get('error_description', result['error'])}"
                )

            # Extract user information from ID token
            user_info = self._extract_user_info(result.get("id_token_claims", {}))

            # Calculate token expiration
            expires_in = result.get("expires_in", 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            return TokenInfo(
                access_token=result["access_token"],
                id_token=result.get("id_token", ""),
                expires_at=expires_at,
                user_info=user_info,
            )

        except Exception as e:
            raise AuthenticationError(
                f"Failed to exchange code for tokens: {e!s}"
            ) from e

    def _extract_user_info(self, id_token_claims: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from ID token claims.

        Args:
            id_token_claims: Claims from ID token

        Returns:
            User information dictionary
        """
        return {
            "user_id": id_token_claims.get("oid", ""),
            "email": id_token_claims.get(
                "email", id_token_claims.get("preferred_username", "")
            ),
            "name": id_token_claims.get("name", ""),
            "given_name": id_token_claims.get("given_name", ""),
            "family_name": id_token_claims.get("family_name", ""),
            "tenant_id": id_token_claims.get("tid", ""),
        }

    def create_jwt_token(self, user_info: Dict[str, Any]) -> str:
        """Create a JWT token for internal use.

        Args:
            user_info: User information to encode in token

        Returns:
            JWT token string
        """
        payload = {
            "user_info": user_info,
            "exp": datetime.now(timezone.utc)
            + timedelta(seconds=self.config.token_expiry_seconds),
            "iat": datetime.now(timezone.utc),
            "iss": "mcp-oauth-example",
        }

        return jwt.encode(payload, self.config.jwt_secret_key, algorithm="HS256")

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )
            return payload
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {e!s}") from e

    async def validate_access_token(self, access_token: str) -> bool:
        """Validate access token with Microsoft Graph API.

        Args:
            access_token: Access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(
                    "https://graph.microsoft.com/v1.0/me", headers=headers, timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False
