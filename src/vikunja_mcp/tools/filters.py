"""Filter-related MCP tools."""

from vikunja_mcp import server
from vikunja_mcp.models import SavedFilter


@server.mcp.tool()
async def list_filters() -> list[SavedFilter]:
    """List all saved filters (virtual projects)."""
    async with server.get_client() as client:
        return await client.list_filters()


@server.mcp.tool()
async def get_filter(filter_id: int) -> SavedFilter:
    """Get details of a single saved filter.

    Args:
        filter_id: The ID of the saved filter.
    """
    async with server.get_client() as client:
        return await client.get_filter(filter_id)


@server.mcp.tool()
async def create_filter(
    title: str,
    filter_query: str,
    description: str | None = None,
    is_favorite: bool | None = None,
    sort_by: list[str] | None = None,
    order_by: list[str] | None = None,
) -> SavedFilter:
    """Create a new saved filter (virtual project).

    Args:
        title: The title of the saved filter.
        filter_query: The filter query string using Vikunja filter DSL.
        description: Optional description of the filter.
        is_favorite: Whether to mark this filter as a favorite.
        sort_by: Optional list of fields to sort by.
        order_by: Optional list of sorting order corresponding to sort_by (asc/desc).
    """
    async with server.get_client() as client:
        return await client.create_filter(
            title=title,
            filter_query=filter_query,
            description=description,
            is_favorite=is_favorite,
            sort_by=sort_by,
            order_by=order_by,
        )


@server.mcp.tool()
async def update_filter(
    filter_id: int,
    title: str | None = None,
    filter_query: str | None = None,
    description: str | None = None,
    is_favorite: bool | None = None,
    sort_by: list[str] | None = None,
    order_by: list[str] | None = None,
) -> SavedFilter:
    """Update properties of an existing saved filter.

    Args:
        filter_id: The ID of the saved filter to update.
        title: Optional new title.
        filter_query: Optional new filter query string using Vikunja filter DSL.
        description: Optional new description.
        is_favorite: Optional new favorite status.
        sort_by: Optional new list of fields to sort by.
        order_by: Optional new list of sorting order (asc/desc).
    """
    async with server.get_client() as client:
        return await client.update_filter(
            filter_id=filter_id,
            title=title,
            filter_query=filter_query,
            description=description,
            is_favorite=is_favorite,
            sort_by=sort_by,
            order_by=order_by,
        )


@server.mcp.tool()
async def delete_filter(filter_id: int) -> str:
    """Permanently delete a saved filter.

    Args:
        filter_id: The ID of the saved filter to delete.
    """
    async with server.get_client() as client:
        await client.delete_filter(filter_id)
        return f"Saved filter '{filter_id}' successfully deleted."
