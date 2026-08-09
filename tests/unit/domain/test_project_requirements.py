from collections.abc import Callable
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


def test_requirements_default_to_unspecified_profiles() -> None:
    requirements = ProjectRequirements()

    assert requirements.application == ApplicationProfile()
    assert requirements.interfaces == InterfaceProfile()
    assert requirements.execution.browsers is None
    assert requirements.team.languages is None
    assert requirements.constraints.approved_technologies is None


def test_partially_specified_requirements_preserve_missing_information() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(application_type="web"),
        interfaces=InterfaceProfile(web_ui=True, rest_api=None),
        automation=AutomationRequirements(ui_testing=True),
    )

    assert requirements.application.frontend_technology is None
    assert requirements.interfaces.web_ui is True
    assert requirements.interfaces.rest_api is None
    assert requirements.automation.api_testing is None


def test_false_is_distinct_from_unspecified() -> None:
    requirements = ProjectRequirements(
        interfaces=InterfaceProfile(web_ui=False),
        automation=AutomationRequirements(accessibility_testing=False),
        execution=ExecutionRequirements(parallel_execution=False),
        delivery=DeliveryProfile(pull_request_validation=False),
    )

    assert requirements.interfaces.web_ui is False
    assert requirements.interfaces.rest_api is None
    assert requirements.automation.accessibility_testing is False
    assert requirements.execution.parallel_execution is False
    assert requirements.delivery.pull_request_validation is False


def test_fully_specified_requirements_aggregate_all_profiles() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile("web", "React", "FastAPI", "modular monolith"),
        interfaces=InterfaceProfile(True, True, False, True, True),
        automation=AutomationRequirements(True, True, True, True, True),
        execution=ExecutionRequirements(1500, 30, True, ("Chrome", "Edge")),
        delivery=DeliveryProfile("Jenkins", "daily", True),
        team=TeamProfile(3, ("Python", "TypeScript"), "advanced"),
        constraints=ConstraintProfile(
            ("Playwright",),
            ("Selenium",),
            ("SOC 2",),
        ),
    )

    assert requirements.execution.expected_test_count == 1500
    assert requirements.execution.browsers == ("Chrome", "Edge")
    assert requirements.team.languages == ("Python", "TypeScript")
    assert requirements.constraints.compliance_requirements == ("SOC 2",)


def test_domain_collections_are_immutable() -> None:
    execution = ExecutionRequirements(browsers=("Chrome",))

    with pytest.raises(FrozenInstanceError):
        execution.browsers = ("Firefox",)  # type: ignore[misc]


@pytest.mark.parametrize("expected_test_count", [-1, -100])
def test_negative_expected_test_count_is_invalid(expected_test_count: int) -> None:
    with pytest.raises(ValueError, match="expected_test_count must not be negative"):
        ExecutionRequirements(expected_test_count=expected_test_count)


@pytest.mark.parametrize("target_execution_minutes", [0, -1])
def test_non_positive_execution_duration_is_invalid(target_execution_minutes: int) -> None:
    with pytest.raises(ValueError, match="target_execution_minutes must be greater than zero"):
        ExecutionRequirements(target_execution_minutes=target_execution_minutes)


@pytest.mark.parametrize("team_size", [0, -1])
def test_non_positive_team_size_is_invalid(team_size: int) -> None:
    with pytest.raises(ValueError, match="team_size must be greater than zero"):
        TeamProfile(team_size=team_size)


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: ExecutionRequirements(browsers=("Chrome", " ")), "browsers"),
        (lambda: TeamProfile(languages=("",)), "languages"),
        (
            lambda: ConstraintProfile(approved_technologies=("Playwright", "\t")),
            "approved_technologies",
        ),
        (lambda: ConstraintProfile(prohibited_technologies=("",)), "prohibited_technologies"),
        (lambda: ConstraintProfile(compliance_requirements=("\n",)), "compliance_requirements"),
    ],
)
def test_blank_collection_values_are_invalid(
    factory: Callable[[], object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        factory()


def test_domain_model_has_no_framework_dependencies() -> None:
    module_names = {
        profile.__class__.__module__
        for profile in (
            ApplicationProfile(),
            InterfaceProfile(),
            AutomationRequirements(),
            ExecutionRequirements(),
            DeliveryProfile(),
            TeamProfile(),
            ConstraintProfile(),
        )
    }

    assert module_names == {"app.domain.models.project_requirements"}


@pytest.mark.parametrize(
    "factory",
    [
        lambda: InterfaceProfile(web_ui="yes"),  # type: ignore[arg-type]
        lambda: AutomationRequirements(api_testing=1),  # type: ignore[arg-type]
        lambda: ExecutionRequirements(parallel_execution="false"),  # type: ignore[arg-type]
        lambda: DeliveryProfile(pull_request_validation=0),  # type: ignore[arg-type]
    ],
)
def test_boolean_fields_reject_non_boolean_values(factory: Callable[[], object]) -> None:
    with pytest.raises(TypeError, match="must be a bool or None"):
        factory()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: ExecutionRequirements(expected_test_count=True),
        lambda: ExecutionRequirements(target_execution_minutes="30"),  # type: ignore[arg-type]
        lambda: TeamProfile(team_size=False),
    ],
)
def test_integer_fields_reject_non_integer_values_and_bool(
    factory: Callable[[], object],
) -> None:
    with pytest.raises(TypeError, match="must be an int or None"):
        factory()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: ApplicationProfile(application_type=" "),
        lambda: ApplicationProfile(frontend_technology=1),  # type: ignore[arg-type]
        lambda: ApplicationProfile(backend_technology="\t"),
        lambda: ApplicationProfile(architecture_style=False),  # type: ignore[arg-type]
        lambda: DeliveryProfile(ci_provider=""),
        lambda: DeliveryProfile(release_frequency=2),  # type: ignore[arg-type]
        lambda: TeamProfile(automation_experience="\n"),
    ],
)
def test_scalar_string_fields_reject_invalid_values(factory: Callable[[], object]) -> None:
    with pytest.raises((TypeError, ValueError), match="must (be a string or None|not be blank)"):
        factory()


def test_scalar_string_fields_trim_surrounding_whitespace() -> None:
    application = ApplicationProfile(frontend_technology="  React  ")
    delivery = DeliveryProfile(ci_provider="  Jenkins  ")
    team = TeamProfile(automation_experience="  advanced  ")

    assert application.frontend_technology == "React"
    assert delivery.ci_provider == "Jenkins"
    assert team.automation_experience == "advanced"


@pytest.mark.parametrize(
    ("member", "value", "expected_name"),
    [
        ("application", InterfaceProfile(), "ApplicationProfile"),
        ("interfaces", AutomationRequirements(), "InterfaceProfile"),
        ("automation", ExecutionRequirements(), "AutomationRequirements"),
        ("execution", DeliveryProfile(), "ExecutionRequirements"),
        ("delivery", TeamProfile(), "DeliveryProfile"),
        ("team", ConstraintProfile(), "TeamProfile"),
        ("constraints", ApplicationProfile(), "ConstraintProfile"),
    ],
)
def test_aggregate_members_reject_wrong_profile_types(
    member: str, value: object, expected_name: str
) -> None:
    arguments = {member: value}

    with pytest.raises(TypeError, match=expected_name):
        ProjectRequirements(**arguments)  # type: ignore[arg-type]
