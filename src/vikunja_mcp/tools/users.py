"""User-related MCP tools."""

from vikunja_mcp import server
from vikunja_mcp.models import User


@server.mcp.tool()
async def get_user_info() -> User:
    """Get the authenticated user's profile from Vikunja.

    Useful for checking connectivity and verifying the API token.
    """
    async with server.get_client() as client:
        return await client.get_user_info()


@server.mcp.tool()
async def search_users(query: str) -> list[User]:
    """Search for users in Vikunja by username or email.

    Args:
        query: The search term (username or email fragment).
    """
    async with server.get_client() as client:
        return await client.search_users(query)
