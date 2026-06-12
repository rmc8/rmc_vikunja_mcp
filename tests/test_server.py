"""Unit tests for the Vikunja MCP server tools and client logic.

Every tool function is tested in isolation by mocking the underlying
:class:`vikunja_mcp.client.VikunjaClient`.  The mocked client is injected
via ``get_client`` so no real HTTP requests are made.
"""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from vikunja_mcp.client import VikunjaClient
from vikunja_mcp.models import Comment, Label, Project, Task, User
from vikunja_mcp.server import (
    add_comment_to_task,
    add_label_to_task,
    assign_user_to_task,
    create_label,
    create_project,
    create_task,
    delete_project,
    delete_task,
    get_client,
    get_project,
    get_task,
    get_user_info,
    list_labels,
    list_projects,
    list_task_comments,
    list_tasks,
    list_tasks_global,
    remove_label_from_task,
    search_users,
    unassign_user_from_task,
    update_task,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client_ctx() -> Generator[AsyncMock]:
    """Yield a mocked :class:`VikunjaClient` wired into ``get_client``.

    Usage in tests::

        async def test_something(mock_client_ctx: AsyncMock) -> None:
            mock_client_ctx.some_method.return_value = ...
            result = await some_tool(...)
    """
    mock_client = AsyncMock()
    with patch("vikunja_mcp.server.get_client") as mock_get_client:
        mock_get_client.return_value.__aenter__.return_value = (
            mock_client
        )
        yield mock_client


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------

class TestConfiguration:
    """Tests for server configuration and environment handling."""

    def test_get_client_missing_env(self) -> None:
        """``get_client`` raises ValueError when env vars are absent."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(
                ValueError, match="VIKUNJA_URL and VIKUNJA_TOKEN"
            ),
        ):
            get_client()


# ---------------------------------------------------------------------------
# User tool tests
# ---------------------------------------------------------------------------

class TestUserTools:
    """Tests for user-related MCP tools."""

    @pytest.mark.asyncio
    async def test_get_user_info(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``get_user_info`` returns the authenticated user's profile."""
        mock_data: dict[str, Any] = {
            "id": 42,
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "created": "2026-06-12T08:00:00Z",
            "updated": "2026-06-12T08:30:00Z",
        }
        mock_client_ctx.get_user_info.return_value = (
            User.model_validate(mock_data)
        )

        user = await get_user_info()

        assert user.id == 42
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        mock_client_ctx.get_user_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_users(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``search_users`` delegates to the client and returns results."""
        mock_users = [
            {"id": 42, "username": "testuser", "email": "test@example.com"}
        ]
        mock_client_ctx.search_users.return_value = [
            User.model_validate(u) for u in mock_users
        ]

        users = await search_users(query="test")

        mock_client_ctx.search_users.assert_called_once_with("test")
        assert len(users) == 1
        assert users[0].id == 42
        assert users[0].username == "testuser"


# ---------------------------------------------------------------------------
# Project tool tests
# ---------------------------------------------------------------------------

class TestProjectTools:
    """Tests for project CRUD MCP tools."""

    @pytest.mark.asyncio
    async def test_list_projects(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``list_projects`` returns all visible projects."""
        mock_data = [
            {"id": 1, "title": "Project 1", "description": "Desc 1"},
            {"id": 2, "title": "Project 2", "description": "Desc 2"},
        ]
        mock_client_ctx.list_projects.return_value = [
            Project.model_validate(p) for p in mock_data
        ]

        projects = await list_projects()

        assert len(projects) == 2
        assert projects[0].title == "Project 1"
        assert projects[1].title == "Project 2"

    @pytest.mark.asyncio
    async def test_create_project(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``create_project`` forwards title and description."""
        mock_data = {"id": 1, "title": "New Proj", "description": "Desc"}
        mock_client_ctx.create_project.return_value = (
            Project.model_validate(mock_data)
        )

        project = await create_project(
            title="New Proj", description="Desc"
        )

        mock_client_ctx.create_project.assert_called_once_with(
            "New Proj", "Desc"
        )
        assert project.id == 1
        assert project.title == "New Proj"

    @pytest.mark.asyncio
    async def test_get_project(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``get_project`` fetches a single project by ID."""
        mock_data = {"id": 1, "title": "Proj 1"}
        mock_client_ctx.get_project.return_value = (
            Project.model_validate(mock_data)
        )

        project = await get_project(project_id=1)

        mock_client_ctx.get_project.assert_called_once_with(1)
        assert project.id == 1

    @pytest.mark.asyncio
    async def test_delete_project(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``delete_project`` returns a confirmation message."""
        result = await delete_project(project_id=1)

        mock_client_ctx.delete_project.assert_called_once_with(1)
        assert "Project '1' successfully deleted." in result


# ---------------------------------------------------------------------------
# Task tool tests
# ---------------------------------------------------------------------------

class TestTaskTools:
    """Tests for task CRUD MCP tools."""

    @pytest.mark.asyncio
    async def test_get_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``get_task`` fetches a single task by ID."""
        mock_data = {"id": 10, "title": "Task 10", "project_id": 1}
        mock_client_ctx.get_task.return_value = (
            Task.model_validate(mock_data)
        )

        task = await get_task(task_id=10)

        mock_client_ctx.get_task.assert_called_once_with(10)
        assert task.id == 10
        assert task.title == "Task 10"

    @pytest.mark.asyncio
    async def test_list_tasks(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``list_tasks`` returns tasks for a given project."""
        mock_data = [{"id": 10, "title": "Task 10", "project_id": 1}]
        mock_client_ctx.list_tasks.return_value = [
            Task.model_validate(t) for t in mock_data
        ]

        tasks = await list_tasks(project_id=1)

        mock_client_ctx.list_tasks.assert_called_once_with(1)
        assert len(tasks) == 1
        assert tasks[0].id == 10

    @pytest.mark.asyncio
    async def test_list_tasks_with_null_labels(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``list_tasks`` handles tasks where the API returns ``labels: null``."""
        mock_data = [
            {
                "id": 11,
                "title": "Task with null labels",
                "project_id": 1,
                "labels": None,
            }
        ]
        mock_client_ctx.list_tasks.return_value = [
            Task.model_validate(t) for t in mock_data
        ]

        tasks = await list_tasks(project_id=1)

        assert len(tasks) == 1
        assert tasks[0].id == 11
        assert tasks[0].labels is None

    @pytest.mark.asyncio
    async def test_list_tasks_global(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``list_tasks_global`` supports search and done filters."""
        mock_data = [
            {"id": 1, "title": "Task 1", "project_id": 10, "done": False},
            {"id": 2, "title": "Task 2", "project_id": 20, "done": True},
        ]
        mock_client_ctx.list_tasks_global.return_value = [
            Task.model_validate(t) for t in mock_data
        ]

        tasks = await list_tasks_global(search="Task", done=None)

        mock_client_ctx.list_tasks_global.assert_called_once_with(
            "Task", None
        )
        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].done is True

    @pytest.mark.asyncio
    async def test_create_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``create_task`` forwards all optional fields."""
        mock_data = {
            "id": 10,
            "title": "Task 10",
            "project_id": 1,
            "description": "Desc",
            "due_date": "2026-06-12T12:00:00Z",
            "priority": 2,
        }
        mock_client_ctx.create_task.return_value = (
            Task.model_validate(mock_data)
        )

        task = await create_task(
            project_id=1,
            title="Task 10",
            description="Desc",
            due_date="2026-06-12T12:00:00Z",
            priority=2,
        )

        mock_client_ctx.create_task.assert_called_once_with(
            project_id=1,
            title="Task 10",
            description="Desc",
            due_date="2026-06-12T12:00:00Z",
            priority=2,
        )
        assert task.id == 10
        assert task.due_date == "2026-06-12T12:00:00Z"
        assert task.priority == 2

    @pytest.mark.asyncio
    async def test_update_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``update_task`` passes only supplied fields to the client."""
        mock_data = {"id": 10, "title": "Updated", "project_id": 1}
        mock_client_ctx.update_task.return_value = (
            Task.model_validate(mock_data)
        )

        task = await update_task(task_id=10, title="Updated")

        mock_client_ctx.update_task.assert_called_once_with(
            task_id=10,
            title="Updated",
            description=None,
            done=None,
            project_id=None,
            due_date=None,
            priority=None,
        )
        assert task.title == "Updated"

    @pytest.mark.asyncio
    async def test_delete_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``delete_task`` returns a confirmation message."""
        result = await delete_task(task_id=10)

        mock_client_ctx.delete_task.assert_called_once_with(10)
        assert "Task '10' successfully deleted." in result


# ---------------------------------------------------------------------------
# Client-level integration test (Read-Modify-Write)
# ---------------------------------------------------------------------------

class TestClientUpdateTaskRMW:
    """Verify the Read-Modify-Write merge logic in the client layer."""

    @pytest.mark.asyncio
    async def test_update_task_read_modify_write(self) -> None:
        """``client.update_task`` merges changes and strips read-only fields."""
        mock_task_data: dict[str, Any] = {
            "id": 101,
            "title": "Old Title",
            "description": "Old Desc",
            "done": False,
            "project_id": 1,
            "due_date": None,
            "priority": None,
            "created": "2026-06-12T00:00:00Z",
            "updated": "2026-06-12T00:00:00Z",
        }

        client = VikunjaClient(
            base_url="https://example.com", token="fake_token"
        )

        # Stub internal methods to avoid real HTTP calls.
        client.get_task = AsyncMock(  # type: ignore[method-assign]
            return_value=Task.model_validate(mock_task_data)
        )
        client._request = AsyncMock(  # type: ignore[method-assign]
            return_value={
                "id": 101,
                "title": "New Title",
                "description": "Old Desc",
                "done": True,
                "project_id": 2,
                "due_date": "2026-06-15T12:00:00Z",
                "priority": 3,
                "created": "2026-06-12T00:00:00Z",
                "updated": "2026-06-12T01:00:00Z",
            }
        )

        result = await client.update_task(
            task_id=101,
            title="New Title",
            done=True,
            project_id=2,
            due_date="2026-06-15T12:00:00Z",
            priority=3,
        )

        # 1. Verify the current state was fetched.
        client.get_task.assert_called_once_with(101)

        # 2. Verify the payload merges and strips created/updated.
        expected_body: dict[str, Any] = {
            "title": "New Title",
            "description": "Old Desc",
            "done": True,
            "project_id": 2,
            "due_date": "2026-06-15T12:00:00Z",
            "priority": 3,
        }
        client._request.assert_called_once_with(
            "POST", "tasks/101", json=expected_body
        )

        # 3. Verify the returned model reflects the update.
        assert result.title == "New Title"
        assert result.done is True
        assert result.project_id == 2
        assert result.due_date == "2026-06-15T12:00:00Z"
        assert result.priority == 3

        await client.close()


# ---------------------------------------------------------------------------
# Label tool tests
# ---------------------------------------------------------------------------

class TestLabelTools:
    """Tests for label CRUD and task-label association tools."""

    @pytest.mark.asyncio
    async def test_list_labels(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``list_labels`` returns all user labels."""
        mock_data = [{"id": 1, "title": "Label 1", "color": "#ff0000"}]
        mock_client_ctx.list_labels.return_value = [
            Label.model_validate(lbl) for lbl in mock_data
        ]

        labels = await list_labels()

        mock_client_ctx.list_labels.assert_called_once()
        assert len(labels) == 1
        assert labels[0].title == "Label 1"

    @pytest.mark.asyncio
    async def test_create_label(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``create_label`` forwards title and colour."""
        mock_data = {"id": 1, "title": "Label 1", "color": "#ff0000"}
        mock_client_ctx.create_label.return_value = (
            Label.model_validate(mock_data)
        )

        label = await create_label(title="Label 1", hex_color="ff0000")

        mock_client_ctx.create_label.assert_called_once_with(
            "Label 1", "ff0000"
        )
        assert label.id == 1

    @pytest.mark.asyncio
    async def test_add_label_to_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``add_label_to_task`` attaches a label and confirms."""
        result = await add_label_to_task(task_id=123, label_id=456)

        mock_client_ctx.add_label_to_task.assert_called_once_with(
            123, 456
        )
        assert "Label '456' successfully added" in result

    @pytest.mark.asyncio
    async def test_remove_label_from_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``remove_label_from_task`` detaches a label and confirms."""
        result = await remove_label_from_task(task_id=10, label_id=1)

        mock_client_ctx.remove_label_from_task.assert_called_once_with(
            10, 1
        )
        assert "Label '1' successfully removed" in result


# ---------------------------------------------------------------------------
# Assignee tool tests
# ---------------------------------------------------------------------------

class TestAssigneeTools:
    """Tests for user-assignment MCP tools."""

    @pytest.mark.asyncio
    async def test_assign_user_to_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``assign_user_to_task`` assigns a user and confirms."""
        result = await assign_user_to_task(task_id=123, user_id=789)

        mock_client_ctx.assign_user_to_task.assert_called_once_with(
            123, 789
        )
        assert "User '789' successfully assigned" in result

    @pytest.mark.asyncio
    async def test_unassign_user_from_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``unassign_user_from_task`` removes assignment and confirms."""
        result = await unassign_user_from_task(task_id=10, user_id=42)

        mock_client_ctx.unassign_user_from_task.assert_called_once_with(
            10, 42
        )
        assert "User '42' successfully unassigned" in result


# ---------------------------------------------------------------------------
# Comment tool tests
# ---------------------------------------------------------------------------

class TestCommentTools:
    """Tests for task-comment MCP tools."""

    @pytest.mark.asyncio
    async def test_list_task_comments(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``list_task_comments`` returns comments with author info."""
        mock_user: dict[str, Any] = {
            "id": 42,
            "username": "testuser",
            "email": "test@example.com",
        }
        mock_comments = [
            {
                "id": 5,
                "comment": "Nice task",
                "author": mock_user,
                "created": "2026-06-12T09:00:00Z",
                "updated": "2026-06-12T09:00:00Z",
            }
        ]
        mock_client_ctx.list_task_comments.return_value = [
            Comment.model_validate(c) for c in mock_comments
        ]

        comments = await list_task_comments(task_id=10)

        mock_client_ctx.list_task_comments.assert_called_once_with(10)
        assert len(comments) == 1
        assert comments[0].comment == "Nice task"
        assert comments[0].author.username == "testuser"

    @pytest.mark.asyncio
    async def test_add_comment_to_task(
        self, mock_client_ctx: AsyncMock
    ) -> None:
        """``add_comment_to_task`` posts a comment and returns it."""
        mock_user: dict[str, Any] = {
            "id": 42,
            "username": "testuser",
            "email": "test@example.com",
        }
        mock_data = {
            "id": 6,
            "comment": "Adding a comment",
            "author": mock_user,
        }
        mock_client_ctx.add_comment_to_task.return_value = (
            Comment.model_validate(mock_data)
        )

        comment = await add_comment_to_task(
            task_id=10, comment="Adding a comment"
        )

        mock_client_ctx.add_comment_to_task.assert_called_once_with(
            10, "Adding a comment"
        )
        assert comment.id == 6
        assert comment.comment == "Adding a comment"
