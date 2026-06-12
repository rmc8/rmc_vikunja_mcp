"""FastMCP server exposing Vikunja task-management operations as MCP tools.

This module wires up :class:`vikunja_mcp.client.VikunjaClient` to the
Model Context Protocol via :pypi:`mcp`.  Each ``@mcp.tool()``-decorated
function maps one-to-one to a Vikunja API operation, providing LLM
assistants with full CRUD access to projects, tasks, labels, comments
and user assignments.

Environment variables:
    VIKUNJA_URL   - Base URL of the Vikunja instance.
    VIKUNJA_TOKEN - API bearer token.
"""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from vikunja_mcp.client import VikunjaClient
from vikunja_mcp.models import Bucket, Comment, Label, Project, SavedFilter, Task, User

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


# ---------------------------------------------------------------------------
# User tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_user_info() -> User:
    """Get the authenticated user's profile from Vikunja.

    Useful for checking connectivity and verifying the API token.
    """
    async with get_client() as client:
        return await client.get_user_info()


@mcp.tool()
async def search_users(query: str) -> list[User]:
    """Search for users in Vikunja by username or email.

    Args:
        query: The search term (username or email fragment).
    """
    async with get_client() as client:
        return await client.search_users(query)


# ---------------------------------------------------------------------------
# Project tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_projects() -> list[Project]:
    """List all projects visible to the authenticated user."""
    async with get_client() as client:
        return await client.list_projects()


@mcp.tool()
async def create_project(
    title: str, description: str | None = None
) -> Project:
    """Create a new project.

    Args:
        title: The title of the project.
        description: Optional project description.
    """
    async with get_client() as client:
        return await client.create_project(title, description)


@mcp.tool()
async def get_project(project_id: int) -> Project:
    """Get project details by project ID.

    Args:
        project_id: The ID of the project.
    """
    async with get_client() as client:
        return await client.get_project(project_id)


@mcp.tool()
async def delete_project(project_id: int) -> str:
    """Delete a project and all of its tasks.

    Args:
        project_id: The ID of the project to delete.
    """
    async with get_client() as client:
        await client.delete_project(project_id)
        return f"Project '{project_id}' successfully deleted."


# ---------------------------------------------------------------------------
# Task tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_task(task_id: int) -> Task:
    """Get task details by task ID.

    Args:
        task_id: The ID of the task.
    """
    async with get_client() as client:
        return await client.get_task(task_id)


@mcp.tool()
async def list_tasks(project_id: int) -> list[Task]:
    """List all tasks within a specific project.

    Args:
        project_id: The ID of the project whose tasks to list.
    """
    async with get_client() as client:
        return await client.list_tasks(project_id)


@mcp.tool()
async def list_tasks_global(
    search: str | None = None, done: bool | None = None
) -> list[Task]:
    """List tasks across all projects with optional filters.

    Both *search* and *done* may be provided simultaneously.

    Args:
        search: Optional free-text search term.
        done: Optional completion-status filter.
    """
    async with get_client() as client:
        return await client.list_tasks_global(search, done)


@mcp.tool()
async def create_task(
    project_id: int,
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: int | None = None,
) -> Task:
    """Create a new task under a specific project.

    The task description field MUST be raw HTML (WYSIWYG format), e.g. using <p>, <br>,
    <h3>, <ul>, <li>. Do NOT use Markdown in the description field.

    Args:
        project_id: The ID of the parent project.
        title: The task title / summary.
        description: Optional detailed description.
            MUST be HTML; Markdown is not allowed.
        due_date: Optional due date in ISO-8601 format.
        priority: Optional priority (higher = more urgent).
    """
    async with get_client() as client:
        return await client.create_task(
            project_id=project_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
        )


@mcp.tool()
async def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    done: bool | None = None,
    project_id: int | None = None,
    due_date: str | None = None,
    priority: int | None = None,
) -> Task:
    """Update fields of an existing task (safe Read-Modify-Write).

    Only the fields you provide will be changed; all others are preserved.
    Setting *project_id* moves the task to a different project.

    The task description field MUST be raw HTML (WYSIWYG format), e.g. using <p>, <br>,
    <h3>, <ul>, <li>. Do NOT use Markdown in the description field.

    Args:
        task_id: The ID of the task to update.
        title: New title (omit to keep current).
        description: New description.
            MUST be HTML; Markdown is not allowed.
        done: New completion status.
        project_id: New parent project ID (moves the task).
        due_date: New due date in ISO-8601 format.
        priority: New priority level.
    """
    async with get_client() as client:
        return await client.update_task(
            task_id=task_id,
            title=title,
            description=description,
            done=done,
            project_id=project_id,
            due_date=due_date,
            priority=priority,
        )


@mcp.tool()
async def delete_task(task_id: int) -> str:
    """Permanently delete a task.

    Args:
        task_id: The ID of the task to delete.
    """
    async with get_client() as client:
        await client.delete_task(task_id)
        return f"Task '{task_id}' successfully deleted."


# ---------------------------------------------------------------------------
# Label tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_labels() -> list[Label]:
    """List all labels owned by the authenticated user."""
    async with get_client() as client:
        return await client.list_labels()


@mcp.tool()
async def create_label(
    title: str, hex_color: str | None = None
) -> Label:
    """Create a new label.

    Args:
        title: The label name.
        hex_color: Optional HEX colour string without '#' (e.g. 'ff0000').
    """
    async with get_client() as client:
        return await client.create_label(title, hex_color)


@mcp.tool()
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
    async with get_client() as client:
        return await client.update_label(
            label_id=label_id,
            title=title,
            description=description,
            hex_color=hex_color,
        )


@mcp.tool()
async def delete_label(label_id: int) -> str:
    """Permanently delete a label.

    Args:
        label_id: The ID of the label to delete.
    """
    async with get_client() as client:
        await client.delete_label(label_id)
        return f"Label '{label_id}' successfully deleted."


@mcp.tool()
async def add_label_to_task(task_id: int, label_id: int) -> str:
    """Attach a label to a task.

    Args:
        task_id: The ID of the task.
        label_id: The ID of the label to attach.
    """
    async with get_client() as client:
        await client.add_label_to_task(task_id, label_id)
        return (
            f"Label '{label_id}' successfully added to task '{task_id}'."
        )


@mcp.tool()
async def remove_label_from_task(
    task_id: int, label_id: int
) -> str:
    """Remove a label from a task.

    Args:
        task_id: The ID of the task.
        label_id: The ID of the label to detach.
    """
    async with get_client() as client:
        await client.remove_label_from_task(task_id, label_id)
        return (
            f"Label '{label_id}' successfully removed "
            f"from task '{task_id}'."
        )


# ---------------------------------------------------------------------------
# Assignee tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def assign_user_to_task(task_id: int, user_id: int) -> str:
    """Assign a user to a task.

    Args:
        task_id: The ID of the task.
        user_id: The ID of the user to assign.
    """
    async with get_client() as client:
        await client.assign_user_to_task(task_id, user_id)
        return (
            f"User '{user_id}' successfully assigned "
            f"to task '{task_id}'."
        )


@mcp.tool()
async def unassign_user_from_task(
    task_id: int, user_id: int
) -> str:
    """Remove a user's assignment from a task.

    Args:
        task_id: The ID of the task.
        user_id: The ID of the user to unassign.
    """
    async with get_client() as client:
        await client.unassign_user_from_task(task_id, user_id)
        return (
            f"User '{user_id}' successfully unassigned "
            f"from task '{task_id}'."
        )


# ---------------------------------------------------------------------------
# Comment tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_task_comments(task_id: int) -> list[Comment]:
    """List all comments on a specific task.

    Args:
        task_id: The ID of the task.
    """
    async with get_client() as client:
        return await client.list_task_comments(task_id)


@mcp.tool()
async def add_comment_to_task(
    task_id: int, comment: str
) -> Comment:
    """Add a comment to a specific task.

    Args:
        task_id: The ID of the task.
        comment: The comment body text.
    """
    async with get_client() as client:
        return await client.add_comment_to_task(task_id, comment)


@mcp.tool()
async def add_task_relation(
    task_id: int, other_task_id: int, relation_kind: str = "subtask"
) -> str:
    """Create a relation (e.g., subtask, blocking) between two tasks.

    Args:
        task_id: The ID of the base task.
        other_task_id: The ID of the target task.
        relation_kind: The relationship type. Defaults to 'subtask'.
            Allowed values: 'subtask', 'parenttask', 'related', 'blocking',
            'blockedby', 'duplicateof', 'duplicates', 'precedes', 'follows',
            'copiedfrom', 'copiedto'.
    """
    async with get_client() as client:
        await client.add_task_relation(task_id, other_task_id, relation_kind)
        return (
            f"Successfully created relation '{relation_kind}' from task "
            f"'{task_id}' to task '{other_task_id}'."
        )


@mcp.tool()
async def remove_task_relation(
    task_id: int, other_task_id: int, relation_kind: str = "subtask"
) -> str:
    """Remove a relation between two tasks.

    Args:
        task_id: The ID of the base task.
        other_task_id: The ID of the target task.
        relation_kind: The relationship type to remove. Defaults to 'subtask'.
    """
    async with get_client() as client:
        await client.remove_task_relation(task_id, other_task_id, relation_kind)
        return (
            f"Successfully removed relation '{relation_kind}' between "
            f"task '{task_id}' and task '{other_task_id}'."
        )


# ---------------------------------------------------------------------------
# Bucket tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_buckets(project_id: int, view_id: int) -> list[Bucket]:
    """List all Kanban buckets (lanes) within a specific project view.

    Args:
        project_id: The ID of the project.
        view_id: The ID of the Kanban view.
    """
    async with get_client() as client:
        return await client.list_buckets(project_id, view_id)


@mcp.tool()
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
    async with get_client() as client:
        return await client.create_bucket(
            project_id=project_id,
            view_id=view_id,
            title=title,
            limit=limit,
            position=position,
        )


@mcp.tool()
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
    async with get_client() as client:
        return await client.update_bucket(
            project_id=project_id,
            view_id=view_id,
            bucket_id=bucket_id,
            title=title,
            limit=limit,
        )


@mcp.tool()
async def delete_bucket(
    project_id: int, view_id: int, bucket_id: int
) -> str:
    """Permanently delete a Kanban bucket (lane).

    Args:
        project_id: The ID of the parent project.
        view_id: The ID of the Kanban view.
        bucket_id: The ID of the bucket to delete.
    """
    async with get_client() as client:
        await client.delete_bucket(project_id, view_id, bucket_id)
        return f"Bucket '{bucket_id}' successfully deleted."


# ---------------------------------------------------------------------------
# Filter tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_filters() -> list[SavedFilter]:
    """List all saved filters (virtual projects)."""
    async with get_client() as client:
        return await client.list_filters()


@mcp.tool()
async def get_filter(filter_id: int) -> SavedFilter:
    """Get details of a single saved filter.

    Args:
        filter_id: The ID of the saved filter.
    """
    async with get_client() as client:
        return await client.get_filter(filter_id)


@mcp.tool()
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
    async with get_client() as client:
        return await client.create_filter(
            title=title,
            filter_query=filter_query,
            description=description,
            is_favorite=is_favorite,
            sort_by=sort_by,
            order_by=order_by,
        )


@mcp.tool()
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
    async with get_client() as client:
        return await client.update_filter(
            filter_id=filter_id,
            title=title,
            filter_query=filter_query,
            description=description,
            is_favorite=is_favorite,
            sort_by=sort_by,
            order_by=order_by,
        )


@mcp.tool()
async def delete_filter(filter_id: int) -> str:
    """Permanently delete a saved filter.

    Args:
        filter_id: The ID of the saved filter to delete.
    """
    async with get_client() as client:
        await client.delete_filter(filter_id)
        return f"Saved filter '{filter_id}' successfully deleted."


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry-point for the ``vikunja-mcp`` CLI command."""
    mcp.run()



if __name__ == "__main__":
    main()

