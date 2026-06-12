"""FastMCP server exposing Vikunja task-management operations as MCP tools.

Environment variables:
    VIKUNJA_URL   - Base URL of the Vikunja instance.
    VIKUNJA_TOKEN - API bearer token.
"""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from vikunja_mcp.client import VikunjaClient

# Load environment variables from a .env file when present.
load_dotenv()

# Initialise the FastMCP server instance.
mcp = FastMCP("vikunja")


def get_client() -> VikunjaClient:
    """Build a :class:`VikunjaClient` from environment variables.

    Returns:
        A ready-to-use client instance (use as an async context manager).

    Raises:
        ValueError: If ``VIKUNJA_URL`` or ``VIKUNJA_TOKEN`` is missing.
    """
    base_url = os.getenv("VIKUNJA_URL")
    token = os.getenv("VIKUNJA_TOKEN")

    if not base_url or not token:
        raise ValueError(
            "VIKUNJA_URL and VIKUNJA_TOKEN environment variables must be set. "
            "Please configure them in your .env file."
        )
    return VikunjaClient(base_url, token)


# Import all tool modules so FastMCP registers them.
# The absolute import ensures we do not have import cycles.
import vikunja_mcp.tools.filters as _filters  # noqa: E402, F401
import vikunja_mcp.tools.labels as _labels  # noqa: E402, F401
import vikunja_mcp.tools.projects as _projects  # noqa: E402, F401
import vikunja_mcp.tools.tasks as _tasks  # noqa: E402, F401
import vikunja_mcp.tools.users as _users  # noqa: E402, F401

# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry-point for the ``vikunja-mcp`` CLI command."""
    mcp.run()


if __name__ == "__main__":
    main()
