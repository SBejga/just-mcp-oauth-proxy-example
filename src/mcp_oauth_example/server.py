"""Protected FastMCP server with OAuth2 authentication."""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .auth import EntraIDAuth, AuthenticationError
from .config import Config


class UserContext(BaseModel):
    """User context information from JWT token."""
    user_id: str
    email: str
    name: str
    given_name: str
    family_name: str
    tenant_id: str


def create_mcp_server(config: Config) -> FastMCP:
    """Create a protected FastMCP server with OAuth authentication.
    
    Args:
        config: Configuration object
        
    Returns:
        Configured FastMCP server
    """
    # Initialize MCP server
    mcp = FastMCP("Protected MCP Server with Entra ID OAuth")
    
    # Initialize authentication
    auth = EntraIDAuth(config)
    
    # Store for demo data - in production this would be a real database
    user_data: Dict[str, Dict] = {}
    
    def get_current_user(context) -> UserContext:
        """Extract user information from request context."""
        # In a real implementation, this would extract the user from the request headers
        # For this example, we'll simulate it
        auth_header = getattr(context, 'headers', {}).get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            raise AuthenticationError("Missing or invalid authorization header")
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            payload = auth.verify_jwt_token(token)
            user_info = payload['user_info']
            return UserContext(**user_info)
        except Exception as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    @mcp.tool
    def get_user_profile() -> Dict:
        """Get the current user's profile information.
        
        Returns:
            User profile data
        """
        try:
            # This would normally get the user context from the request
            # For demo purposes, we'll return a sample profile
            return {
                "status": "success",
                "message": "This tool requires authentication via OAuth2",
                "note": "In a real implementation, this would return the authenticated user's profile",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sample_data": {
                    "user_id": "sample-user-123",
                    "name": "Sample User",
                    "email": "user@example.com",
                    "tenant": "example-tenant"
                }
            }
        except AuthenticationError as e:
            return {"error": str(e), "status": "authentication_failed"}
    
    @mcp.tool
    def save_user_note(note: str) -> Dict:
        """Save a note for the authenticated user.
        
        Args:
            note: The note content to save
            
        Returns:
            Save operation result
        """
        try:
            # In a real implementation, this would get the user from the request context
            user_id = "sample-user-123"  # This would come from authentication
            
            if user_id not in user_data:
                user_data[user_id] = {"notes": []}
            
            note_entry = {
                "id": len(user_data[user_id]["notes"]) + 1,
                "content": note,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            user_data[user_id]["notes"].append(note_entry)
            
            return {
                "status": "success",
                "message": "Note saved successfully",
                "note_id": note_entry["id"],
                "timestamp": note_entry["timestamp"]
            }
        except AuthenticationError as e:
            return {"error": str(e), "status": "authentication_failed"}
    
    @mcp.tool
    def get_user_notes() -> List[Dict]:
        """Get all notes for the authenticated user.
        
        Returns:
            List of user notes
        """
        try:
            # In a real implementation, this would get the user from the request context
            user_id = "sample-user-123"  # This would come from authentication
            
            if user_id not in user_data:
                return []
            
            return user_data[user_id].get("notes", [])
        except AuthenticationError as e:
            return [{"error": str(e), "status": "authentication_failed"}]
    
    @mcp.tool
    def delete_user_note(note_id: int) -> Dict:
        """Delete a specific note for the authenticated user.
        
        Args:
            note_id: The ID of the note to delete
            
        Returns:
            Delete operation result
        """
        try:
            # In a real implementation, this would get the user from the request context
            user_id = "sample-user-123"  # This would come from authentication
            
            if user_id not in user_data or "notes" not in user_data[user_id]:
                return {"error": "Note not found", "status": "not_found"}
            
            notes = user_data[user_id]["notes"]
            note_index = None
            
            for i, note in enumerate(notes):
                if note["id"] == note_id:
                    note_index = i
                    break
            
            if note_index is None:
                return {"error": "Note not found", "status": "not_found"}
            
            deleted_note = notes.pop(note_index)
            
            return {
                "status": "success",
                "message": "Note deleted successfully",
                "deleted_note": deleted_note
            }
        except AuthenticationError as e:
            return {"error": str(e), "status": "authentication_failed"}
    
    @mcp.tool
    def get_server_info() -> Dict:
        """Get information about the MCP server and authentication status.
        
        Returns:
            Server information
        """
        return {
            "server_name": "Protected MCP Server",
            "version": "0.1.0",
            "authentication": "OAuth2 with Microsoft Entra ID",
            "features": [
                "User profile management",
                "Personal note storage",
                "JWT token authentication",
                "PKCE OAuth2 flow"
            ],
            "endpoints": {
                "auth_server": config.auth_server_url,
                "mcp_server": config.server_url
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @mcp.tool
    def calculate_sum(numbers: List[float]) -> Dict:
        """Calculate the sum of a list of numbers.
        
        This is a simple tool that doesn't require user-specific data
        but is still protected by authentication.
        
        Args:
            numbers: List of numbers to sum
            
        Returns:
            Calculation result
        """
        try:
            total = sum(numbers)
            return {
                "status": "success",
                "input": numbers,
                "result": total,
                "count": len(numbers),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "calculation_failed"
            }
    
    # Add a resource for server documentation
    @mcp.resource("server-docs://readme")
    def get_server_docs():
        """Get server documentation and usage examples."""
        return """
# Protected MCP Server with OAuth2

This server demonstrates OAuth2 authentication with Microsoft Entra ID.

## Available Tools:

1. **get_user_profile()** - Get authenticated user's profile
2. **save_user_note(note: str)** - Save a personal note
3. **get_user_notes()** - Retrieve all personal notes  
4. **delete_user_note(note_id: int)** - Delete a specific note
5. **get_server_info()** - Get server information
6. **calculate_sum(numbers: List[float])** - Calculate sum of numbers

## Authentication:

All tools require a valid JWT token obtained through the OAuth2 flow.
Include the token in the Authorization header: `Bearer <your-token>`

## Usage Example:

1. Visit the auth server to get a token
2. Use the token to authenticate API calls
3. Access protected tools and resources
        """
    
    return mcp


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        config = Config.from_env()
        mcp = create_mcp_server(config)
        
        print(f"Starting Protected MCP Server...")
        print(f"Server URL: {config.server_url}")
        print(f"Authentication required via: {config.auth_server_url}")
        print("Press Ctrl+C to stop")
        
        # Run the server
        mcp.run(
            host=config.server_host,
            port=config.server_port,
        )
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
    except Exception as e:
        print(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()