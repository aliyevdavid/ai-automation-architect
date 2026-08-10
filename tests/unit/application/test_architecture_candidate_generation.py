from dataclasses import replace

import pytest

from app.application import (
    analyze_project_requirements,
    generate_automation_architecture_candidate,
)
from app.domain.models import (
    ArchitectureDecision,
    ArchitectureLayer,
    AutomationArchitectureCandidate,
    AutomationCapability,
    DeliveryStrategy,
    ExecutionStrategy,
    ProjectRequirements,
    RequirementTraceReference,
)
from app.domain.services import (
    EngineeringPolicyEvaluationResult,
    EngineeringPolicyFinding,
)

POLICIES = (
    (
        "capability.browser_automation_required",
        "automation.ui_testing",
        "Browser automation",
        "Support automated validation of browser-based user interfaces.",
        "Browser automation layer",
        ("Execute browser-based user-interface automation.",),
        "Include browser-based UI automation.",
        "Explicit project requirements require browser-based UI automation.",
    ),
    (
        "capability.api_automation_required",
        "automation.api_testing",
        "API automation",
        "Support automated validation of application programming interfaces.",
        "API automation layer",
        ("Execute automated API validation.",),
        "Include API test automation.",
        "Explicit project requirements require API test automation.",
    ),
    (
        "capability.integration_testing_required",
        "automation.integration_testing",
        "Integration testing",
        "Support automated validation across integrated system boundaries.",
        "Integration testing layer",
        ("Validate interactions across integrated system boundaries.",),
        "Include integration testing.",
        "Explicit project requirements require integration testing.",
    ),
    (
        "capability.performance_testing_required",
        "automation.performance_testing",
        "Performance testing",
        "Support automated evaluation of system performance characteristics.",
        None,
        None,
        "Include performance testing.",
        "Explicit project requirements require performance testing.",
    ),
    (
        "capability.accessibility_testing_required",
        "automation.accessibility_testing",
        "Accessibility testing",
        "Support automated accessibility validation.",
        None,
        None,
        "Include accessibility testing.",
        "Explicit project requirements require accessibility testing.",
    ),
    (
        "capability.parallel_execution_required",
        "execution.parallel_execution",
        "Parallel test execution",
        "Support concurrent automated test execution.",
        None,
        None,
        "Support parallel test execution.",
        "Explicit project requirements require parallel test execution.",
    ),
    (
        "capability.pull_request_validation_required",
        "delivery.pull_request_validation",
        "Pull-request validation",
        "Support automated validation of code changes before integration.",
        None,
        None,
        "Include automated pull-request validation.",
        "Explicit project requirements require automated pull-request validation.",
    ),
)


def _analysis_with(*findings: EngineeringPolicyFinding):
    baseline = analyze_project_requirements(ProjectRequirements())
    return replace(
        baseline,
        engineering_policies=EngineeringPolicyEvaluationResult(tuple(findings)),
    )


def _finding(code: str, *paths: str) -> EngineeringPolicyFinding:
    return EngineeringPolicyFinding(code, paths, "Generator input message")


def test_empty_findings_produce_empty_valid_candidate() -> None:
    assert generate_automation_architecture_candidate(_analysis_with()) == (
        AutomationArchitectureCandidate()
    )


@pytest.mark.parametrize(
    (
        "code",
        "path",
        "capability_name",
        "purpose",
        "layer_name",
        "responsibilities",
        "decision",
        "rationale",
    ),
    POLICIES,
)
def test_each_policy_has_its_exact_capability_layer_and_decision_mapping(
    code: str,
    path: str,
    capability_name: str,
    purpose: str,
    layer_name: str | None,
    responsibilities: tuple[str, ...] | None,
    decision: str,
    rationale: str,
) -> None:
    candidate = generate_automation_architecture_candidate(
        _analysis_with(_finding(code, path))
    )
    references = (RequirementTraceReference(path),)

    assert candidate.capabilities == (
        AutomationCapability(capability_name, purpose, references),
    )
    assert candidate.decisions == (
        ArchitectureDecision(decision, rationale, references),
    )
    assert candidate.layers == (
        ()
        if layer_name is None or responsibilities is None
        else (ArchitectureLayer(layer_name, responsibilities, references),)
    )
    assert candidate.assumptions == ()
    assert candidate.risks == ()


def test_browser_parallel_and_pull_request_policies_populate_only_defined_strategies() -> None:
    browser = _finding(POLICIES[0][0], "browser.first", "browser.second")
    parallel = _finding(POLICIES[5][0], "parallel.first", "parallel.second")
    pull_request = _finding(POLICIES[6][0], "delivery.first", "delivery.second")

    candidate = generate_automation_architecture_candidate(
        _analysis_with(browser, parallel, pull_request)
    )

    assert candidate.execution_strategy == ExecutionStrategy(
        browser_execution="Support browser-based UI automation execution.",
        parallelization="Support parallel test execution.",
        regression_execution=None,
        test_distribution=None,
        requirement_references=(
            RequirementTraceReference("browser.first"),
            RequirementTraceReference("browser.second"),
            RequirementTraceReference("parallel.first"),
            RequirementTraceReference("parallel.second"),
        ),
    )
    assert candidate.delivery_strategy == DeliveryStrategy(
        continuous_integration=None,
        pull_request_validation="Run automated validation for pull requests.",
        release_validation=None,
        requirement_references=(
            RequirementTraceReference("delivery.first"),
            RequirementTraceReference("delivery.second"),
        ),
    )


def test_all_findings_preserve_capability_layer_decision_and_reference_order() -> None:
    findings = tuple(_finding(policy[0], policy[1]) for policy in reversed(POLICIES))

    candidate = generate_automation_architecture_candidate(_analysis_with(*findings))

    assert tuple(item.name for item in candidate.capabilities) == tuple(
        policy[2] for policy in reversed(POLICIES)
    )
    assert tuple(item.name for item in candidate.layers) == (
        "Integration testing layer",
        "API automation layer",
        "Browser automation layer",
    )
    assert tuple(item.decision for item in candidate.decisions) == tuple(
        policy[6] for policy in reversed(POLICIES)
    )
    for finding, capability, decision in zip(
        findings, candidate.capabilities, candidate.decisions, strict=True
    ):
        assert capability.requirement_references == finding.trace_references
        assert decision.requirement_references == finding.trace_references
        assert all(
            isinstance(reference, RequirementTraceReference)
            for reference in capability.requirement_references
        )


def test_duplicate_findings_and_trace_references_are_not_deduplicated() -> None:
    duplicate = _finding(
        "capability.browser_automation_required",
        "automation.ui_testing",
        "automation.ui_testing",
    )

    candidate = generate_automation_architecture_candidate(
        _analysis_with(duplicate, duplicate)
    )

    assert len(candidate.capabilities) == len(candidate.layers) == len(candidate.decisions) == 2
    assert candidate.execution_strategy.requirement_references == (
        RequirementTraceReference("automation.ui_testing"),
        RequirementTraceReference("automation.ui_testing"),
        RequirementTraceReference("automation.ui_testing"),
        RequirementTraceReference("automation.ui_testing"),
    )


def test_equal_analyses_produce_equal_candidates() -> None:
    first = _analysis_with(_finding(POLICIES[1][0], POLICIES[1][1]))
    second = _analysis_with(_finding(POLICIES[1][0], POLICIES[1][1]))

    assert first == second
    assert generate_automation_architecture_candidate(first) == (
        generate_automation_architecture_candidate(second)
    )


def test_unknown_policy_code_fails_fast_and_identifies_the_code() -> None:
    unsupported_code = "capability.unsupported_required"

    with pytest.raises(ValueError, match=unsupported_code):
        generate_automation_architecture_candidate(
            _analysis_with(_finding(unsupported_code, "automation.unknown"))
        )


def test_generation_does_not_mutate_the_analysis_or_nested_results() -> None:
    analysis = _analysis_with(_finding(POLICIES[0][0], POLICIES[0][1]))
    before = repr(analysis)
    findings_before = analysis.engineering_policies.findings

    generate_automation_architecture_candidate(analysis)

    assert repr(analysis) == before
    assert analysis.engineering_policies.findings is findings_before


def test_generated_text_does_not_select_a_concrete_framework_or_provider() -> None:
    candidate = generate_automation_architecture_candidate(
        _analysis_with(*(_finding(policy[0], policy[1]) for policy in POLICIES))
    )
    generated_text = repr(candidate).casefold()

    prohibited = (
        "playwright",
        "selenium",
        "cypress",
        "jenkins",
        "github actions",
        "azure devops",
    )
    assert all(term not in generated_text for term in prohibited)
