import toml
import os
import importlib.metadata
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.proxy import ProxyClient
from fastmcp.utilities.logging import get_logger
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn


logger = get_logger(__name__)
    
proxyMcpUrl = os.environ.get("PROXY_MCP_URL", "")

if not proxyMcpUrl:
    logger.error("PROXY_MCP_URL not set; remote proxy not started.")
    exit(1)

mcp = FastMCP.as_proxy(
    ProxyClient(proxyMcpUrl),
    name="Jameson",
    auth=AzureProvider() # auth config via env
)

@mcp.tool
def version() -> str:
    """Reads the version number from the pyproject.toml file."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    version = "0.0.0"
    fastmcp_version = importlib.metadata.version("fastmcp")
    if pyproject_path.exists():
        pyproject_data = toml.load(pyproject_path)
        if "project" in pyproject_data and "version" in pyproject_data["project"]:
            version = pyproject_data["project"]["version"]
    return (
        f"just-mcp-oauth-proxy-example: v{version}\n"
        f"fastmcp: v{fastmcp_version}"
    )

@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated Azure user."""
    token = get_access_token()
    # The AzureProvider stores user data in token claims
    return {
        "azure_id": token.claims.get("sub"), # type: ignore
        "email": token.claims.get("email"), # type: ignore
        "name": token.claims.get("name"), # type: ignore
        "job_title": token.claims.get("job_title"), # type: ignore
        "office_location": token.claims.get("office_location") # type: ignore
    }

if __name__ == "__main__":
    CORS_ALLOW_ORIGINS = os.environ.get("CORS_ALLOW_ORIGINS", "*")
    logger.info(f"CORS_ALLOW_ORIGINS: {CORS_ALLOW_ORIGINS}")
    
    starlette_app = mcp.streamable_http_app()
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=[CORS_ALLOW_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(starlette_app, host="0.0.0.0", port=4242)
    # mcp.run(transport="http", host="0.0.0.0", port=4242)