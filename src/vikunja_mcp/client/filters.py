"""Filter operations for the Vikunja client."""

from typing import Any

from vikunja_mcp.client.base import VikunjaClientBase
from vikunja_mcp.models import SavedFilter


class FilterMixin(VikunjaClientBase):
    """Mixin for filter-related endpoints."""

    async def list_filters(self) -> list[SavedFilter]:
        """List all saved filters."""
        data = await self._request("GET", "filters")
        return [SavedFilter.model_validate(item) for item in data]

    async def get_filter(self, filter_id: int) -> SavedFilter:
        """Fetch a single saved filter by its ID.

        Args:
            filter_id: Saved filter ID.
        """
        data = await self._request("GET", f"filters/{filter_id}")
        return SavedFilter.model_validate(data)

    async def create_filter(
        self,
        title: str,
        filter_query: str,
        description: str | None = None,
        is_favorite: bool | None = None,
        sort_by: list[str] | None = None,
        order_by: list[str] | None = None,
    ) -> SavedFilter:
        """Create a new saved filter.

        Args:
            title: Title of the saved filter.
            filter_query: The filter query string.
            description: Optional description.
            is_favorite: Optional favorite flag.
            sort_by: Optional fields to sort by.
            order_by: Optional sort order (asc/desc).
        """
        body: dict[str, Any] = {
            "title": title,
            "filters": {
                "filter": filter_query,
            },
        }
        if description is not None:
            body["description"] = description
        if is_favorite is not None:
            body["is_favorite"] = is_favorite
        if sort_by is not None:
            body["filters"]["sort_by"] = sort_by
        if order_by is not None:
            body["filters"]["order_by"] = order_by

        data = await self._request("PUT", "filters", json=body)
        return SavedFilter.model_validate(data)

    async def update_filter(
        self,
        filter_id: int,
        title: str | None = None,
        filter_query: str | None = None,
        description: str | None = None,
        is_favorite: bool | None = None,
        sort_by: list[str] | None = None,
        order_by: list[str] | None = None,
    ) -> SavedFilter:
        """Update an existing saved filter.

        Args:
            filter_id: ID of the filter to update.
            title: Optional new title.
            filter_query: Optional new filter query.
            description: Optional new description.
            is_favorite: Optional new favorite flag.
            sort_by: Optional new fields to sort by.
            order_by: Optional new sort order (asc/desc).
        """
        current = await self.get_filter(filter_id)

        body: dict[str, Any] = {
            "title": title if title is not None else current.title,
            "description": (
                description
                if description is not None
                else current.description
            ),
            "is_favorite": (
                is_favorite
                if is_favorite is not None
                else current.is_favorite
            ),
            "filters": {
                "filter": (
                    filter_query
                    if filter_query is not None
                    else current.filters.filter
                ),
            },
        }

        merged_sort_by = sort_by if sort_by is not None else current.filters.sort_by
        if merged_sort_by is not None:
            body["filters"]["sort_by"] = merged_sort_by

        merged_order_by = order_by if order_by is not None else current.filters.order_by
        if merged_order_by is not None:
            body["filters"]["order_by"] = merged_order_by

        data = await self._request("POST", f"filters/{filter_id}", json=body)
        return SavedFilter.model_validate(data)

    async def delete_filter(self, filter_id: int) -> None:
        """Permanently delete a saved filter.

        Args:
            filter_id: Saved filter ID.
        """
        await self._request("DELETE", f"filters/{filter_id}")
