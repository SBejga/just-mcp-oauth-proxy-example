# Azure AD (Entra ID) Setup Guide

This guide walks you through setting up Microsoft Entra ID (formerly Azure AD) for OAuth2 authentication with your MCP server.

## Prerequisites

- Azure account with administrative privileges
- Access to Azure Portal (portal.azure.com)

## Step-by-Step Setup

### 1. Access Azure Portal

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Sign in with your Azure account
3. Ensure you're in the correct tenant/directory

### 2. Register a New Application

1. **Navigate to Azure Active Directory**:
   - In the Azure Portal, search for "Azure Active Directory" or find it in the left sidebar
   - Click on "Azure Active Directory"

2. **Go to App Registrations**:
   - In the Azure AD overview page, click on "App registrations" in the left menu
   - Click "New registration"

3. **Configure Basic Settings**:
   ```
   Name: MCP OAuth Example
   Supported account types: Accounts in this organizational directory only (Single tenant)
   Redirect URI: Leave blank for now
   ```
   
4. **Click "Register"**

### 3. Configure Authentication

1. **After registration, go to Authentication**:
   - In your app's overview page, click "Authentication" in the left menu
   - Click "Add a platform"
   - Select "Web"

2. **Configure Redirect URIs**:
   ```
   Redirect URIs: http://localhost:8000/auth/callback
   ```
   
   ⚠️ **Important**: The URI must be exactly `http://localhost:8000/auth/callback` to match the default configuration.

3. **Configure Token Settings**:
   - Under "Implicit grant and hybrid flows":
     - ✅ Check "Access tokens (used for implicit flows)"
     - ✅ Check "ID tokens (used for implicit and hybrid flows)"

4. **Enable Public Client Flows**:
   - Scroll down to "Advanced settings"
   - Under "Allow public client flows":
     - ✅ Set "Enable the following mobile and desktop flows" to **Yes**

5. **Click "Save"**

### 4. Collect Required Information

After setting up the application, collect these values:

1. **Application (Client) ID**:
   - Go to "Overview" in your app registration
   - Copy the "Application (client) ID" value
   - This goes in your `.env` file as `AUTH_CLIENT_ID`

2. **Directory (Tenant) ID**:
   - Still in "Overview", copy the "Directory (tenant) ID" value
   - This goes in your `.env` file as `AUTH_TENANT_ID`

### 5. Optional: Configure API Permissions

If you want to access additional Microsoft Graph APIs:

1. **Go to API Permissions**:
   - Click "API permissions" in the left menu
   - By default, you'll see "Microsoft Graph" with "User.Read" permission

2. **Add Additional Permissions** (optional):
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Choose "Delegated permissions"
   - Add permissions like:
     - `profile` - Basic profile information
     - `email` - Email address
     - `openid` - OpenID Connect sign-in
     - `offline_access` - Refresh tokens (if needed)

3. **Grant Admin Consent** (if required):
   - If your organization requires admin consent, click "Grant admin consent for [Your Organization]"

### 6. Configure Your Application

Create your `.env` file with the collected information:

```env
# Required: Copy these from your Azure AD app registration
AUTH_TENANT_ID=your-directory-tenant-id-here
AUTH_CLIENT_ID=your-application-client-id-here

# Default settings (modify if needed)
AUTH_REDIRECT_URI=http://localhost:8000/auth/callback
AUTH_SCOPES=openid,profile,email
SERVER_HOST=localhost
SERVER_PORT=8080
AUTH_SERVER_PORT=8000

# Optional: Custom JWT settings
JWT_SECRET_KEY=your-custom-secret-key-here
TOKEN_EXPIRY_SECONDS=3600
```

## Verification

To verify your setup:

1. **Test Configuration**:
   ```bash
   make check-env
   ```

2. **Start the Auth Server**:
   ```bash
   make run-auth-server
   ```

3. **Visit the Auth Server**:
   - Open http://localhost:8000 in your browser
   - Click "Authenticate with Entra ID"
   - You should be redirected to Microsoft's login page

## Common Issues and Solutions

### Issue: "AADSTS50011: The reply URL specified in the request does not match..."

**Solution**: 
- Ensure the redirect URI in Azure AD exactly matches your `.env` file
- URI must be: `http://localhost:8000/auth/callback`
- Check for extra spaces or typos

### Issue: "AADSTS700016: Application not found in directory"

**Solution**:
- Verify you're using the correct Client ID
- Ensure you're in the right Azure AD tenant
- Check that the application is registered in the same tenant you're trying to authenticate against

### Issue: "invalid_client" error

**Solution**:
- Ensure "Allow public client flows" is enabled in Azure AD
- Verify the Client ID is correct
- Make sure you're using the Public Client Application flow (not Confidential Client)

### Issue: Token verification fails

**Solution**:
- Check that your Tenant ID is correct
- Ensure the JWT secret key is consistent between server restarts
- Verify system clock is synchronized

## Security Considerations

### For Development
- Use `http://localhost` URLs only for development
- Never expose your Client ID in public repositories (use `.env` files)

### For Production
- Use HTTPS redirect URIs only
- Implement proper token storage and rotation
- Consider using Azure Key Vault for secrets
- Enable additional security features like Conditional Access

## Advanced Configuration

### Custom Scopes
If you need access to specific APIs, configure custom scopes:

```env
AUTH_SCOPES=openid,profile,email,https://graph.microsoft.com/User.Read,https://graph.microsoft.com/Mail.Read
```

### Multi-Tenant Applications
For multi-tenant support:

1. In Azure AD, set "Supported account types" to:
   - "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"

2. Use `common` or `organizations` as tenant ID:
   ```env
   AUTH_TENANT_ID=common
   ```

### Custom Token Lifetime
Configure token expiration:

```env
TOKEN_EXPIRY_SECONDS=7200  # 2 hours
```

## Resources

- [Microsoft Identity Platform Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [OAuth 2.0 and PKCE](https://tools.ietf.org/html/rfc7636)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)