from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import (
    ApplicationProfile,
    ConstraintProfile,
    DeliveryProfile,
    ProjectRequirements,
    RequirementTraceReference,
)
from app.domain.services import (
    ConflictSeverity,
    RequirementConflict,
    RequirementConflictResult,
    analyze_requirement_conflicts,
)


def test_empty_requirements_have_no_conflicts() -> None:
    result = analyze_requirement_conflicts(ProjectRequirements())

    assert result == RequirementConflictResult(conflicts=())
    assert result.conflict_count == 0
    assert result.has_conflicts is False


def test_complete_noncontradictory_requirements_have_no_conflicts() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile("web", "React", "FastAPI", "modular monolith"),
        delivery=DeliveryProfile("GitHub Actions", "daily", True),
        constraints=ConstraintProfile(("Playwright",), ("Selenium",), ("SOC 2",)),
    )

    assert analyze_requirement_conflicts(requirements).conflicts == ()


@pytest.mark.parametrize(
    ("approved", "prohibited", "preserved"),
    [
        ("Playwright", "Playwright", "Playwright"),
        ("Playwright", "playwright", "Playwright"),
        (" PostgreSQL ", "postgresql", " PostgreSQL "),
    ],
)
def test_approved_prohibited_overlap_uses_exact_normalized_comparison(
    approved: str, prohibited: str, preserved: str
) -> None:
    requirements = ProjectRequirements(
        constraints=ConstraintProfile((approved,), (prohibited,)),
    )

    conflict = analyze_requirement_conflicts(requirements).conflicts[0]

    assert conflict == RequirementConflict(
        code="technology.approved_prohibited_overlap",
        severity=ConflictSeverity.ERROR,
        field_paths=(
            "constraints.approved_technologies",
            "constraints.prohibited_technologies",
        ),
        message=f"Technology '{preserved}' is simultaneously approved and prohibited.",
        conflicting_value=preserved,
    )


@pytest.mark.parametrize(
    ("application", "delivery", "code", "paths", "value"),
    [
        (
            ApplicationProfile(frontend_technology="React"),
            DeliveryProfile(),
            "technology.frontend_prohibited",
            ("application.frontend_technology", "constraints.prohibited_technologies"),
            "React",
        ),
        (
            ApplicationProfile(backend_technology="FastAPI"),
            DeliveryProfile(),
            "technology.backend_prohibited",
            ("application.backend_technology", "constraints.prohibited_technologies"),
            "FastAPI",
        ),
        (
            ApplicationProfile(),
            DeliveryProfile(ci_provider="Jenkins"),
            "delivery.ci_provider_prohibited",
            ("delivery.ci_provider", "constraints.prohibited_technologies"),
            "Jenkins",
        ),
    ],
)
def test_selected_technologies_report_exact_code_severity_paths_and_value(
    application: ApplicationProfile,
    delivery: DeliveryProfile,
    code: str,
    paths: tuple[str, ...],
    value: str,
) -> None:
    requirements = ProjectRequirements(
        application=application,
        delivery=delivery,
        constraints=ConstraintProfile(prohibited_technologies=(value.swapcase(),)),
    )

    conflict = analyze_requirement_conflicts(requirements).conflicts[0]

    assert conflict.code == code
    assert conflict.severity is ConflictSeverity.ERROR
    assert conflict.field_paths == paths
    assert conflict.conflicting_value == value


def test_multiple_conflicts_follow_policy_order_and_approved_source_order() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(frontend_technology="React", backend_technology="FastAPI"),
        delivery=DeliveryProfile(ci_provider="Jenkins"),
        constraints=ConstraintProfile(
            approved_technologies=("Jenkins", "React", "FastAPI"),
            prohibited_technologies=("react", "fastapi", "jenkins"),
        ),
    )

    result = analyze_requirement_conflicts(requirements)

    assert result.conflict_count == 6
    assert result.has_conflicts is True
    assert tuple(conflict.code for conflict in result.conflicts) == (
        "technology.approved_prohibited_overlap",
        "technology.approved_prohibited_overlap",
        "technology.approved_prohibited_overlap",
        "technology.frontend_prohibited",
        "technology.backend_prohibited",
        "delivery.ci_provider_prohibited",
    )
    assert tuple(conflict.conflicting_value for conflict in result.conflicts) == (
        "Jenkins",
        "React",
        "FastAPI",
        "React",
        "FastAPI",
        "Jenkins",
    )


@pytest.mark.parametrize(
    ("approved", "prohibited"),
    [("PostgreSQL", "Postgres"), ("GitHub", "GitHub Actions")],
)
def test_comparison_does_not_use_fuzzy_or_substring_matching(
    approved: str, prohibited: str
) -> None:
    requirements = ProjectRequirements(
        constraints=ConstraintProfile((approved,), (prohibited,)),
    )

    assert analyze_requirement_conflicts(requirements).conflicts == ()


@pytest.mark.parametrize(
    "constraints",
    [ConstraintProfile(None, None), ConstraintProfile((), ())],
)
def test_none_and_empty_collections_have_no_conflicts(constraints: ConstraintProfile) -> None:
    result = analyze_requirement_conflicts(ProjectRequirements(constraints=constraints))

    assert result.conflicts == ()


def test_analysis_does_not_mutate_requirements() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(frontend_technology="React"),
        constraints=ConstraintProfile((" React ",), ("react",)),
    )
    before = repr(requirements)

    analyze_requirement_conflicts(requirements)

    assert repr(requirements) == before


def test_conflict_and_result_are_immutable() -> None:
    conflict = RequirementConflict(
        "code",
        ConflictSeverity.ERROR,
        ("field.one", "field.two"),
        "message",
        "value",
    )
    result = RequirementConflictResult((conflict,))

    with pytest.raises(FrozenInstanceError):
        conflict.code = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.conflicts = ()  # type: ignore[misc]


def test_conflict_exposes_ordered_duplicate_trace_references_without_changing_contract() -> None:
    paths = (
        "application.frontend_technology",
        "constraints.prohibited_technologies[1]",
        "application.frontend_technology",
    )
    conflict = RequirementConflict("code", ConflictSeverity.ERROR, paths, "message", "value")

    assert conflict.field_paths is paths
    assert conflict.trace_references == tuple(RequirementTraceReference(path) for path in paths)
    assert (
        RequirementConflict("code", ConflictSeverity.ERROR, paths, "message", "value")
        == conflict
    )


def test_conflict_with_no_paths_exposes_no_trace_references() -> None:
    conflict = RequirementConflict("code", ConflictSeverity.ERROR, (), "message", "value")

    assert conflict.trace_references == ()


def test_conflict_service_and_models_are_framework_independent() -> None:
    expected_module = "app.domain.services.requirements_conflicts"

    assert ConflictSeverity.__module__ == expected_module
    assert RequirementConflict.__module__ == expected_module
    assert RequirementConflictResult.__module__ == expected_module
    assert analyze_requirement_conflicts.__module__ == expected_module
