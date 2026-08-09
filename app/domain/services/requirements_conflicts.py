from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.models import ProjectRequirements


class ConflictSeverity(StrEnum):
    """Severity assigned to an explicit requirement contradiction."""

    ERROR = "error"


@dataclass(frozen=True, slots=True)
class RequirementConflict:
    """One deterministic contradiction between supplied requirements."""

    code: str
    severity: ConflictSeverity
    field_paths: tuple[str, ...]
    message: str
    conflicting_value: str


@dataclass(frozen=True, slots=True)
class RequirementConflictResult:
    """Immutable result of deterministic requirement conflict analysis."""

    conflicts: tuple[RequirementConflict, ...]

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)


def _comparison_key(value: str) -> str:
    return value.strip().casefold()


def _selected_technology_conflict(
    *,
    value: str | None,
    prohibited_keys: set[str],
    code: str,
    field_path: str,
    label: str,
) -> RequirementConflict | None:
    if value is None or _comparison_key(value) not in prohibited_keys:
        return None

    return RequirementConflict(
        code=code,
        severity=ConflictSeverity.ERROR,
        field_paths=(field_path, "constraints.prohibited_technologies"),
        message=f"The selected {label} '{value}' is prohibited.",
        conflicting_value=value,
    )


def analyze_requirement_conflicts(
    requirements: ProjectRequirements,
) -> RequirementConflictResult:
    """Report only explicit contradictions defined by the requirement conflict policies."""
    approved = requirements.constraints.approved_technologies or ()
    prohibited = requirements.constraints.prohibited_technologies or ()
    prohibited_keys = {_comparison_key(value) for value in prohibited}
    conflicts: list[RequirementConflict] = []

    for value in approved:
        if _comparison_key(value) in prohibited_keys:
            conflicts.append(
                RequirementConflict(
                    code="technology.approved_prohibited_overlap",
                    severity=ConflictSeverity.ERROR,
                    field_paths=(
                        "constraints.approved_technologies",
                        "constraints.prohibited_technologies",
                    ),
                    message=f"Technology '{value}' is simultaneously approved and prohibited.",
                    conflicting_value=value,
                )
            )

    selected_policies = (
        (
            requirements.application.frontend_technology,
            "technology.frontend_prohibited",
            "application.frontend_technology",
            "frontend technology",
        ),
        (
            requirements.application.backend_technology,
            "technology.backend_prohibited",
            "application.backend_technology",
            "backend technology",
        ),
        (
            requirements.delivery.ci_provider,
            "delivery.ci_provider_prohibited",
            "delivery.ci_provider",
            "CI provider",
        ),
    )
    for selected_value, code, field_path, label in selected_policies:
        conflict = _selected_technology_conflict(
            value=selected_value,
            prohibited_keys=prohibited_keys,
            code=code,
            field_path=field_path,
            label=label,
        )
        if conflict is not None:
            conflicts.append(conflict)

    return RequirementConflictResult(conflicts=tuple(conflicts))
