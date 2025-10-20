from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)

auth_provider = AzureProvider()
mcp = FastMCP(name="Jameson", auth=auth_provider)

@mcp.tool
def relativator(size: float, typ: str) -> str:
    return f"Example response for size={size}, type={typ}"

if __name__ == "__main__":
    mcp.run(transport="http", port=4242)