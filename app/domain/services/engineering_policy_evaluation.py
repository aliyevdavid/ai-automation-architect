from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import ProjectRequirements, RequirementTraceReference


@dataclass(frozen=True, slots=True)
class EngineeringPolicyFinding:
    """One engineering capability required by an explicit project requirement."""

    code: str
    field_paths: tuple[str, ...]
    message: str

    @property
    def trace_references(self) -> tuple[RequirementTraceReference, ...]:
        """Typed references preserving the finding's field-path sequence."""
        return tuple(RequirementTraceReference(path) for path in self.field_paths)


@dataclass(frozen=True, slots=True)
class EngineeringPolicyEvaluationResult:
    """Immutable result of deterministic engineering policy evaluation."""

    findings: tuple[EngineeringPolicyFinding, ...]

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)


def evaluate_engineering_policies(
    requirements: ProjectRequirements,
) -> EngineeringPolicyEvaluationResult:
    """Derive required engineering capabilities from explicit boolean requirements."""
    policies = (
        (
            requirements.automation.ui_testing,
            EngineeringPolicyFinding(
                code="capability.browser_automation_required",
                field_paths=("automation.ui_testing",),
                message="The automation architecture must support browser-based UI automation.",
            ),
        ),
        (
            requirements.automation.api_testing,
            EngineeringPolicyFinding(
                code="capability.api_automation_required",
                field_paths=("automation.api_testing",),
                message="The automation architecture must support API test automation.",
            ),
        ),
        (
            requirements.automation.integration_testing,
            EngineeringPolicyFinding(
                code="capability.integration_testing_required",
                field_paths=("automation.integration_testing",),
                message="The automation architecture must support integration testing.",
            ),
        ),
        (
            requirements.automation.performance_testing,
            EngineeringPolicyFinding(
                code="capability.performance_testing_required",
                field_paths=("automation.performance_testing",),
                message="The automation architecture must support performance testing.",
            ),
        ),
        (
            requirements.automation.accessibility_testing,
            EngineeringPolicyFinding(
                code="capability.accessibility_testing_required",
                field_paths=("automation.accessibility_testing",),
                message="The automation architecture must support accessibility testing.",
            ),
        ),
        (
            requirements.execution.parallel_execution,
            EngineeringPolicyFinding(
                code="capability.parallel_execution_required",
                field_paths=("execution.parallel_execution",),
                message="The automation architecture must support parallel test execution.",
            ),
        ),
        (
            requirements.delivery.pull_request_validation,
            EngineeringPolicyFinding(
                code="capability.pull_request_validation_required",
                field_paths=("delivery.pull_request_validation",),
                message=(
                    "The automation architecture must support automated pull-request validation."
                ),
            ),
        ),
    )

    return EngineeringPolicyEvaluationResult(
        findings=tuple(finding for enabled, finding in policies if enabled is True)
    )
