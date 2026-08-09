from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import (
    ApplicationProfile,
    AutomationRequirements,
    ConstraintProfile,
    DeliveryProfile,
    ExecutionRequirements,
    ProjectRequirements,
    TeamProfile,
)
from app.domain.services import (
    EngineeringPolicyEvaluationResult,
    EngineeringPolicyFinding,
    evaluate_engineering_policies,
)

EXPECTED_FINDINGS = (
    EngineeringPolicyFinding(
        "capability.browser_automation_required",
        ("automation.ui_testing",),
        "The automation architecture must support browser-based UI automation.",
    ),
    EngineeringPolicyFinding(
        "capability.api_automation_required",
        ("automation.api_testing",),
        "The automation architecture must support API test automation.",
    ),
    EngineeringPolicyFinding(
        "capability.integration_testing_required",
        ("automation.integration_testing",),
        "The automation architecture must support integration testing.",
    ),
    EngineeringPolicyFinding(
        "capability.performance_testing_required",
        ("automation.performance_testing",),
        "The automation architecture must support performance testing.",
    ),
    EngineeringPolicyFinding(
        "capability.accessibility_testing_required",
        ("automation.accessibility_testing",),
        "The automation architecture must support accessibility testing.",
    ),
    EngineeringPolicyFinding(
        "capability.parallel_execution_required",
        ("execution.parallel_execution",),
        "The automation architecture must support parallel test execution.",
    ),
    EngineeringPolicyFinding(
        "capability.pull_request_validation_required",
        ("delivery.pull_request_validation",),
        "The automation architecture must support automated pull-request validation.",
    ),
)


def _requirements_for_policy(index: int) -> ProjectRequirements:
    automation_values = [False] * 5
    parallel_execution = False
    pull_request_validation = False
    if index < 5:
        automation_values[index] = True
    elif index == 5:
        parallel_execution = True
    else:
        pull_request_validation = True
    return ProjectRequirements(
        automation=AutomationRequirements(*automation_values),
        execution=ExecutionRequirements(parallel_execution=parallel_execution),
        delivery=DeliveryProfile(pull_request_validation=pull_request_validation),
    )


def test_empty_requirements_produce_no_findings() -> None:
    result = evaluate_engineering_policies(ProjectRequirements())

    assert result == EngineeringPolicyEvaluationResult(())
    assert result.finding_count == 0
    assert result.has_findings is False


def test_explicit_false_values_produce_no_findings() -> None:
    requirements = ProjectRequirements(
        automation=AutomationRequirements(False, False, False, False, False),
        execution=ExecutionRequirements(parallel_execution=False),
        delivery=DeliveryProfile(pull_request_validation=False),
    )

    assert evaluate_engineering_policies(requirements).findings == ()


def test_explicit_none_values_produce_no_findings() -> None:
    requirements = ProjectRequirements(
        automation=AutomationRequirements(None, None, None, None, None),
        execution=ExecutionRequirements(parallel_execution=None),
        delivery=DeliveryProfile(pull_request_validation=None),
    )

    assert evaluate_engineering_policies(requirements).findings == ()


@pytest.mark.parametrize(("index", "expected"), tuple(enumerate(EXPECTED_FINDINGS)))
def test_each_explicit_true_derives_its_exact_capability(
    index: int, expected: EngineeringPolicyFinding
) -> None:
    result = evaluate_engineering_policies(_requirements_for_policy(index))

    assert result.findings == (expected,)
    assert result.finding_count == 1
    assert result.has_findings is True


def test_multiple_simultaneous_policies_follow_policy_order() -> None:
    requirements = ProjectRequirements(
        automation=AutomationRequirements(
            ui_testing=True,
            integration_testing=True,
            accessibility_testing=True,
        ),
        delivery=DeliveryProfile(pull_request_validation=True),
    )

    result = evaluate_engineering_policies(requirements)

    assert result.findings == (
        EXPECTED_FINDINGS[0],
        EXPECTED_FINDINGS[2],
        EXPECTED_FINDINGS[4],
        EXPECTED_FINDINGS[6],
    )


def test_all_policies_have_exact_codes_paths_messages_and_order() -> None:
    requirements = ProjectRequirements(
        automation=AutomationRequirements(True, True, True, True, True),
        execution=ExecutionRequirements(parallel_execution=True),
        delivery=DeliveryProfile(pull_request_validation=True),
    )

    first = evaluate_engineering_policies(requirements)
    second = evaluate_engineering_policies(requirements)

    assert first == second == EngineeringPolicyEvaluationResult(EXPECTED_FINDINGS)
    assert first.finding_count == 7
    assert first.has_findings is True


def test_unrelated_fields_do_not_activate_or_change_policies() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(
            application_type="browser API performance accessibility integration",
            frontend_technology="Playwright",
            backend_technology="FastAPI",
            architecture_style="parallel microservices",
        ),
        execution=ExecutionRequirements(browsers=("Chrome", "Edge")),
        delivery=DeliveryProfile(ci_provider="GitHub Actions", release_frequency="per PR"),
        team=TeamProfile(languages=("Python",), automation_experience="expert"),
        constraints=ConstraintProfile(
            approved_technologies=("Selenium",),
            compliance_requirements=("accessibility testing required",),
        ),
    )

    assert evaluate_engineering_policies(requirements).findings == ()


def test_evaluation_does_not_mutate_project_requirements() -> None:
    requirements = ProjectRequirements(
        automation=AutomationRequirements(ui_testing=True),
        execution=ExecutionRequirements(parallel_execution=True),
    )
    before = repr(requirements)

    evaluate_engineering_policies(requirements)

    assert repr(requirements) == before


def test_finding_and_result_objects_are_immutable() -> None:
    finding = EXPECTED_FINDINGS[0]
    result = EngineeringPolicyEvaluationResult((finding,))

    with pytest.raises(FrozenInstanceError):
        finding.code = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.findings = ()  # type: ignore[misc]


def test_policy_service_and_models_are_framework_independent() -> None:
    expected_module = "app.domain.services.engineering_policy_evaluation"

    assert EngineeringPolicyFinding.__module__ == expected_module
    assert EngineeringPolicyEvaluationResult.__module__ == expected_module
    assert evaluate_engineering_policies.__module__ == expected_module
