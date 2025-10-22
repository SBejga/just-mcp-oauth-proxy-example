from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from base_tools import get_version_info, get_azure_user_info

mcp = FastMCP(name="Jameson", auth=AzureProvider()) # auth config via env

@mcp.tool
def version() -> str:
    return get_version_info()

@mcp.tool
async def get_user_info() -> dict:
    return await get_azure_user_info()

if __name__ == "__main__":
    mcp.run(transport="http", port=4242)