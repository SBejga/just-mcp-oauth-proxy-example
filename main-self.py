from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from base_tools import get_version_info, get_azure_user_info, get_jameson_icon

 # auth config via env
mcp = FastMCP(name="Jameson", auth=AzureProvider(), icons=[get_jameson_icon()])

@mcp.tool
def version() -> str:
    return get_version_info()

@mcp.tool
async def get_user_info() -> dict:
    return await get_azure_user_info()

if __name__ == "__main__":
    mcp.run(transport="http", port=4242)