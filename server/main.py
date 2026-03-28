"""
LOD-MCP Server - Entry Point
Luxembourgish Online Dictionary MCP Server
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.tools import mcp

if __name__ == "__main__":
    mcp.run()
