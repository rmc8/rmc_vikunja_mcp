"""Project and bucket operations for the Vikunja client."""

from typing import Any

from vikunja_mcp.client.base import VikunjaClientBase
from vikunja_mcp.models import Bucket, Project


class ProjectMixin(VikunjaClientBase):
    """Mixin for project and bucket-related endpoints."""

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

    async def list_buckets(self, project_id: int, view_id: int) -> list[Bucket]:
        """List all Kanban buckets within a specific project view.

        Args:
            project_id: Vikunja project ID.
            view_id: Vikunja project view ID.
        """
        data = await self._request(
            "GET", f"projects/{project_id}/views/{view_id}/buckets"
        )
        return [Bucket.model_validate(item) for item in data]

    async def create_bucket(
        self,
        project_id: int,
        view_id: int,
        title: str,
        limit: int | None = None,
        position: float | None = None,
    ) -> Bucket:
        """Create a new Kanban bucket in a project view.

        Args:
            project_id: Parent project ID.
            view_id: Parent project view ID.
            title: Title of the bucket.
            limit: Optional Work In Progress (WIP) limit.
            position: Optional position of the bucket.
        """
        body: dict[str, Any] = {"title": title}
        if limit is not None:
            body["limit"] = limit
        if position is not None:
            body["position"] = position
        data = await self._request(
            "PUT", f"projects/{project_id}/views/{view_id}/buckets", json=body
        )
        return Bucket.model_validate(data)

    async def update_bucket(
        self,
        project_id: int,
        view_id: int,
        bucket_id: int,
        title: str | None = None,
        limit: int | None = None,
    ) -> Bucket:
        """Update an existing Kanban bucket.

        Args:
            project_id: Parent project ID.
            view_id: Parent project view ID.
            bucket_id: ID of the bucket to update.
            title: Optional new title.
            limit: Optional new WIP limit.
        """
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if limit is not None:
            body["limit"] = limit
        data = await self._request(
            "POST",
            f"projects/{project_id}/views/{view_id}/buckets/{bucket_id}",
            json=body,
        )
        return Bucket.model_validate(data)

    async def delete_bucket(
        self, project_id: int, view_id: int, bucket_id: int
    ) -> None:
        """Delete a Kanban bucket.

        Args:
            project_id: Parent project ID.
            view_id: Parent project view ID.
            bucket_id: ID of the bucket to delete.
        """
        await self._request(
            "DELETE",
            f"projects/{project_id}/views/{view_id}/buckets/{bucket_id}",
        )
