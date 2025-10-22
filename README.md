# just-mcp-oauth-proxy-example

Entra ID OAuth Proxy with FastMCP

## Entra ID App registration

> following https://github.com/jlowin/fastmcp/blob/v2.13.0rc2/docs/integrations/azure.mdx

1. [X] [Azure Portal](https://portal.azure.com/) "Microsoft Entra ID" > "App registrations"
2. [X] "New registration"
   - Name: `just-mcp-oauth-proxy-example`
   - Supported account types: "Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)"
   - Redirect URI: `Web` - `http://localhost:6274/oauth/callback`
     (for mcp inspector, adding ngrok or similar later)
3. [X] "Register"
4. [X] "Expose an API": Configure your Application ID URI and define scopes
    - Go to "Expose an API" in the App registration sidebar.
    - Click **Add** (was Add not "Set") next to "Application ID URI" and choose one of:
        - Keep the default `api://<your generated client id>}`
        - note it down for later use as `identifier_uri`
    - Click "Add a scope" and create a scope your app
        - Scope name: `read`
        - Who can consent: Admins and users
        - Admin consent display name: `Read access to just-mcp-oauth-proxy-example`
        - Admin consent description: `Allows read access to just-mcp-oauth-proxy-example`
        - User consent display name: `Read access to just-mcp-oauth-proxy-example`
        - User consent description: `Allows read access to just-mcp-oauth-proxy-example`
        - State: Enabled
        - "Add scope"
        - note down the scope ("read")
5. [X] "Configure Access Token Version": Ensure your app uses access token v2
    - Go to "Manifest" in the App registration sidebar.
    - **Attention**: This shows why so ever the old deprecated Azure AD Graph manifest by default!
    - **Hint**: You can check the with "Entra ID Admin Portal" ! https://entra.microsoft.com/ > "Azure Active Directory" > "App registrations" > select your app > "Manifest" > "Edit manifest" > see the JSON property `accessTokenAcceptedVersion`
7. [X] "Certificates & secrets" > "New client secret"
    - Description: `just-mcp-oauth-proxy-example-secret`
    - Expires: `In 6 months`
    - "Add"
    - Note down the secret value (immediately, won't be shown again)
8. [X] "Overview": Note down the "Application (client) ID" and "Directory (tenant) ID"
    - **Application (client) ID**: A UUID like `835f09b6-0f0f-40cc-85cb-f32c5829a149`
    - **Directory (tenant) ID**: A UUID like `08541b6e-646d-43de-a0eb-834e6713d6d5`
9. Add yourself as owner of the app registration

## Run

Set the required environment variables to use and configure the OAuth proxy with Entra ID.
See `.env` - I inject client id, secret and tenant id from the app registration above using 1password CLI. (`./run.sh main.py`)

Then I test with MCP Inspector. Check if newer version published.

> With connection-type `via proxy`, as I understand fastmcp does not add CORS headers by default.

```
npx @modelcontextprotocol/inspector@0.17.1
```

> works with fastmcp 2.13.0rc2 and MCP Inspector 0.17.1

## Tested with:

### fastmcp 2.13.0rc2

- [X] MCP Inspector 0.17.1 `via proxy` localhost
- [ ] MCP Inspector 0.17.1 `direct` localhost (session-id not found?)
- [ ] ChatGPT Web
    - [X] Adding, list/tools
    - [X] tool call => 401
- [ ] Claude Desktop
- [ ] Claude Web


## update fastmcp dependency

change version in `pyproject.toml`

```
fastmcp==2.13.0rc2
```

then run: `uv sync`