from dataclasses import dataclass
from enum import StrEnum

from app.domain.models import ProjectRequirements, RequirementTraceReference


class RequirementClassificationKind(StrEnum):
    """Whether an explicit requirement is soft or mandatory."""

    PREFERENCE = "preference"
    CONSTRAINT = "constraint"


@dataclass(frozen=True, slots=True)
class RequirementClassification:
    """Classification of one indexed structured requirement value."""

    field_path: str
    value: str
    kind: RequirementClassificationKind

    def __post_init__(self) -> None:
        if not isinstance(self.field_path, str):
            raise TypeError("field_path must be a string.")
        if not self.field_path.strip():
            raise ValueError("field_path must not be blank.")
        if not isinstance(self.value, str):
            raise TypeError("value must be a string.")
        if not self.value.strip():
            raise ValueError("value must not be blank.")
        if not isinstance(self.kind, RequirementClassificationKind):
            raise TypeError("kind must be a RequirementClassificationKind.")

    @property
    def trace_references(self) -> tuple[RequirementTraceReference, ...]:
        return (RequirementTraceReference(self.field_path),)


@dataclass(frozen=True, slots=True)
class RequirementClassificationResult:
    """Ordered classifications derived from explicit structured fields."""

    classifications: tuple[RequirementClassification, ...]


def classify_project_requirements(
    requirements: ProjectRequirements,
) -> RequirementClassificationResult:
    """Classify explicit normalized preferences and constraints in stable order."""
    if not isinstance(requirements, ProjectRequirements):
        raise TypeError("requirements must be a ProjectRequirements.")

    sources = (
        (
            "preferences.preferred_technologies",
            requirements.preferences.preferred_technologies,
            RequirementClassificationKind.PREFERENCE,
        ),
        (
            "constraints.approved_technologies",
            requirements.constraints.approved_technologies,
            RequirementClassificationKind.CONSTRAINT,
        ),
        (
            "constraints.prohibited_technologies",
            requirements.constraints.prohibited_technologies,
            RequirementClassificationKind.CONSTRAINT,
        ),
        (
            "constraints.compliance_requirements",
            requirements.constraints.compliance_requirements,
            RequirementClassificationKind.CONSTRAINT,
        ),
    )
    classifications = tuple(
        RequirementClassification(f"{field_path}[{index}]", value, kind)
        for field_path, values, kind in sources
        for index, value in enumerate(values or ())
    )
    return RequirementClassificationResult(classifications)
