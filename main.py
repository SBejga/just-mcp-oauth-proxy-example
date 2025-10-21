from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from fastmcp.server.dependencies import get_access_token
import importlib.metadata
from pathlib import Path
import toml

mcp = FastMCP(name="Jameson", auth=AzureProvider()) # auth config via env

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
    mcp.run(transport="http", port=4242)