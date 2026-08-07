"""MCP server skeleton — tools wired in once MCP SDK v2 is finalized in the install path.

Wiring of the nine tools (proxy_list/select/test/test_group, provider_list/
healthcheck/update_url, mode_set, connections_list) will land in the next
commit. This module exists so ``pip install -e .`` and ``mihomo-mcp`` (console
script) both work end-to-end without import errors.
"""
from __future__ import annotations

import sys

from mcp.server import MCPServer

from mihomo_mcp import __version__

mcp = MCPServer("mihomo-mcp")


@mcp.tool()
def version() -> str:
    """Return the mihomo-mcp package version."""
    return __version__


def main() -> None:
    """Run the MCP server over stdio."""
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
