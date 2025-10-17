"""Configuration management for MCP OAuth Example."""

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration class for OAuth and MCP server settings."""

    # Entra ID OAuth Configuration
    tenant_id: str
    client_id: str
    redirect_uri: str
    scopes: List[str]

    # Server Configuration
    server_host: str
    server_port: int
    auth_server_port: int

    # Security Configuration
    jwt_secret_key: str
    token_expiry_seconds: int

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        # Required environment variables
        tenant_id = os.getenv("AUTH_TENANT_ID")
        client_id = os.getenv("AUTH_CLIENT_ID")

        if not tenant_id:
            raise ValueError("AUTH_TENANT_ID environment variable is required")
        if not client_id:
            raise ValueError("AUTH_CLIENT_ID environment variable is required")

        # Optional configuration with defaults
        redirect_uri = os.getenv(
            "AUTH_REDIRECT_URI", "http://localhost:8000/auth/callback"
        )
        scopes_str = os.getenv("AUTH_SCOPES", "openid,profile,email")
        scopes = [scope.strip() for scope in scopes_str.split(",")]

        server_host = os.getenv("SERVER_HOST", "localhost")
        server_port = int(os.getenv("SERVER_PORT", "8080"))
        auth_server_port = int(os.getenv("AUTH_SERVER_PORT", "8000"))

        jwt_secret_key = os.getenv("JWT_SECRET_KEY", os.urandom(32).hex())
        token_expiry_seconds = int(os.getenv("TOKEN_EXPIRY_SECONDS", "3600"))

        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            server_host=server_host,
            server_port=server_port,
            auth_server_port=auth_server_port,
            jwt_secret_key=jwt_secret_key,
            token_expiry_seconds=token_expiry_seconds,
        )

    @property
    def authority(self) -> str:
        """Get the Entra ID authority URL."""
        return f"https://login.microsoftonline.com/{self.tenant_id}"

    @property
    def server_url(self) -> str:
        """Get the MCP server URL."""
        return f"http://{self.server_host}:{self.server_port}"

    @property
    def auth_server_url(self) -> str:
        """Get the OAuth authentication server URL."""
        return f"http://{self.server_host}:{self.auth_server_port}"
