import toml
import importlib.metadata
from pathlib import Path
from fastmcp.server.dependencies import get_access_token


def get_version_info() -> str:
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


async def get_azure_user_info() -> dict:
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