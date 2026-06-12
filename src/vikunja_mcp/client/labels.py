"""Label operations for the Vikunja client."""

from typing import Any

from vikunja_mcp.client.base import VikunjaClientBase
from vikunja_mcp.models import Label


class LabelMixin(VikunjaClientBase):
    """Mixin for label-related endpoints."""

    async def list_labels(self) -> list[Label]:
        """List every label owned by the authenticated user."""
        data = await self._request("GET", "labels")
        return [Label.model_validate(item) for item in data]

    async def create_label(
        self, title: str, hex_color: str | None = None
    ) -> Label:
        """Create a new label.

        Args:
            title:     Label name.
            hex_color: Optional HEX colour string without '#' (e.g. ``'ff0000'``).
        """
        body: dict[str, str] = {"title": title}
        if hex_color is not None:
            body["hex_color"] = hex_color
        data = await self._request("PUT", "labels", json=body)
        return Label.model_validate(data)

    async def update_label(
        self,
        label_id: int,
        title: str | None = None,
        description: str | None = None,
        hex_color: str | None = None,
    ) -> Label:
        """Update an existing label (Read-Modify-Write)."""
        current_data = await self._request("GET", f"labels/{label_id}")
        current = Label.model_validate(current_data)

        body: dict[str, Any] = {
            "title": title if title is not None else current.title,
            "description": (
                description if description is not None else current.description
            ),
            "hex_color": (
                hex_color if hex_color is not None else current.hex_color
            ),
        }

        data = await self._request("POST", f"labels/{label_id}", json=body)
        return Label.model_validate(data)

    async def delete_label(self, label_id: int) -> None:
        """Permanently delete a label.

        Args:
            label_id: ID of the label to delete.
        """
        await self._request("DELETE", f"labels/{label_id}")

    async def add_label_to_task(
        self, task_id: int, label_id: int
    ) -> None:
        """Attach *label_id* to *task_id*.

        Args:
            task_id:  Vikunja task ID.
            label_id: Vikunja label ID.
        """
        body = {"label_id": label_id}
        await self._request(
            "PUT", f"tasks/{task_id}/labels", json=body
        )

    async def remove_label_from_task(
        self, task_id: int, label_id: int
    ) -> None:
        """Detach *label_id* from *task_id*.

        Args:
            task_id:  Vikunja task ID.
            label_id: Vikunja label ID.
        """
        await self._request(
            "DELETE", f"tasks/{task_id}/labels/{label_id}"
        )
