from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import RequirementTraceReference


@pytest.mark.parametrize(
    "field_path",
    [
        "automation.api_testing",
        " application.frontend_technology ",
        "constraints.approved_technologies[0]",
        "constraints.prohibited_technologies[1]",
    ],
)
def test_field_path_is_preserved_exactly(field_path: str) -> None:
    assert RequirementTraceReference(field_path).field_path == field_path


def test_trace_reference_is_immutable() -> None:
    reference = RequirementTraceReference("automation.api_testing")

    with pytest.raises(FrozenInstanceError):
        reference.field_path = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("field_path", ["", " ", "\t\n"])
def test_blank_field_path_is_invalid(field_path: str) -> None:
    with pytest.raises(ValueError, match="field_path must not be blank"):
        RequirementTraceReference(field_path)


def test_non_string_field_path_is_invalid() -> None:
    with pytest.raises(TypeError, match="field_path must be a string"):
        RequirementTraceReference(1)  # type: ignore[arg-type]


def test_trace_reference_model_is_framework_independent() -> None:
    assert RequirementTraceReference.__module__ == (
        "app.domain.models.requirement_trace_reference"
    )
