"""OAuth2 authentication server using FastAPI."""

import secrets
import webbrowser
from typing import Dict, Optional
from urllib.parse import urlencode, parse_qs

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from .auth import EntraIDAuth, AuthenticationError
from .config import Config


class AuthServer:
    """OAuth2 authentication server."""
    
    def __init__(self, config: Config) -> None:
        """Initialize the authentication server.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.auth = EntraIDAuth(config)
        self.app = FastAPI(title="MCP OAuth Authentication Server")
        self.sessions: Dict[str, Dict] = {}
        
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with authentication link."""
            return HTMLResponse("""
            <html>
                <head>
                    <title>MCP OAuth Authentication</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                        .container { text-align: center; }
                        .button { 
                            display: inline-block; 
                            padding: 12px 24px; 
                            background-color: #0078d4; 
                            color: white; 
                            text-decoration: none; 
                            border-radius: 4px; 
                            font-size: 16px;
                        }
                        .button:hover { background-color: #106ebe; }
                        .info { 
                            background-color: #f3f2f1; 
                            padding: 20px; 
                            border-radius: 4px; 
                            margin: 20px 0; 
                            text-align: left;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>MCP OAuth Authentication Server</h1>
                        <p>This server demonstrates OAuth2 authentication with Microsoft Entra ID for FastMCP servers.</p>
                        
                        <div class="info">
                            <h3>How it works:</h3>
                            <ol>
                                <li>Click "Authenticate with Entra ID" to start the OAuth flow</li>
                                <li>You'll be redirected to Microsoft's login page</li>
                                <li>After successful authentication, you'll receive a JWT token</li>
                                <li>Use this token to access the protected MCP server</li>
                            </ol>
                        </div>
                        
                        <a href="/auth/login" class="button">Authenticate with Entra ID</a>
                    </div>
                </body>
            </html>
            """)
        
        @self.app.get("/auth/login")
        async def login():
            """Initiate OAuth2 login flow."""
            # Generate PKCE parameters
            code_verifier, code_challenge = self.auth.generate_pkce_pair()
            state = secrets.token_urlsafe(32)
            
            # Store session data
            self.sessions[state] = {
                "code_verifier": code_verifier,
                "code_challenge": code_challenge,
            }
            
            # Get authorization URL
            auth_url = self.auth.get_authorization_url(state, code_challenge)
            
            return RedirectResponse(url=auth_url)
        
        @self.app.get("/auth/callback")
        async def callback(
            code: Optional[str] = Query(None),
            state: Optional[str] = Query(None),
            error: Optional[str] = Query(None),
            error_description: Optional[str] = Query(None),
        ):
            """Handle OAuth2 callback."""
            if error:
                error_msg = error_description or error
                raise HTTPException(
                    status_code=400, 
                    detail=f"Authentication failed: {error_msg}"
                )
            
            if not code or not state:
                raise HTTPException(
                    status_code=400, 
                    detail="Missing authorization code or state parameter"
                )
            
            # Verify state and get session
            session = self.sessions.get(state)
            if not session:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid or expired state parameter"
                )
            
            try:
                # Exchange code for tokens
                token_info = await self.auth.exchange_code_for_tokens(
                    code, session["code_verifier"]
                )
                
                # Create JWT token for our application
                jwt_token = self.auth.create_jwt_token(token_info.user_info)
                
                # Clean up session
                del self.sessions[state]
                
                # Return success page with token
                return HTMLResponse(f"""
                <html>
                    <head>
                        <title>Authentication Successful</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                            .success {{ color: #107c10; }}
                            .token-container {{ 
                                background-color: #f3f2f1; 
                                padding: 20px; 
                                border-radius: 4px; 
                                margin: 20px 0; 
                                word-break: break-all;
                            }}
                            .copy-button {{ 
                                background-color: #0078d4; 
                                color: white; 
                                border: none; 
                                padding: 8px 16px; 
                                border-radius: 4px; 
                                cursor: pointer;
                            }}
                            .user-info {{ 
                                background-color: #e1f5fe; 
                                padding: 15px; 
                                border-radius: 4px; 
                                margin: 20px 0;
                            }}
                        </style>
                    </head>
                    <body>
                        <h1 class="success">✅ Authentication Successful!</h1>
                        
                        <div class="user-info">
                            <h3>User Information:</h3>
                            <p><strong>Name:</strong> {token_info.user_info.get('name', 'N/A')}</p>
                            <p><strong>Email:</strong> {token_info.user_info.get('email', 'N/A')}</p>
                            <p><strong>User ID:</strong> {token_info.user_info.get('user_id', 'N/A')}</p>
                        </div>
                        
                        <h3>Your JWT Token:</h3>
                        <div class="token-container">
                            <div id="token">{jwt_token}</div>
                            <button class="copy-button" onclick="copyToken()">Copy Token</button>
                        </div>
                        
                        <p><strong>Note:</strong> Use this token in the Authorization header as "Bearer [token]" when making requests to the MCP server.</p>
                        <p><strong>Token expires at:</strong> {token_info.expires_at.isoformat()}</p>
                        
                        <script>
                            function copyToken() {{
                                const tokenText = document.getElementById('token').textContent;
                                navigator.clipboard.writeText(tokenText).then(function() {{
                                    alert('Token copied to clipboard!');
                                }});
                            }}
                        </script>
                    </body>
                </html>
                """)
                
            except AuthenticationError as e:
                # Clean up session
                if state in self.sessions:
                    del self.sessions[state]
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy", "service": "mcp-oauth-auth-server"}
    
    def run(self, open_browser: bool = True) -> None:
        """Run the authentication server.
        
        Args:
            open_browser: Whether to open browser automatically
        """
        if open_browser:
            webbrowser.open(f"http://{self.config.server_host}:{self.config.auth_server_port}")
        
        uvicorn.run(
            self.app,
            host=self.config.server_host,
            port=self.config.auth_server_port,
            log_level="info",
        )


def main() -> None:
    """Main entry point for the authentication server."""
    try:
        config = Config.from_env()
        server = AuthServer(config)
        
        print(f"Starting OAuth Authentication Server...")
        print(f"Server URL: {config.auth_server_url}")
        print(f"Redirect URI: {config.redirect_uri}")
        print("Press Ctrl+C to stop")
        
        server.run()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
    except KeyboardInterrupt:
        print("\nShutting down authentication server...")
    except Exception as e:
        print(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()