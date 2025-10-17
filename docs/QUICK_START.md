# Quick Start Guide

Get up and running with the FastMCP OAuth Proxy example in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
git clone <repository-url>
cd just-mcp-oauth-proxy-example
pip install -e .
```

### 2. Configure Azure AD

**Create App Registration:**
1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: "MCP OAuth Example"
4. Redirect URI: `http://localhost:8000/auth/callback`
5. Enable "Allow public client flows" = Yes

**Get Credentials:**
- Copy **Application (client) ID**
- Copy **Directory (tenant) ID**

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
AUTH_TENANT_ID=your-tenant-id
AUTH_CLIENT_ID=your-client-id
```

### 4. Run the Example

**Terminal 1** - Start Auth Server:
```bash
python scripts/run_auth_server.py
```

**Terminal 2** - Start MCP Server:
```bash
python scripts/run_mcp_server.py
```

**Terminal 3** - Run Client Demo:
```bash
python examples/oauth_client_example.py
```

## 🎯 What You'll See

1. **Auth Server** opens at http://localhost:8000
2. **Browser** opens automatically for authentication
3. **Login** with your Microsoft account
4. **Token** displayed on success page
5. **Client** uses token to call protected MCP tools

## 🔧 Available Tools

The protected MCP server provides these tools:

- `get_user_profile()` - Get authenticated user info
- `save_user_note(note)` - Save a personal note
- `get_user_notes()` - Get all user notes
- `delete_user_note(id)` - Delete a note
- `calculate_sum(numbers)` - Calculate sum
- `get_server_info()` - Server status

## 📝 Example Usage

After authentication, the client demonstrates:

```python
# Get user profile
await client.call_mcp_tool("get_user_profile")

# Save a note
await client.call_mcp_tool("save_user_note", {"note": "Hello World!"})

# Get all notes
await client.call_mcp_tool("get_user_notes")

# Calculate sum
await client.call_mcp_tool("calculate_sum", {"numbers": [1, 2, 3, 4, 5]})
```

## 🛠️ Development Commands

```bash
# Install dev dependencies
make install-dev

# Format code
make format

# Run tests
make test

# Check environment
make check-env

# Run quality checks
make check-all
```

## ❓ Troubleshooting

**Authentication fails?**
- Check tenant ID and client ID are correct
- Verify redirect URI matches exactly: `http://localhost:8000/auth/callback`
- Ensure "Allow public client flows" is enabled

**Connection refused?**
- Make sure both servers are running
- Check ports 8000 and 8080 are available

**Token invalid?**
- Copy the complete token from the success page
- Don't include extra spaces or line breaks

## 📚 Next Steps

- Read the full [README.md](../README.md)
- Check [Azure Setup Guide](AZURE_SETUP.md) for detailed configuration
- Explore the code in `/src/mcp_oauth_example/`
- Add your own protected MCP tools

## 🤝 Need Help?

- Check the [Issues](https://github.com/SBejga/just-mcp-oauth-proxy-example/issues)
- Read the [FastMCP Documentation](https://fastmcp.wiki)
- Review [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/) docs

Happy coding! 🎉