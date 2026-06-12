"""Async HTTP client for the Vikunja REST API (v1).

This module encapsulates every HTTP interaction with the Vikunja server
behind typed async methods.  Each method validates the response through
Pydantic models defined in :mod:`vikunja_mcp.models`.

Usage::

    async with VikunjaClient(base_url, token) as client:
        projects = await client.list_projects()
"""

from typing import Any, Self

import httpx

from vikunja_mcp.models import Comment, Label, Project, Task, User




class VikunjaClient:
    """Async client for the Vikunja REST API.

    Attributes:
        base_url: Resolved API root ending with ``/api/v1``.
        token:    Bearer token used for authentication.
        headers:  Default request headers (auth + content-type).
        client:   Underlying :class:`httpx.AsyncClient` instance.
    """

    base_url: str
    token: str
    headers: dict[str, str]
    client: httpx.AsyncClient

    def __init__(self, base_url: str, token: str) -> None:
        # Normalise the URL: strip trailing slash, ensure /api/v1 suffix.
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/api/v1"):
            self.base_url = f"{base_url}/api/v1"
        else:
            self.base_url = base_url

        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            headers=self.headers, timeout=30.0
        )

    async def close(self) -> None:
        """Close the underlying HTTP transport."""
        await self.client.aclose()

    # -- Context-manager protocol ----------------------------------------

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        await self.close()

    # -- Low-level request helper ----------------------------------------

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Any:
        """Send an HTTP request and return the parsed JSON body.

        Args:
            method: HTTP method (``GET``, ``POST``, ``PUT``, ``DELETE``).
            path:   API path relative to ``/api/v1/`` (leading ``/``
                    is stripped automatically).
            **kwargs: Forwarded to :meth:`httpx.AsyncClient.request`
                      (e.g. ``json=``, ``params=``).

        Returns:
            Parsed JSON (dict or list).  Returns an empty dict for
            ``204 No Content`` responses.

        Raises:
            ValueError: On HTTP 4xx / 5xx errors from the API.
            ConnectionError: When the server is unreachable.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                message = error_detail.get("message", str(e))
            except Exception:
                message = e.response.text or str(e)
            raise ValueError(
                f"Vikunja API Error ({e.response.status_code}): {message}"
            ) from e
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Failed to connect to Vikunja server: {e}"
            ) from e

    # -- User endpoints --------------------------------------------------

    async def get_user_info(self) -> User:
        """Return the authenticated user's profile.

        Useful as a connectivity / auth-token health check.
        """
        data = await self._request("GET", "user")
        return User.model_validate(data)

    async def search_users(self, query: str) -> list[User]:
        """Search for users by username or email fragment.

        Args:
            query: Search term matched against username and email.
        """
        params = {"search": query}
        data = await self._request("GET", "users", params=params)
        return [User.model_validate(item) for item in data]

    # -- Project endpoints -----------------------------------------------

    async def list_projects(self) -> list[Project]:
        """List every project visible to the authenticated user."""
        data = await self._request("GET", "projects")
        return [Project.model_validate(item) for item in data]

    async def create_project(
        self, title: str, description: str | None = None
    ) -> Project:
        """Create a new project.

        Args:
            title:       The project title.
            description: Optional longer description.
        """
        body: dict[str, str] = {"title": title}
        if description is not None:
            body["description"] = description
        data = await self._request("PUT", "projects", json=body)
        return Project.model_validate(data)

    async def get_project(self, project_id: int) -> Project:
        """Fetch a single project by its ID.

        Args:
            project_id: Vikunja project ID.
        """
        data = await self._request("GET", f"projects/{project_id}")
        return Project.model_validate(data)

    async def delete_project(self, project_id: int) -> None:
        """Permanently delete a project and all its tasks.

        Args:
            project_id: Vikunja project ID.
        """
        await self._request("DELETE", f"projects/{project_id}")

    # -- Task endpoints --------------------------------------------------

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
        """Update an existing task using a safe Read-Modify-Write pattern.

        The Vikunja ``POST /tasks/{id}`` endpoint resets any field absent
        from the request body.  To avoid data loss we first GET the current
        state, extract only the scalar fields Vikunja accepts on write,
        merge in caller-supplied overrides, and then POST the result.

        Using an explicit whitelist (rather than a full model dump) prevents
        accidentally sending read-only or nested fields (labels, assignees, …)
        that the API would reject or silently corrupt.

        Setting *project_id* to a different value effectively **moves**
        the task to another project.

        Args:
            task_id:     ID of the task to update.
            title:       New title (``None`` = keep current).
            description: New description.
            done:        New completion status (``False`` is valid and applied).
            project_id:  New parent project (moves the task).
            due_date:    New due date in ISO-8601 format.
            priority:    New priority level.
        """
        # 1. Read current state.
        current = await self.get_task(task_id)

        # 2. Build body from writable scalar fields only (whitelist).
        #    This avoids sending labels/assignees/reactions that the API
        #    would reject or use to overwrite existing associations.
        body: dict[str, Any] = {
            "title": current.title,
            "description": current.description,
            "done": current.done,
            "project_id": current.project_id,
            "due_date": current.due_date,
            "priority": current.priority,
        }

        # 3. Merge caller-supplied overrides.
        #    Note: use explicit sentinel checks so that falsy values like
        #    done=False or priority=0 are still applied.
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if done is not None:          # False must be applied
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

    # -- Label endpoints -------------------------------------------------

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
        """Update an existing label (Read-Modify-Write).

        Fetches the current label state first, then merges in the
        caller-supplied changes before POSTing, so unspecified fields
        are preserved.

        Args:
            label_id:    ID of the label to update.
            title:       New label name (``None`` = keep current).
            description: New description.
            hex_color:   New HEX colour without '#' (e.g. ``'ff0000'``).
        """
        # 1. Read current state.
        current_data = await self._request("GET", f"labels/{label_id}")
        current = Label.model_validate(current_data)

        # 2. Build body, preserving existing values for unspecified fields.
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
