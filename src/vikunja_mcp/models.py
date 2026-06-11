"""Pydantic models representing Vikunja API resources.

These models define the schema for JSON payloads exchanged with the
Vikunja REST API.  Using ``extra="ignore"`` ensures that unrecognised
fields returned by future API versions are silently discarded rather than
causing validation errors.
"""

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """A Vikunja user account."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    id: int = Field(..., description="Unique user identifier.")
    username: str = Field(..., description="Login username.")
    email: str | None = Field(
        default=None, description="Email address (may be hidden)."
    )
    name: str | None = Field(
        default=None, description="Display name."
    )
    created: str | None = Field(
        default=None, description="ISO-8601 creation timestamp."
    )
    updated: str | None = Field(
        default=None, description="ISO-8601 last-update timestamp."
    )


class Project(BaseModel):
    """A Vikunja project (top-level container for tasks)."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    id: int = Field(..., description="Unique project identifier.")
    title: str = Field(..., description="Human-readable project title.")
    description: str | None = Field(
        default=None, description="Optional project description."
    )
    created: str | None = Field(
        default=None, description="ISO-8601 creation timestamp."
    )
    updated: str | None = Field(
        default=None, description="ISO-8601 last-update timestamp."
    )


class Task(BaseModel):
    """A Vikunja task belonging to a project."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    id: int = Field(..., description="Unique task identifier.")
    title: str = Field(..., description="Task title / summary.")
    description: str | None = Field(
        default=None, description="Detailed task description."
    )
    done: bool = Field(
        default=False, description="Whether the task is completed."
    )
    project_id: int = Field(
        ..., description="ID of the parent project."
    )
    due_date: str | None = Field(
        default=None, description="ISO-8601 due date."
    )
    priority: int | None = Field(
        default=None, description="Priority level (higher = more urgent)."
    )
    created: str | None = Field(
        default=None, description="ISO-8601 creation timestamp."
    )
    updated: str | None = Field(
        default=None, description="ISO-8601 last-update timestamp."
    )


class Label(BaseModel):
    """A label (tag) that can be attached to tasks."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    id: int = Field(..., description="Unique label identifier.")
    title: str = Field(..., description="Label name.")
    description: str | None = Field(
        default=None, description="Optional label description."
    )
    color: str | None = Field(
        default=None, description="HEX colour string, e.g. '#ff0000'."
    )
    created: str | None = Field(
        default=None, description="ISO-8601 creation timestamp."
    )
    updated: str | None = Field(
        default=None, description="ISO-8601 last-update timestamp."
    )


class Comment(BaseModel):
    """A comment left on a task."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    id: int = Field(..., description="Unique comment identifier.")
    comment: str = Field(..., description="Comment body text.")
    author: User = Field(..., description="User who wrote the comment.")
    created: str | None = Field(
        default=None, description="ISO-8601 creation timestamp."
    )
    updated: str | None = Field(
        default=None, description="ISO-8601 last-update timestamp."
    )
