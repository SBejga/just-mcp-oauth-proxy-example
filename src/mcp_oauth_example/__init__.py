"""
FastMCP OAuth Proxy Example for Entra ID

This package demonstrates how to integrate Microsoft Entra ID (Azure AD) OAuth2
authentication with FastMCP servers using PKCE flow.
"""

__version__ = "0.1.0"
__author__ = "Example Author"
__email__ = "author@example.com"

from .auth import AuthenticationError, EntraIDAuth
from .config import Config
from .server import create_mcp_server

__all__ = [
    "AuthenticationError",
    "Config",
    "EntraIDAuth",
    "create_mcp_server",
]
