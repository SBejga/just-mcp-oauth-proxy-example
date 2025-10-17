#!/usr/bin/env python3
"""
OAuth Client Example for FastMCP with Entra ID

This example demonstrates how to:
1. Authenticate with Microsoft Entra ID using OAuth2 + PKCE
2. Use the obtained token to interact with a protected MCP server
"""

import asyncio
import json
import sys
import webbrowser
from pathlib import Path

import httpx

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_oauth_example.config import Config
from mcp_oauth_example.auth import EntraIDAuth


class MCPOAuthClient:
    """Client for interacting with OAuth-protected MCP server."""
    
    def __init__(self, config: Config) -> None:
        """Initialize the client.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.auth = EntraIDAuth(config)
        self.token: str = ""
    
    async def authenticate_interactive(self) -> bool:
        """Perform interactive OAuth authentication.
        
        Returns:
            True if authentication successful, False otherwise
        """
        print("🔐 Starting OAuth2 authentication with Microsoft Entra ID...")
        print(f"📱 Opening browser to: {self.config.auth_server_url}")
        
        # Open the auth server in browser
        webbrowser.open(f"{self.config.auth_server_url}")
        
        print("\n📋 Please complete the authentication in your browser.")
        print("After successful authentication, copy the JWT token and paste it here.")
        print("(The token will be displayed on the success page)")
        
        while True:
            try:
                token = input("\nPaste your JWT token here: ").strip()
                
                if not token:
                    continue
                
                # Verify the token
                payload = self.auth.verify_jwt_token(token)
                user_info = payload.get('user_info', {})
                
                print(f"✅ Authentication successful!")
                print(f"👤 Logged in as: {user_info.get('name', 'Unknown')} ({user_info.get('email', 'Unknown')})")
                
                self.token = token
                return True
                
            except Exception as e:
                print(f"❌ Invalid token: {e}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return False
    
    async def call_mcp_tool(self, tool_name: str, params: dict = None) -> dict:
        """Call an MCP tool on the protected server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            Tool response
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate_interactive() first.")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        # Construct MCP-style request
        request_data = {
            "method": f"tools/{tool_name}",
            "params": params or {}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Note: This is a simplified example. In a real MCP implementation,
                # you would use the proper MCP protocol over stdio or HTTP transport
                print(f"🔧 Calling tool: {tool_name}")
                print(f"📤 Request: {json.dumps(request_data, indent=2)}")
                
                # For demonstration, we'll simulate the tool call
                # In reality, you'd send this to the MCP server endpoint
                response = {
                    "status": "simulated",
                    "tool": tool_name,
                    "params": params,
                    "message": "This is a simulated response. In a real implementation, this would call the actual MCP server.",
                    "note": "The authentication token was successfully validated."
                }
                
                print(f"📥 Response: {json.dumps(response, indent=2)}")
                return response
                
            except httpx.RequestError as e:
                print(f"❌ Request failed: {e}")
                return {"error": str(e)}
    
    async def demo_workflow(self) -> None:
        """Demonstrate a complete workflow with the MCP server."""
        print("🚀 Starting MCP OAuth Example Workflow")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not await self.authenticate_interactive():
            print("❌ Authentication failed. Exiting.")
            return
        
        print("\n" + "=" * 50)
        print("🎯 Demonstrating MCP Tool Calls")
        print("=" * 50)
        
        # Step 2: Get server info
        await self.call_mcp_tool("get_server_info")
        
        print("\n" + "-" * 30)
        
        # Step 3: Get user profile
        await self.call_mcp_tool("get_user_profile")
        
        print("\n" + "-" * 30)
        
        # Step 4: Save a note
        await self.call_mcp_tool("save_user_note", {"note": "This is a test note from the OAuth client!"})
        
        print("\n" + "-" * 30)
        
        # Step 5: Get notes
        await self.call_mcp_tool("get_user_notes")
        
        print("\n" + "-" * 30)
        
        # Step 6: Calculate sum
        await self.call_mcp_tool("calculate_sum", {"numbers": [1, 2, 3, 4, 5]})
        
        print("\n" + "=" * 50)
        print("✅ Workflow completed successfully!")
        print("=" * 50)


async def main() -> None:
    """Main function."""
    try:
        # Load configuration
        config = Config.from_env()
        
        print("🏁 MCP OAuth Client Example")
        print("=" * 50)
        print(f"🔗 Auth Server: {config.auth_server_url}")
        print(f"🖥️  MCP Server: {config.server_url}")
        print(f"🏢 Tenant ID: {config.tenant_id}")
        print(f"📱 Client ID: {config.client_id}")
        print("=" * 50)
        
        # Create client and run demo
        client = MCPOAuthClient(config)
        await client.demo_workflow()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Created a .env file (copy from .env.example)")
        print("   2. Set your AUTH_TENANT_ID and AUTH_CLIENT_ID")
        print("   3. Configured the redirect URI in Azure AD")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())