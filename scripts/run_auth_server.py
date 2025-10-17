#!/usr/bin/env python3
"""
Script to run the OAuth authentication server.

This script starts the FastAPI-based OAuth server that handles
the Entra ID authentication flow.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_oauth_example.auth_server import main

if __name__ == "__main__":
    main()
