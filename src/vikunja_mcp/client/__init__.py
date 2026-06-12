"""Async HTTP client for the Vikunja REST API (v1)."""

from vikunja_mcp.client.base import VikunjaClientBase
from vikunja_mcp.client.filters import FilterMixin
from vikunja_mcp.client.labels import LabelMixin
from vikunja_mcp.client.projects import ProjectMixin
from vikunja_mcp.client.tasks import TaskMixin
from vikunja_mcp.client.users import UserMixin


class VikunjaClient(
    UserMixin,
    ProjectMixin,
    TaskMixin,
    LabelMixin,
    FilterMixin,
    VikunjaClientBase,
):
    """Async client for the Vikunja REST API.

    Inherits from resource-specific mixins for structured endpoints.
    """


__all__ = ["VikunjaClient"]
