"""Label-related MCP tools."""

from vikunja_mcp import server
from vikunja_mcp.models import Label


@server.mcp.tool()
async def list_labels() -> list[Label]:
    """List all labels owned by the authenticated user."""
    async with server.get_client() as client:
        return await client.list_labels()


@server.mcp.tool()
async def create_label(
    title: str, hex_color: str | None = None
) -> Label:
    """Create a new label.

    Args:
        title: The label name.
        hex_color: Optional HEX colour string without '#' (e.g. 'ff0000').
    """
    async with server.get_client() as client:
        return await client.create_label(title, hex_color)


@server.mcp.tool()
async def update_label(
    label_id: int,
    title: str | None = None,
    description: str | None = None,
    hex_color: str | None = None,
) -> Label:
    """Update an existing label's name, description, or colour.

    Only the fields you provide will be changed; all others are preserved.

    Args:
        label_id: The ID of the label to update.
        title: New label name (omit to keep current).
        description: New description (omit to keep current).
        hex_color: New HEX colour without '#' (e.g. 'ff0000'; omit to keep current).
    """
    async with server.get_client() as client:
        return await client.update_label(
            label_id=label_id,
            title=title,
            description=description,
            hex_color=hex_color,
        )


@server.mcp.tool()
async def delete_label(label_id: int) -> str:
    """Permanently delete a label.

    Args:
        label_id: The ID of the label to delete.
    """
    async with server.get_client() as client:
        await client.delete_label(label_id)
        return f"Label '{label_id}' successfully deleted."


@server.mcp.tool()
async def add_label_to_task(task_id: int, label_id: int) -> str:
    """Attach a label to a task.

    Args:
        task_id: The ID of the task.
        label_id: The ID of the label to attach.
    """
    async with server.get_client() as client:
        await client.add_label_to_task(task_id, label_id)
        return (
            f"Label '{label_id}' successfully added to task '{task_id}'."
        )


@server.mcp.tool()
async def remove_label_from_task(
    task_id: int, label_id: int
) -> str:
    """Remove a label from a task.

    Args:
        task_id: The ID of the task.
        label_id: The ID of the label to detach.
    """
    async with server.get_client() as client:
        await client.remove_label_from_task(task_id, label_id)
        return (
            f"Label '{label_id}' successfully removed "
            f"from task '{task_id}'."
        )
