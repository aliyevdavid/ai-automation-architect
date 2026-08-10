from __future__ import annotations

from dataclasses import dataclass

from app.application.requirement_analysis import RequirementAnalysisResult
from app.domain.models import (
    ArchitectureDecision,
    ArchitectureLayer,
    AutomationArchitectureCandidate,
    AutomationCapability,
    DeliveryStrategy,
    ExecutionStrategy,
    RequirementTraceReference,
)


@dataclass(frozen=True, slots=True)
class _PolicyMapping:
    capability_name: str
    capability_purpose: str
    decision: str
    rationale: str
    layer_name: str | None = None
    layer_responsibilities: tuple[str, ...] = ()
    execution_field: str | None = None
    execution_value: str | None = None
    delivery_field: str | None = None
    delivery_value: str | None = None


_POLICY_MAPPINGS = {
    "capability.browser_automation_required": _PolicyMapping(
        capability_name="Browser automation",
        capability_purpose="Support automated validation of browser-based user interfaces.",
        layer_name="Browser automation layer",
        layer_responsibilities=("Execute browser-based user-interface automation.",),
        execution_field="browser_execution",
        execution_value="Support browser-based UI automation execution.",
        decision="Include browser-based UI automation.",
        rationale="Explicit project requirements require browser-based UI automation.",
    ),
    "capability.api_automation_required": _PolicyMapping(
        capability_name="API automation",
        capability_purpose=(
            "Support automated validation of application programming interfaces."
        ),
        layer_name="API automation layer",
        layer_responsibilities=("Execute automated API validation.",),
        decision="Include API test automation.",
        rationale="Explicit project requirements require API test automation.",
    ),
    "capability.integration_testing_required": _PolicyMapping(
        capability_name="Integration testing",
        capability_purpose=(
            "Support automated validation across integrated system boundaries."
        ),
        layer_name="Integration testing layer",
        layer_responsibilities=(
            "Validate interactions across integrated system boundaries.",
        ),
        decision="Include integration testing.",
        rationale="Explicit project requirements require integration testing.",
    ),
    "capability.performance_testing_required": _PolicyMapping(
        capability_name="Performance testing",
        capability_purpose=(
            "Support automated evaluation of system performance characteristics."
        ),
        decision="Include performance testing.",
        rationale="Explicit project requirements require performance testing.",
    ),
    "capability.accessibility_testing_required": _PolicyMapping(
        capability_name="Accessibility testing",
        capability_purpose="Support automated accessibility validation.",
        decision="Include accessibility testing.",
        rationale="Explicit project requirements require accessibility testing.",
    ),
    "capability.parallel_execution_required": _PolicyMapping(
        capability_name="Parallel test execution",
        capability_purpose="Support concurrent automated test execution.",
        execution_field="parallelization",
        execution_value="Support parallel test execution.",
        decision="Support parallel test execution.",
        rationale="Explicit project requirements require parallel test execution.",
    ),
    "capability.pull_request_validation_required": _PolicyMapping(
        capability_name="Pull-request validation",
        capability_purpose=(
            "Support automated validation of code changes before integration."
        ),
        delivery_field="pull_request_validation",
        delivery_value="Run automated validation for pull requests.",
        decision="Include automated pull-request validation.",
        rationale=(
            "Explicit project requirements require automated pull-request validation."
        ),
    ),
}


def generate_automation_architecture_candidate(
    analysis: RequirementAnalysisResult,
) -> AutomationArchitectureCandidate:
    """Generate one deterministic candidate from evaluated engineering policies."""
    layers: list[ArchitectureLayer] = []
    capabilities: list[AutomationCapability] = []
    decisions: list[ArchitectureDecision] = []
    execution_values: dict[str, str] = {}
    execution_references: list[RequirementTraceReference] = []
    delivery_values: dict[str, str] = {}
    delivery_references: list[RequirementTraceReference] = []

    for finding in analysis.engineering_policies.findings:
        try:
            mapping = _POLICY_MAPPINGS[finding.code]
        except KeyError:
            raise ValueError(f"Unsupported engineering-policy code: {finding.code}") from None

        references = finding.trace_references
        capabilities.append(
            AutomationCapability(
                mapping.capability_name,
                mapping.capability_purpose,
                references,
            )
        )
        decisions.append(
            ArchitectureDecision(mapping.decision, mapping.rationale, references)
        )

        if mapping.layer_name is not None:
            layers.append(
                ArchitectureLayer(
                    mapping.layer_name,
                    mapping.layer_responsibilities,
                    references,
                )
            )
        if mapping.execution_field is not None:
            assert mapping.execution_value is not None
            execution_values[mapping.execution_field] = mapping.execution_value
            execution_references.extend(references)
        if mapping.delivery_field is not None:
            assert mapping.delivery_value is not None
            delivery_values[mapping.delivery_field] = mapping.delivery_value
            delivery_references.extend(references)

    return AutomationArchitectureCandidate(
        layers=tuple(layers),
        capabilities=tuple(capabilities),
        execution_strategy=ExecutionStrategy(
            **execution_values,
            requirement_references=tuple(execution_references),
        ),
        delivery_strategy=DeliveryStrategy(
            **delivery_values,
            requirement_references=tuple(delivery_references),
        ),
        assumptions=(),
        risks=(),
        decisions=tuple(decisions),
    )
