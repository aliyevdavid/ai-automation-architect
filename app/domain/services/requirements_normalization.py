from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import cast

from app.domain.models import (
    ApplicationProfile,
    ConstraintProfile,
    DeliveryProfile,
    ExecutionRequirements,
    ProjectRequirements,
    RequirementTraceReference,
    TeamProfile,
)


class RequirementNormalizationRule(StrEnum):
    """Deterministic transformation applied to one requirement value."""

    TRIM_SURROUNDING_WHITESPACE = "trim_surrounding_whitespace"
    CASEFOLD_CASE_INSENSITIVE_VALUE = "casefold_case_insensitive_value"
    TRIM_AND_CASEFOLD_CASE_INSENSITIVE_VALUE = (
        "trim_and_casefold_case_insensitive_value"
    )


@dataclass(frozen=True, slots=True)
class RequirementNormalizationChange:
    """Trace of one changed requirement value."""

    field_path: str
    original_value: str
    normalized_value: str
    rule: RequirementNormalizationRule

    @property
    def trace_references(self) -> tuple[RequirementTraceReference, ...]:
        """Typed tuple view of the changed requirement field."""
        return (RequirementTraceReference(self.field_path),)


@dataclass(frozen=True, slots=True)
class RequirementNormalizationResult:
    """Immutable normalized requirements and their ordered change trace."""

    normalized_requirements: ProjectRequirements
    changes: tuple[RequirementNormalizationChange, ...]


def _normalize_string(
    value: str | None,
    *,
    field_path: str,
    case_insensitive: bool,
    changes: list[RequirementNormalizationChange],
) -> str | None:
    if value is None:
        return None

    trimmed_value = value.strip()
    normalized_value = trimmed_value.casefold() if case_insensitive else trimmed_value
    if normalized_value == value:
        return value

    if case_insensitive and trimmed_value != value and normalized_value != trimmed_value:
        rule = RequirementNormalizationRule.TRIM_AND_CASEFOLD_CASE_INSENSITIVE_VALUE
    elif case_insensitive:
        rule = RequirementNormalizationRule.CASEFOLD_CASE_INSENSITIVE_VALUE
    else:
        rule = RequirementNormalizationRule.TRIM_SURROUNDING_WHITESPACE
    changes.append(
        RequirementNormalizationChange(field_path, value, normalized_value, rule)
    )
    return normalized_value


def _normalize_collection(
    values: tuple[str, ...] | None,
    *,
    field_path: str,
    case_insensitive: bool,
    changes: list[RequirementNormalizationChange],
) -> tuple[str, ...] | None:
    if values is None:
        return None
    return tuple(
        cast(
            str,
            _normalize_string(
                value,
                field_path=f"{field_path}[{index}]",
                case_insensitive=case_insensitive,
                changes=changes,
            ),
        )
        for index, value in enumerate(values)
    )


def normalize_project_requirements(
    requirements: ProjectRequirements,
) -> RequirementNormalizationResult:
    """Normalize only deterministic representations with established semantics."""
    if not isinstance(requirements, ProjectRequirements):
        raise TypeError("requirements must be a ProjectRequirements.")

    changes: list[RequirementNormalizationChange] = []
    application = requirements.application
    execution = requirements.execution
    delivery = requirements.delivery
    team = requirements.team
    constraints = requirements.constraints

    normalized_requirements = ProjectRequirements(
        application=ApplicationProfile(
            application_type=application.application_type,
            frontend_technology=_normalize_string(
                application.frontend_technology,
                field_path="application.frontend_technology",
                case_insensitive=True,
                changes=changes,
            ),
            backend_technology=_normalize_string(
                application.backend_technology,
                field_path="application.backend_technology",
                case_insensitive=True,
                changes=changes,
            ),
            architecture_style=application.architecture_style,
        ),
        interfaces=requirements.interfaces,
        automation=requirements.automation,
        execution=ExecutionRequirements(
            expected_test_count=execution.expected_test_count,
            target_execution_minutes=execution.target_execution_minutes,
            parallel_execution=execution.parallel_execution,
            browsers=_normalize_collection(
                execution.browsers,
                field_path="execution.browsers",
                case_insensitive=False,
                changes=changes,
            ),
        ),
        delivery=DeliveryProfile(
            ci_provider=_normalize_string(
                delivery.ci_provider,
                field_path="delivery.ci_provider",
                case_insensitive=True,
                changes=changes,
            ),
            release_frequency=delivery.release_frequency,
            pull_request_validation=delivery.pull_request_validation,
        ),
        team=TeamProfile(
            team_size=team.team_size,
            languages=_normalize_collection(
                team.languages,
                field_path="team.languages",
                case_insensitive=False,
                changes=changes,
            ),
            automation_experience=team.automation_experience,
        ),
        constraints=ConstraintProfile(
            approved_technologies=_normalize_collection(
                constraints.approved_technologies,
                field_path="constraints.approved_technologies",
                case_insensitive=True,
                changes=changes,
            ),
            prohibited_technologies=_normalize_collection(
                constraints.prohibited_technologies,
                field_path="constraints.prohibited_technologies",
                case_insensitive=True,
                changes=changes,
            ),
            compliance_requirements=_normalize_collection(
                constraints.compliance_requirements,
                field_path="constraints.compliance_requirements",
                case_insensitive=False,
                changes=changes,
            ),
        ),
    )
    return RequirementNormalizationResult(normalized_requirements, tuple(changes))
