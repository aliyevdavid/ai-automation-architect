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
    RequirementsCompletenessResult,
    analyze_requirements_completeness,
)


def complete_base_requirements() -> ProjectRequirements:
    return ProjectRequirements(
        application=ApplicationProfile("web", architecture_style="modular monolith"),
        interfaces=InterfaceProfile(False, False, False, False, False),
        automation=AutomationRequirements(False, False, False, False, False),
        execution=ExecutionRequirements(100, 15, False),
        delivery=DeliveryProfile("GitHub Actions", "daily", False),
        team=TeamProfile(2, ("Python",), "advanced"),
        constraints=ConstraintProfile((), (), ()),
    )


def test_unspecified_requirements_report_every_base_field_missing() -> None:
    result = analyze_requirements_completeness(ProjectRequirements())

    assert result.required_count == 24
    assert result.satisfied_count == 0
    assert len(result.missing_requirements) == 24
    assert result.completeness_percentage == 0.0
    assert result.is_complete is False


def test_partially_specified_requirements_have_exact_score_and_missing_fields() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(application_type="web"),
        interfaces=InterfaceProfile(web_ui=False),
        automation=AutomationRequirements(ui_testing=False),
    )

    result = analyze_requirements_completeness(requirements)

    assert result.required_count == 24
    assert result.satisfied_count == 3
    assert result.completeness_percentage == 12.5
    assert "application.application_type" not in result.missing_requirements
    assert "application.architecture_style" in result.missing_requirements


def test_fully_complete_base_requirements_are_complete() -> None:
    result = analyze_requirements_completeness(complete_base_requirements())

    assert result == RequirementsCompletenessResult(24, 24, (), 100.0, True)


def test_false_and_empty_tuples_count_as_explicitly_supplied() -> None:
    result = analyze_requirements_completeness(complete_base_requirements())

    assert "interfaces.web_ui" not in result.missing_requirements
    assert "execution.parallel_execution" not in result.missing_requirements
    assert "constraints.approved_technologies" not in result.missing_requirements


def test_none_counts_as_missing_even_when_other_values_are_falsy() -> None:
    requirements = ProjectRequirements(
        interfaces=InterfaceProfile(False, False, False, False, None),
    )

    result = analyze_requirements_completeness(requirements)

    assert result.satisfied_count == 4
    assert "interfaces.messaging" in result.missing_requirements


def test_web_ui_true_activates_frontend_technology_requirement() -> None:
    requirements = complete_base_requirements()
    requirements = ProjectRequirements(
        application=requirements.application,
        interfaces=InterfaceProfile(True, False, False, False, False),
        automation=requirements.automation,
        execution=requirements.execution,
        delivery=requirements.delivery,
        team=requirements.team,
        constraints=requirements.constraints,
    )

    result = analyze_requirements_completeness(requirements)

    assert result.required_count == 25
    assert result.satisfied_count == 24
    assert result.missing_requirements == ("application.frontend_technology",)


def test_web_ui_false_does_not_activate_frontend_technology() -> None:
    result = analyze_requirements_completeness(complete_base_requirements())

    assert "application.frontend_technology" not in result.missing_requirements
    assert result.required_count == 24


@pytest.mark.parametrize("interface_name", ["rest_api", "graphql", "database", "messaging"])
def test_each_backend_interface_activates_backend_technology(interface_name: str) -> None:
    interface_names = ("web_ui", "rest_api", "graphql", "database", "messaging")
    interfaces = {name: False for name in interface_names}
    interfaces[interface_name] = True
    base = complete_base_requirements()
    requirements = ProjectRequirements(
        application=base.application,
        interfaces=InterfaceProfile(**interfaces),
        automation=base.automation,
        execution=base.execution,
        delivery=base.delivery,
        team=base.team,
        constraints=base.constraints,
    )

    result = analyze_requirements_completeness(requirements)

    assert result.required_count == 25
    assert result.missing_requirements == ("application.backend_technology",)


def test_false_backend_interfaces_do_not_activate_backend_technology() -> None:
    result = analyze_requirements_completeness(complete_base_requirements())

    assert "application.backend_technology" not in result.missing_requirements


def test_ui_testing_true_activates_browsers_requirement() -> None:
    base = complete_base_requirements()
    requirements = ProjectRequirements(
        application=base.application,
        interfaces=base.interfaces,
        automation=AutomationRequirements(True, False, False, False, False),
        execution=base.execution,
        delivery=base.delivery,
        team=base.team,
        constraints=base.constraints,
    )

    result = analyze_requirements_completeness(requirements)

    assert result.required_count == 25
    assert result.missing_requirements == ("execution.browsers",)


def test_ui_testing_false_does_not_activate_browsers() -> None:
    result = analyze_requirements_completeness(complete_base_requirements())

    assert "execution.browsers" not in result.missing_requirements


def test_all_conditional_rules_can_be_active_and_complete() -> None:
    base = complete_base_requirements()
    requirements = ProjectRequirements(
        application=ApplicationProfile("web", "React", "FastAPI", "modular monolith"),
        interfaces=InterfaceProfile(True, True, False, False, False),
        automation=AutomationRequirements(True, False, False, False, False),
        execution=ExecutionRequirements(100, 15, False, ()),
        delivery=base.delivery,
        team=base.team,
        constraints=base.constraints,
    )

    result = analyze_requirements_completeness(requirements)

    assert result.required_count == 27
    assert result.satisfied_count == 27
    assert result.completeness_percentage == 100.0
    assert result.is_complete is True


def test_percentage_is_rounded_to_two_decimal_places() -> None:
    requirements = ProjectRequirements(application=ApplicationProfile(application_type="web"))

    result = analyze_requirements_completeness(requirements)

    assert result.completeness_percentage == 4.17


def test_missing_requirement_order_is_stable() -> None:
    first = analyze_requirements_completeness(
        ProjectRequirements(
            interfaces=InterfaceProfile(web_ui=True, rest_api=True),
            automation=AutomationRequirements(ui_testing=True),
        )
    )
    second = analyze_requirements_completeness(
        ProjectRequirements(
            interfaces=InterfaceProfile(web_ui=True, rest_api=True),
            automation=AutomationRequirements(ui_testing=True),
        )
    )

    assert first.missing_requirements == second.missing_requirements
    assert first.missing_requirements[-3:] == (
        "application.frontend_technology",
        "application.backend_technology",
        "execution.browsers",
    )


def test_analysis_does_not_mutate_project_requirements() -> None:
    requirements = complete_base_requirements()

    before = repr(requirements)
    analyze_requirements_completeness(requirements)

    assert repr(requirements) == before
    with pytest.raises(FrozenInstanceError):
        requirements.application = ApplicationProfile()  # type: ignore[misc]


def test_completeness_service_and_result_are_framework_independent() -> None:
    assert RequirementsCompletenessResult.__module__ == (
        "app.domain.services.requirements_completeness"
    )
    assert analyze_requirements_completeness.__module__ == (
        "app.domain.services.requirements_completeness"
    )
