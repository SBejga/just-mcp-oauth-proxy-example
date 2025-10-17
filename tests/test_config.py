"""Tests for configuration management."""

import os
import pytest
from unittest.mock import patch

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_oauth_example.config import Config


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_from_env_with_minimal_config(self):
        """Test config creation with minimal required environment variables."""
        env_vars = {
            "AUTH_TENANT_ID": "test-tenant-123",
            "AUTH_CLIENT_ID": "test-client-456",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            assert config.tenant_id == "test-tenant-123"
            assert config.client_id == "test-client-456"
            assert config.redirect_uri == "http://localhost:8000/auth/callback"
            assert config.scopes == ["openid", "profile", "email"]
            assert config.server_host == "localhost"
            assert config.server_port == 8080
            assert config.auth_server_port == 8000
    
    def test_from_env_with_full_config(self):
        """Test config creation with all environment variables set."""
        env_vars = {
            "AUTH_TENANT_ID": "test-tenant-123",
            "AUTH_CLIENT_ID": "test-client-456",
            "AUTH_REDIRECT_URI": "http://example.com/callback",
            "AUTH_SCOPES": "openid,profile,email,custom",
            "SERVER_HOST": "0.0.0.0",
            "SERVER_PORT": "9090",
            "AUTH_SERVER_PORT": "9000",
            "JWT_SECRET_KEY": "my-secret-key",
            "TOKEN_EXPIRY_SECONDS": "7200",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            assert config.tenant_id == "test-tenant-123"
            assert config.client_id == "test-client-456"
            assert config.redirect_uri == "http://example.com/callback"
            assert config.scopes == ["openid", "profile", "email", "custom"]
            assert config.server_host == "0.0.0.0"
            assert config.server_port == 9090
            assert config.auth_server_port == 9000
            assert config.jwt_secret_key == "my-secret-key"
            assert config.token_expiry_seconds == 7200
    
    def test_from_env_missing_tenant_id(self):
        """Test that missing tenant ID raises ValueError."""
        env_vars = {
            "AUTH_CLIENT_ID": "test-client-456",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="AUTH_TENANT_ID environment variable is required"):
                Config.from_env()
    
    def test_from_env_missing_client_id(self):
        """Test that missing client ID raises ValueError."""
        env_vars = {
            "AUTH_TENANT_ID": "test-tenant-123",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="AUTH_CLIENT_ID environment variable is required"):
                Config.from_env()
    
    def test_authority_property(self):
        """Test authority URL generation."""
        config = Config(
            tenant_id="test-tenant",
            client_id="test-client",
            redirect_uri="http://localhost:8000/callback",
            scopes=["openid"],
            server_host="localhost",
            server_port=8080,
            auth_server_port=8000,
            jwt_secret_key="secret",
            token_expiry_seconds=3600,
        )
        
        assert config.authority == "https://login.microsoftonline.com/test-tenant"
    
    def test_server_url_property(self):
        """Test server URL generation."""
        config = Config(
            tenant_id="test-tenant",
            client_id="test-client",
            redirect_uri="http://localhost:8000/callback",
            scopes=["openid"],
            server_host="example.com",
            server_port=9090,
            auth_server_port=8000,
            jwt_secret_key="secret",
            token_expiry_seconds=3600,
        )
        
        assert config.server_url == "http://example.com:9090"
    
    def test_auth_server_url_property(self):
        """Test auth server URL generation."""
        config = Config(
            tenant_id="test-tenant",
            client_id="test-client",
            redirect_uri="http://localhost:8000/callback",
            scopes=["openid"],
            server_host="example.com",
            server_port=8080,
            auth_server_port=9000,
            jwt_secret_key="secret",
            token_expiry_seconds=3600,
        )
        
        assert config.auth_server_url == "http://example.com:9000"