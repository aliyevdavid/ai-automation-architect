from uuid import UUID, uuid4

import pytest

from app.domain.models.project import Project, ProjectStatus


def test_create_project_generates_identifier_and_defaults_to_draft() -> None:
    project = Project.create(name="Enterprise Web Automation")

    assert isinstance(project.project_id, UUID)
    assert project.name == "Enterprise Web Automation"
    assert project.status is ProjectStatus.DRAFT


def test_project_normalizes_surrounding_name_whitespace() -> None:
    project = Project.create(name="  Enterprise Web Automation  ")

    assert project.name == "Enterprise Web Automation"


def test_project_accepts_explicit_identifier_and_status() -> None:
    project_id = uuid4()

    project = Project(
        project_id=project_id,
        name="API Automation Architecture",
        status=ProjectStatus.ACTIVE,
    )

    assert project.project_id == project_id
    assert project.status is ProjectStatus.ACTIVE


@pytest.mark.parametrize("name", ["", " ", "\t", "\n"])
def test_project_rejects_blank_name(name: str) -> None:
    with pytest.raises(ValueError, match="Project name must not be empty"):
        Project.create(name=name)


def test_project_rejects_non_uuid_identifier() -> None:
    with pytest.raises(TypeError, match="project_id must be a UUID"):
        Project(  # type: ignore[arg-type]
            project_id="not-a-uuid",
            name="Invalid Project",
        )


def test_project_rejects_non_string_name() -> None:
    with pytest.raises(TypeError, match="name must be a string"):
        Project(  # type: ignore[arg-type]
            project_id=uuid4(),
            name=123,
        )


def test_project_rejects_invalid_status_type() -> None:
    with pytest.raises(TypeError, match="status must be a ProjectStatus"):
        Project(  # type: ignore[arg-type]
            project_id=uuid4(),
            name="Invalid Status Project",
            status="draft",
        )
