#!/usr/bin/env python3
"""
Script to run the protected MCP server.

This script starts the FastMCP server that requires OAuth authentication.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_oauth_example.server import main

if __name__ == "__main__":
    main()
