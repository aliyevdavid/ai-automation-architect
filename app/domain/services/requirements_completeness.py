from __future__ import annotations

from dataclasses import dataclass
from operator import attrgetter

from app.domain.models import ProjectRequirements

_BASE_REQUIRED_FIELDS = (
    "application.application_type",
    "application.architecture_style",
    "interfaces.web_ui",
    "interfaces.rest_api",
    "interfaces.graphql",
    "interfaces.database",
    "interfaces.messaging",
    "automation.ui_testing",
    "automation.api_testing",
    "automation.integration_testing",
    "automation.performance_testing",
    "automation.accessibility_testing",
    "execution.expected_test_count",
    "execution.target_execution_minutes",
    "execution.parallel_execution",
    "delivery.ci_provider",
    "delivery.release_frequency",
    "delivery.pull_request_validation",
    "team.team_size",
    "team.languages",
    "team.automation_experience",
    "constraints.approved_technologies",
    "constraints.prohibited_technologies",
    "constraints.compliance_requirements",
)


@dataclass(frozen=True, slots=True)
class RequirementsCompletenessResult:
    """Deterministic completeness score and its missing requirement paths."""

    required_count: int
    satisfied_count: int
    missing_requirements: tuple[str, ...]
    completeness_percentage: float
    is_complete: bool


def analyze_requirements_completeness(
    requirements: ProjectRequirements,
) -> RequirementsCompletenessResult:
    """Evaluate explicitly supplied values against currently applicable requirements."""
    required_fields = list(_BASE_REQUIRED_FIELDS)

    if requirements.interfaces.web_ui is True:
        required_fields.append("application.frontend_technology")

    if any(
        interface is True
        for interface in (
            requirements.interfaces.rest_api,
            requirements.interfaces.graphql,
            requirements.interfaces.database,
            requirements.interfaces.messaging,
        )
    ):
        required_fields.append("application.backend_technology")

    if requirements.automation.ui_testing is True:
        required_fields.append("execution.browsers")

    missing_requirements = tuple(
        field_path
        for field_path in required_fields
        if attrgetter(field_path)(requirements) is None
    )
    required_count = len(required_fields)
    satisfied_count = required_count - len(missing_requirements)

    return RequirementsCompletenessResult(
        required_count=required_count,
        satisfied_count=satisfied_count,
        missing_requirements=missing_requirements,
        completeness_percentage=round(satisfied_count / required_count * 100, 2),
        is_complete=not missing_requirements,
    )
