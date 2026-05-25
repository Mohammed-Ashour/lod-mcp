"""LOD-MCP server entry point."""

from server.tools import mcp


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
