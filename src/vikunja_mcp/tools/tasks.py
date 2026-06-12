"""Task, comments, assignments, and relations MCP tools."""

from vikunja_mcp import server
from vikunja_mcp.models import Comment, Task


@server.mcp.tool()
async def get_task(task_id: int) -> Task:
    """Get task details by task ID.

    Args:
        task_id: The ID of the task.
    """
    async with server.get_client() as client:
        return await client.get_task(task_id)


@server.mcp.tool()
async def list_tasks(project_id: int) -> list[Task]:
    """List all tasks within a specific project.

    Args:
        project_id: The ID of the project whose tasks to list.
    """
    async with server.get_client() as client:
        return await client.list_tasks(project_id)


@server.mcp.tool()
async def list_tasks_global(
    search: str | None = None, done: bool | None = None
) -> list[Task]:
    """List tasks across all projects with optional filters.

    Both *search* and *done* may be provided simultaneously.

    Args:
        search: Optional free-text search term.
        done: Optional completion-status filter.
    """
    async with server.get_client() as client:
        return await client.list_tasks_global(search, done)


@server.mcp.tool()
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
    async with server.get_client() as client:
        return await client.create_task(
            project_id=project_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
        )


@server.mcp.tool()
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
    async with server.get_client() as client:
        return await client.update_task(
            task_id=task_id,
            title=title,
            description=description,
            done=done,
            project_id=project_id,
            due_date=due_date,
            priority=priority,
        )


@server.mcp.tool()
async def delete_task(task_id: int) -> str:
    """Permanently delete a task.

    Args:
        task_id: The ID of the task to delete.
    """
    async with server.get_client() as client:
        await client.delete_task(task_id)
        return f"Task '{task_id}' successfully deleted."


# -- Assignee tools ----------------------------------------------

@server.mcp.tool()
async def assign_user_to_task(task_id: int, user_id: int) -> str:
    """Assign a user to a task.

    Args:
        task_id: The ID of the task.
        user_id: The ID of the user to assign.
    """
    async with server.get_client() as client:
        await client.assign_user_to_task(task_id, user_id)
        return (
            f"User '{user_id}' successfully assigned "
            f"to task '{task_id}'."
        )


@server.mcp.tool()
async def unassign_user_from_task(
    task_id: int, user_id: int
) -> str:
    """Remove a user's assignment from a task.

    Args:
        task_id: The ID of the task.
        user_id: The ID of the user to unassign.
    """
    async with server.get_client() as client:
        await client.unassign_user_from_task(task_id, user_id)
        return (
            f"User '{user_id}' successfully unassigned "
            f"from task '{task_id}'."
        )


# -- Comment tools -----------------------------------------------

@server.mcp.tool()
async def list_task_comments(task_id: int) -> list[Comment]:
    """List all comments on a specific task.

    Args:
        task_id: The ID of the task.
    """
    async with server.get_client() as client:
        return await client.list_task_comments(task_id)


@server.mcp.tool()
async def add_comment_to_task(
    task_id: int, comment: str
) -> Comment:
    """Add a comment to a specific task.

    Args:
        task_id: The ID of the task.
        comment: The comment body text.
    """
    async with server.get_client() as client:
        return await client.add_comment_to_task(task_id, comment)


# -- Task Relation tools -----------------------------------------

@server.mcp.tool()
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
    async with server.get_client() as client:
        await client.add_task_relation(task_id, other_task_id, relation_kind)
        return (
            f"Successfully created relation '{relation_kind}' from task "
            f"'{task_id}' to task '{other_task_id}'."
        )


@server.mcp.tool()
async def remove_task_relation(
    task_id: int, other_task_id: int, relation_kind: str = "subtask"
) -> str:
    """Remove a relation between two tasks.

    Args:
        task_id: The ID of the base task.
        other_task_id: The ID of the target task.
        relation_kind: The relationship type to remove. Defaults to 'subtask'.
    """
    async with server.get_client() as client:
        await client.remove_task_relation(task_id, other_task_id, relation_kind)
        return (
            f"Successfully removed relation '{relation_kind}' between "
            f"task '{task_id}' and task '{other_task_id}'."
        )
