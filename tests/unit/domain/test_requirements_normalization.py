from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import (
    ApplicationProfile,
    AutomationRequirements,
    ConstraintProfile,
    DeliveryProfile,
    ExecutionRequirements,
    InterfaceProfile,
    ProjectRequirements,
    TeamProfile,
)
from app.domain.services import (
    RequirementNormalizationChange,
    RequirementNormalizationResult,
    RequirementNormalizationRule,
    normalize_project_requirements,
)


def test_normalizes_supported_values_and_records_ordered_trace() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(
            application_type=" Web ",
            frontend_technology="React",
            backend_technology="FASTAPI",
            architecture_style=" Modular Monolith ",
        ),
        execution=ExecutionRequirements(browsers=(" Chrome ", "Edge")),
        delivery=DeliveryProfile(ci_provider="GitHub Actions"),
        team=TeamProfile(languages=(" Python ", "C#")),
        constraints=ConstraintProfile(
            approved_technologies=(" Playwright ", "unknown-tool"),
            prohibited_technologies=("SELENIUM",),
            compliance_requirements=(" SOC 2 ",),
        ),
    )

    result = normalize_project_requirements(requirements)

    assert result.normalized_requirements == ProjectRequirements(
        application=ApplicationProfile("Web", "react", "fastapi", "Modular Monolith"),
        execution=ExecutionRequirements(browsers=("Chrome", "Edge")),
        delivery=DeliveryProfile(ci_provider="github actions"),
        team=TeamProfile(languages=("Python", "C#")),
        constraints=ConstraintProfile(
            ("playwright", "unknown-tool"), ("selenium",), ("SOC 2",)
        ),
    )
    assert tuple(change.field_path for change in result.changes) == (
        "application.frontend_technology",
        "application.backend_technology",
        "execution.browsers[0]",
        "delivery.ci_provider",
        "team.languages[0]",
        "constraints.approved_technologies[0]",
        "constraints.prohibited_technologies[0]",
        "constraints.compliance_requirements[0]",
    )
    assert result.changes[0] == RequirementNormalizationChange(
        field_path="application.frontend_technology",
        original_value="React",
        normalized_value="react",
        rule=RequirementNormalizationRule.CASEFOLD_CASE_INSENSITIVE_VALUE,
    )
    assert result.changes[5] == RequirementNormalizationChange(
        field_path="constraints.approved_technologies[0]",
        original_value=" Playwright ",
        normalized_value="playwright",
        rule=RequirementNormalizationRule.TRIM_AND_CASEFOLD_CASE_INSENSITIVE_VALUE,
    )


def test_preserves_none_false_empty_tuples_and_original_aggregate() -> None:
    requirements = ProjectRequirements(
        interfaces=InterfaceProfile(web_ui=False),
        automation=AutomationRequirements(ui_testing=False),
        execution=ExecutionRequirements(parallel_execution=False, browsers=()),
        delivery=DeliveryProfile(pull_request_validation=False),
        team=TeamProfile(languages=None),
        constraints=ConstraintProfile(
            approved_technologies=None,
            prohibited_technologies=(),
            compliance_requirements=None,
        ),
    )
    before = repr(requirements)

    result = normalize_project_requirements(requirements)

    normalized = result.normalized_requirements
    assert normalized.interfaces.web_ui is False
    assert normalized.automation.ui_testing is False
    assert normalized.execution.parallel_execution is False
    assert normalized.execution.browsers == ()
    assert normalized.team.languages is None
    assert normalized.constraints.approved_technologies is None
    assert normalized.constraints.prohibited_technologies == ()
    assert result.changes == ()
    assert repr(requirements) == before


def test_unchanged_canonical_data_has_no_changes_and_preserves_collection_order() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(frontend_technology="react"),
        execution=ExecutionRequirements(browsers=("Firefox", "Chrome", "Firefox")),
        constraints=ConstraintProfile(
            approved_technologies=("custom technology", "playwright")
        ),
    )

    first = normalize_project_requirements(requirements)
    second = normalize_project_requirements(requirements)

    assert first == second
    assert first.changes == ()
    assert first.normalized_requirements.execution.browsers == (
        "Firefox",
        "Chrome",
        "Firefox",
    )
    assert first.normalized_requirements.constraints.approved_technologies == (
        "custom technology",
        "playwright",
    )


def test_unknown_values_are_casefolded_but_not_guessed_or_aliased() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(frontend_technology="PW"),
        delivery=DeliveryProfile(ci_provider="Microsoft CI"),
        constraints=ConstraintProfile(prohibited_technologies=("selenium-ish",)),
    )

    normalized = normalize_project_requirements(requirements).normalized_requirements

    assert normalized.application.frontend_technology == "pw"
    assert normalized.delivery.ci_provider == "microsoft ci"
    assert normalized.constraints.prohibited_technologies == ("selenium-ish",)


def test_result_and_change_contracts_are_immutable() -> None:
    change = RequirementNormalizationChange(
        "field",
        "Original",
        "original",
        RequirementNormalizationRule.CASEFOLD_CASE_INSENSITIVE_VALUE,
    )
    result = RequirementNormalizationResult(ProjectRequirements(), (change,))

    with pytest.raises(FrozenInstanceError):
        change.field_path = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.changes = ()  # type: ignore[misc]


def test_normalization_service_is_framework_independent() -> None:
    expected_module = "app.domain.services.requirements_normalization"

    assert RequirementNormalizationChange.__module__ == expected_module
    assert RequirementNormalizationResult.__module__ == expected_module
    assert RequirementNormalizationRule.__module__ == expected_module
    assert normalize_project_requirements.__module__ == expected_module
