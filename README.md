# FastMCP OAuth Proxy Example with Microsoft Entra ID

This project demonstrates how to integrate Microsoft Entra ID (formerly Azure AD) OAuth2 authentication with FastMCP (Model Context Protocol) servers. It provides a complete example of securing MCP servers using OAuth2 + PKCE (Proof Key for Code Exchange) flow.

## 🎯 What This Example Shows

- **OAuth2 Authentication Flow** with Microsoft Entra ID
- **PKCE (Proof Key for Code Exchange)** for secure public clients
- **FastMCP Server** with protected tools and resources
- **JWT Token Management** for session handling
- **Interactive Client Example** demonstrating the complete flow

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│  Auth Server     │───▶│   Entra ID      │
│                 │    │  (FastAPI)       │    │   (OAuth2)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │ JWT Token             │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│ Protected MCP   │    │   User Data      │
│ Server (FastMCP)│    │   & Resources    │
└─────────────────┘    └──────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Microsoft Azure account with admin access
- Azure AD tenant

### 2. Azure AD Setup

1. **Register an Application**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to Azure Active Directory > App registrations
   - Click "New registration"
   - Set name: "MCP OAuth Example"
   - Select "Accounts in this organizational directory only"
   - Click "Register"

2. **Configure Authentication**:
   - Go to Authentication > Add a platform > Web
   - Set Redirect URI: `http://localhost:8000/auth/callback`
   - Enable "Access tokens" and "ID tokens"
   - Under "Advanced settings", set "Allow public client flows" to "Yes"

3. **Get Required Information**:
   - Copy the **Application (client) ID**
   - Copy the **Directory (tenant) ID**

### 3. Project Setup

1. **Clone and Install**:
   ```bash
   git clone <repository-url>
   cd just-mcp-oauth-proxy-example
   pip install -e .
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Azure AD details:
   ```env
   AUTH_TENANT_ID=your-tenant-id-here
   AUTH_CLIENT_ID=your-client-id-here
   AUTH_REDIRECT_URI=http://localhost:8000/auth/callback
   ```

### 4. Run the Example

**Terminal 1** - Start the OAuth Authentication Server:
```bash
python scripts/run_auth_server.py
```

**Terminal 2** - Start the Protected MCP Server:
```bash
python scripts/run_mcp_server.py
```

**Terminal 3** - Run the Interactive Client Example:
```bash
python examples/oauth_client_example.py
```

## 🔧 Components

### OAuth Authentication Server (`auth_server.py`)

A FastAPI-based server that handles the OAuth2 flow:
- **`/auth/login`** - Initiates OAuth flow
- **`/auth/callback`** - Handles OAuth callback
- **`/`** - User-friendly landing page

### Protected MCP Server (`server.py`)

A FastMCP server with OAuth-protected tools:
- **`get_user_profile()`** - Get authenticated user info
- **`save_user_note(note)`** - Save personal notes
- **`get_user_notes()`** - Retrieve user's notes
- **`delete_user_note(id)`** - Delete a specific note
- **`calculate_sum(numbers)`** - Simple calculator tool
- **`get_server_info()`** - Server status and info

### OAuth Client (`oauth_client_example.py`)

Interactive example showing how to:
1. Authenticate with Entra ID
2. Receive and store JWT tokens
3. Make authenticated calls to MCP server

## 🔐 Security Features

- **PKCE Flow** - Secure OAuth2 for public clients
- **JWT Tokens** - Stateless authentication
- **Token Validation** - Proper expiry and signature checks
- **User Context** - Per-user data isolation

## 📝 Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `AUTH_TENANT_ID` | Azure AD Tenant ID | **Required** |
| `AUTH_CLIENT_ID` | Azure AD Application ID | **Required** |
| `AUTH_REDIRECT_URI` | OAuth redirect URI | `http://localhost:8000/auth/callback` |
| `AUTH_SCOPES` | OAuth scopes to request | `openid profile email` |
| `SERVER_HOST` | Server host address | `localhost` |
| `SERVER_PORT` | MCP server port | `8080` |
| `AUTH_SERVER_PORT` | Auth server port | `8000` |
| `JWT_SECRET_KEY` | JWT signing secret | Auto-generated |
| `TOKEN_EXPIRY_SECONDS` | Token expiration time | `3600` |

## 🧪 Testing

Run the test suite:
```bash
pip install -e ".[dev]"
pytest
```

## 📚 API Reference

### Authentication Flow

1. **Start OAuth Flow**:
   ```
   GET /auth/login
   ```

2. **Handle Callback**:
   ```
   GET /auth/callback?code=...&state=...
   ```

3. **Use JWT Token**:
   ```
   Authorization: Bearer <jwt-token>
   ```

### MCP Tools

All tools require authentication via JWT token in the Authorization header.

#### Get User Profile
```python
mcp.call_tool("get_user_profile")
```

#### Save User Note
```python
mcp.call_tool("save_user_note", {"note": "My note content"})
```

#### Get User Notes
```python
mcp.call_tool("get_user_notes")
```

## 🛠️ Development

### Project Structure
```
├── src/mcp_oauth_example/
│   ├── __init__.py          # Package initialization
│   ├── auth.py              # OAuth & JWT handling
│   ├── auth_server.py       # FastAPI OAuth server
│   ├── config.py            # Configuration management
│   └── server.py            # Protected MCP server
├── examples/
│   └── oauth_client_example.py  # Interactive client demo
├── scripts/
│   ├── run_auth_server.py   # Start OAuth server
│   └── run_mcp_server.py    # Start MCP server
├── tests/                   # Test suite
├── .env.example            # Environment template
└── pyproject.toml          # Project configuration
```

### Adding Custom Tools

To add your own OAuth-protected MCP tools:

```python
from mcp_oauth_example import create_mcp_server, Config

config = Config.from_env()
mcp = create_mcp_server(config)

@mcp.tool
def my_custom_tool(param1: str, param2: int) -> dict:
    """My custom authenticated tool."""
    # Tool implementation here
    return {"result": "success"}
```

## 🔍 Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**
   - Ensure the redirect URI in Azure AD exactly matches your `.env` file
   - URI must be exactly: `http://localhost:8000/auth/callback`

2. **"Token verification failed"**
   - Check that your tenant ID and client ID are correct
   - Ensure the JWT secret key is consistent between server restarts

3. **"Connection refused"**
   - Make sure both auth server and MCP server are running
   - Check that ports 8000 and 8080 are not in use by other applications

### Debug Mode

Enable debug logging:
```bash
export PYTHONPATH="src:$PYTHONPATH"
export LOG_LEVEL="DEBUG"
python scripts/run_auth_server.py
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 🔗 Resources

- [FastMCP Documentation](https://fastmcp.wiki)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [OAuth 2.0 PKCE](https://tools.ietf.org/html/rfc7636)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

**Made with ❤️ for the MCP community**