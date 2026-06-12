"""Task, comment, assignee and relation operations for the Vikunja client."""

from typing import Any

from vikunja_mcp.client.base import VikunjaClientBase
from vikunja_mcp.models import Comment, Task


class TaskMixin(VikunjaClientBase):
    """Mixin for task-related endpoints."""

    async def get_task(self, task_id: int) -> Task:
        """Fetch a single task by its ID.

        Args:
            task_id: Vikunja task ID.
        """
        data = await self._request("GET", f"tasks/{task_id}")
        return Task.model_validate(data)

    async def list_tasks(self, project_id: int) -> list[Task]:
        """List all tasks belonging to a specific project.

        Args:
            project_id: Vikunja project ID.
        """
        data = await self._request(
            "GET", f"projects/{project_id}/tasks"
        )
        return [Task.model_validate(item) for item in data]

    async def list_tasks_global(
        self,
        search: str | None = None,
        done: bool | None = None,
    ) -> list[Task]:
        """List tasks across all projects with optional filtering.

        Both *search* and *done* may be supplied at the same time.

        Args:
            search: Free-text search term.
            done:   If given, filter by completion status.
        """
        params: dict[str, Any] = {}
        if search is not None:
            params["s"] = search
        if done is not None:
            params["filter"] = f"done = {str(done).lower()}"

        data = await self._request("GET", "tasks/all", params=params)
        return [Task.model_validate(item) for item in data]

    async def create_task(
        self,
        project_id: int,
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        priority: int | None = None,
    ) -> Task:
        """Create a new task under *project_id*.

        Args:
            project_id:  Parent project ID.
            title:       Task title / summary.
            description: Optional detailed description.
            due_date:    Optional due date in ISO-8601 format.
            priority:    Optional priority level (higher = more urgent).
        """
        body: dict[str, Any] = {"title": title}
        if description is not None:
            body["description"] = description
        if due_date is not None:
            body["due_date"] = due_date
        if priority is not None:
            body["priority"] = priority
        data = await self._request(
            "PUT", f"projects/{project_id}/tasks", json=body
        )
        return Task.model_validate(data)

    async def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        done: bool | None = None,
        project_id: int | None = None,
        due_date: str | None = None,
        priority: int | None = None,
    ) -> Task:
        """Update an existing task using a safe Read-Modify-Write pattern."""
        current = await self.get_task(task_id)

        body: dict[str, Any] = {
            "title": current.title,
            "description": current.description,
            "done": current.done,
            "project_id": current.project_id,
            "due_date": current.due_date,
            "priority": current.priority,
        }

        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if done is not None:
            body["done"] = done
        if project_id is not None:
            body["project_id"] = project_id
        if due_date is not None:
            body["due_date"] = due_date
        if priority is not None:
            body["priority"] = priority

        data = await self._request("POST", f"tasks/{task_id}", json=body)
        return Task.model_validate(data)

    async def delete_task(self, task_id: int) -> None:
        """Permanently delete a task.

        Args:
            task_id: Vikunja task ID.
        """
        await self._request("DELETE", f"tasks/{task_id}")

    # -- Assignee endpoints ----------------------------------------------

    async def assign_user_to_task(
        self, task_id: int, user_id: int
    ) -> None:
        """Assign *user_id* to *task_id*.

        Args:
            task_id: Vikunja task ID.
            user_id: Vikunja user ID.
        """
        body = {"user_id": user_id}
        await self._request(
            "PUT", f"tasks/{task_id}/assignees", json=body
        )

    async def unassign_user_from_task(
        self, task_id: int, user_id: int
    ) -> None:
        """Remove *user_id* from the assignees of *task_id*.

        Args:
            task_id: Vikunja task ID.
            user_id: Vikunja user ID.
        """
        await self._request(
            "DELETE", f"tasks/{task_id}/assignees/{user_id}"
        )

    # -- Comment endpoints -----------------------------------------------

    async def list_task_comments(
        self, task_id: int
    ) -> list[Comment]:
        """List every comment on *task_id*.

        Args:
            task_id: Vikunja task ID.
        """
        data = await self._request(
            "GET", f"tasks/{task_id}/comments"
        )
        return [Comment.model_validate(item) for item in data]

    async def add_comment_to_task(
        self, task_id: int, comment: str
    ) -> Comment:
        """Post a new comment on *task_id*.

        Args:
            task_id: Vikunja task ID.
            comment: Comment body text.
        """
        body = {"comment": comment}
        data = await self._request(
            "PUT", f"tasks/{task_id}/comments", json=body
        )
        return Comment.model_validate(data)

    # -- Task Relation endpoints -----------------------------------------

    async def add_task_relation(
        self, task_id: int, other_task_id: int, relation_kind: str
    ) -> None:
        """Create a relation between *task_id* and *other_task_id*.

        Args:
            task_id:         ID of the base task.
            other_task_id:   ID of the target task.
            relation_kind:   The kind of relation (e.g., 'subtask', 'blocking').
        """
        body = {
            "other_task_id": other_task_id,
            "relation_kind": relation_kind,
        }
        await self._request(
            "PUT", f"tasks/{task_id}/relations", json=body
        )

    async def remove_task_relation(
        self, task_id: int, other_task_id: int, relation_kind: str
    ) -> None:
        """Remove a relation between *task_id* and *other_task_id*.

        Args:
            task_id:         ID of the base task.
            other_task_id:   ID of the target task.
            relation_kind:   The kind of relation to remove.
        """
        await self._request(
            "DELETE",
            f"tasks/{task_id}/relations/{relation_kind}/{other_task_id}",
        )
