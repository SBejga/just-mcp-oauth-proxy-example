"""Tests for OAuth authentication functionality."""

import base64
import hashlib
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_oauth_example.auth import EntraIDAuth, AuthenticationError, TokenInfo
from mcp_oauth_example.config import Config


@pytest.fixture
def config():
    """Create a test configuration."""
    return Config(
        tenant_id="test-tenant-123",
        client_id="test-client-456",
        redirect_uri="http://localhost:8000/auth/callback",
        scopes=["openid", "profile", "email"],
        server_host="localhost",
        server_port=8080,
        auth_server_port=8000,
        jwt_secret_key="test-secret-key-for-jwt-signing",
        token_expiry_seconds=3600,
    )


@pytest.fixture
def auth_handler(config):
    """Create an authentication handler."""
    with patch('mcp_oauth_example.auth.msal.PublicClientApplication'):
        return EntraIDAuth(config)


class TestEntraIDAuth:
    """Test OAuth authentication functionality."""
    
    def test_initialization(self, config):
        """Test proper initialization of EntraIDAuth."""
        with patch('mcp_oauth_example.auth.msal.PublicClientApplication') as mock_app:
            auth = EntraIDAuth(config)
            
            mock_app.assert_called_once_with(
                client_id=config.client_id,
                authority=config.authority
            )
            assert auth.config == config
    
    def test_generate_pkce_pair(self, auth_handler):
        """Test PKCE code verifier and challenge generation."""
        code_verifier, code_challenge = auth_handler.generate_pkce_pair()
        
        # Verify code verifier format
        assert isinstance(code_verifier, str)
        assert len(code_verifier) >= 43  # Base64 encoded 32 bytes
        assert '=' not in code_verifier  # Padding should be removed
        
        # Verify code challenge is SHA256 hash of verifier
        expected_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        expected_challenge = base64.urlsafe_b64encode(expected_challenge).decode('utf-8').rstrip('=')
        
        assert code_challenge == expected_challenge
    
    def test_get_authorization_url(self, auth_handler):
        """Test authorization URL generation."""
        mock_app = auth_handler.app
        mock_app.get_authorization_request_url.return_value = "https://login.microsoftonline.com/oauth2/authorize?..."
        
        state = "test-state-123"
        code_challenge = "test-code-challenge"
        
        auth_url = auth_handler.get_authorization_url(state, code_challenge)
        
        mock_app.get_authorization_request_url.assert_called_once_with(
            scopes=auth_handler.config.scopes,
            redirect_uri=auth_handler.config.redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )
        
        assert auth_url == "https://login.microsoftonline.com/oauth2/authorize?..."
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_success(self, auth_handler):
        """Test successful token exchange."""
        # Mock successful MSAL response
        mock_result = {
            "access_token": "test-access-token",
            "id_token": "test-id-token",
            "expires_in": 3600,
            "id_token_claims": {
                "oid": "user-123",
                "email": "user@example.com",
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "tid": "tenant-123"
            }
        }
        
        auth_handler.app.acquire_token_by_authorization_code.return_value = mock_result
        
        token_info = await auth_handler.exchange_code_for_tokens("auth-code", "code-verifier")
        
        assert isinstance(token_info, TokenInfo)
        assert token_info.access_token == "test-access-token"
        assert token_info.id_token == "test-id-token"
        assert token_info.user_info["user_id"] == "user-123"
        assert token_info.user_info["email"] == "user@example.com"
        assert token_info.user_info["name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_failure(self, auth_handler):
        """Test token exchange failure handling."""
        # Mock MSAL error response
        mock_result = {
            "error": "invalid_grant",
            "error_description": "The authorization code is invalid"
        }
        
        auth_handler.app.acquire_token_by_authorization_code.return_value = mock_result
        
        with pytest.raises(AuthenticationError, match="Token exchange failed"):
            await auth_handler.exchange_code_for_tokens("invalid-code", "code-verifier")
    
    def test_extract_user_info(self, auth_handler):
        """Test user info extraction from ID token claims."""
        claims = {
            "oid": "user-123",
            "email": "user@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "tid": "tenant-123"
        }
        
        user_info = auth_handler._extract_user_info(claims)
        
        expected = {
            "user_id": "user-123",
            "email": "user@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "tenant_id": "tenant-123",
        }
        
        assert user_info == expected
    
    def test_extract_user_info_minimal(self, auth_handler):
        """Test user info extraction with minimal claims."""
        claims = {}
        
        user_info = auth_handler._extract_user_info(claims)
        
        expected = {
            "user_id": "",
            "email": "",
            "name": "",
            "given_name": "",
            "family_name": "",
            "tenant_id": "",
        }
        
        assert user_info == expected
    
    def test_create_jwt_token(self, auth_handler):
        """Test JWT token creation."""
        user_info = {
            "user_id": "user-123",
            "email": "user@example.com",
            "name": "Test User"
        }
        
        token = auth_handler.create_jwt_token(user_info)
        
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    def test_verify_jwt_token_success(self, auth_handler):
        """Test JWT token verification success."""
        user_info = {
            "user_id": "user-123",
            "email": "user@example.com",
            "name": "Test User"
        }
        
        token = auth_handler.create_jwt_token(user_info)
        payload = auth_handler.verify_jwt_token(token)
        
        assert payload["user_info"] == user_info
        assert payload["iss"] == "mcp-oauth-example"
    
    def test_verify_jwt_token_invalid(self, auth_handler):
        """Test JWT token verification with invalid token."""
        with pytest.raises(AuthenticationError, match="Invalid token"):
            auth_handler.verify_jwt_token("invalid.jwt.token")
    
    @pytest.mark.asyncio
    async def test_validate_access_token_success(self, auth_handler):
        """Test access token validation success."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_handler.validate_access_token("valid-token")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_access_token_failure(self, auth_handler):
        """Test access token validation failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_handler.validate_access_token("invalid-token")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_access_token_exception(self, auth_handler):
        """Test access token validation with network exception."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Network error"))
            
            result = await auth_handler.validate_access_token("token")
            
            assert result is False