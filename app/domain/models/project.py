from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4


class ProjectStatus(StrEnum):
    """Lifecycle status for an automation architecture project."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(slots=True)
class Project:
    """Core domain model for an automation architecture project."""

    project_id: UUID
    name: str
    status: ProjectStatus = ProjectStatus.DRAFT

    def __post_init__(self) -> None:
        if not isinstance(self.project_id, UUID):
            raise TypeError("project_id must be a UUID.")

        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")

        if not isinstance(self.status, ProjectStatus):
            raise TypeError("status must be a ProjectStatus.")

        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("Project name must not be empty.")

        self.name = normalized_name

    @classmethod
    def create(cls, *, name: str) -> Project:
        """Create a new project with a generated stable identifier."""
        return cls(
            project_id=uuid4(),
            name=name,
            status=ProjectStatus.DRAFT,
        )
