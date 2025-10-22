import os
import uvicorn
from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from fastmcp.server.proxy import ProxyClient
from fastmcp.utilities.logging import get_logger
from starlette.middleware.cors import CORSMiddleware
from base_tools import get_version_info, get_azure_user_info

logger = get_logger(__name__)
    
proxyMcpUrl = os.environ.get("PROXY_MCP_URL", "")

if not proxyMcpUrl:
    logger.error("PROXY_MCP_URL not set; remote proxy not started.")
    exit(1)
else:
    logger.info(f"Using PROXY_MCP_URL: {proxyMcpUrl}")

mcp = FastMCP.as_proxy(
    ProxyClient(proxyMcpUrl),
    name="Jameson",
    auth=AzureProvider() # auth config via env
)

@mcp.tool
def version() -> str:
    return get_version_info()

@mcp.tool
async def get_user_info() -> dict:
    return await get_azure_user_info()

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