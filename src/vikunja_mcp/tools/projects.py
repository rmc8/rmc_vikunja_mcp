"""Project and bucket-related MCP tools."""

from vikunja_mcp import server
from vikunja_mcp.models import Bucket, Project


@server.mcp.tool()
async def list_projects() -> list[Project]:
    """List all projects visible to the authenticated user."""
    async with server.get_client() as client:
        return await client.list_projects()


@server.mcp.tool()
async def create_project(
    title: str, description: str | None = None
) -> Project:
    """Create a new project.

    Args:
        title: The title of the project.
        description: Optional project description.
    """
    async with server.get_client() as client:
        return await client.create_project(title, description)


@server.mcp.tool()
async def get_project(project_id: int) -> Project:
    """Get project details by project ID.

    Args:
        project_id: The ID of the project.
    """
    async with server.get_client() as client:
        return await client.get_project(project_id)


@server.mcp.tool()
async def delete_project(project_id: int) -> str:
    """Delete a project and all of its tasks.

    Args:
        project_id: The ID of the project to delete.
    """
    async with server.get_client() as client:
        await client.delete_project(project_id)
        return f"Project '{project_id}' successfully deleted."


@server.mcp.tool()
async def list_buckets(project_id: int, view_id: int) -> list[Bucket]:
    """List all Kanban buckets (lanes) within a specific project view.

    Args:
        project_id: The ID of the project.
        view_id: The ID of the Kanban view.
    """
    async with server.get_client() as client:
        return await client.list_buckets(project_id, view_id)


@server.mcp.tool()
async def create_bucket(
    project_id: int,
    view_id: int,
    title: str,
    limit: int | None = None,
    position: float | None = None,
) -> Bucket:
    """Create a new Kanban bucket (lane) in a project view.

    Args:
        project_id: The ID of the parent project.
        view_id: The ID of the Kanban view.
        title: The title of the bucket.
        limit: Optional Work In Progress (WIP) limit.
        position: Optional position of the bucket in the view.
    """
    async with server.get_client() as client:
        return await client.create_bucket(
            project_id=project_id,
            view_id=view_id,
            title=title,
            limit=limit,
            position=position,
        )


@server.mcp.tool()
async def update_bucket(
    project_id: int,
    view_id: int,
    bucket_id: int,
    title: str | None = None,
    limit: int | None = None,
) -> Bucket:
    """Update properties of an existing Kanban bucket (lane).

    Args:
        project_id: The ID of the parent project.
        view_id: The ID of the Kanban view.
        bucket_id: The ID of the bucket to update.
        title: Optional new title.
        limit: Optional new WIP limit.
    """
    async with server.get_client() as client:
        return await client.update_bucket(
            project_id=project_id,
            view_id=view_id,
            bucket_id=bucket_id,
            title=title,
            limit=limit,
        )


@server.mcp.tool()
async def delete_bucket(
    project_id: int, view_id: int, bucket_id: int
) -> str:
    """Permanently delete a Kanban bucket (lane).

    Args:
        project_id: The ID of the parent project.
        view_id: The ID of the Kanban view.
        bucket_id: The ID of the bucket to delete.
    """
    async with server.get_client() as client:
        await client.delete_bucket(project_id, view_id, bucket_id)
        return f"Bucket '{bucket_id}' successfully deleted."
