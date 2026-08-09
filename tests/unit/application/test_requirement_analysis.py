from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.application import RequirementAnalysisResult, analyze_project_requirements
from app.domain.models import (
    ApplicationProfile,
    AutomationRequirements,
    ConstraintProfile,
    ExecutionRequirements,
    ProjectRequirements,
    RequirementTraceReference,
)
from app.domain.services import (
    EngineeringPolicyEvaluationResult,
    RequirementConflictResult,
    RequirementNormalizationResult,
    RequirementsCompletenessResult,
    analyze_requirement_conflicts,
    analyze_requirements_completeness,
    evaluate_engineering_policies,
    normalize_project_requirements,
)


def test_analysis_composes_existing_domain_results_from_normalized_requirements() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile(frontend_technology="Playwright"),
        automation=AutomationRequirements(ui_testing=True),
        constraints=ConstraintProfile(
            approved_technologies=("  PLAYWRIGHT  ",),
            prohibited_technologies=(" playwright ",),
        ),
    )
    before = repr(requirements)

    result = analyze_project_requirements(requirements)
    normalized = result.normalization.normalized_requirements

    assert isinstance(result, RequirementAnalysisResult)
    assert isinstance(result.normalization, RequirementNormalizationResult)
    assert isinstance(result.completeness, RequirementsCompletenessResult)
    assert isinstance(result.conflicts, RequirementConflictResult)
    assert isinstance(result.engineering_policies, EngineeringPolicyEvaluationResult)
    assert normalized.constraints.approved_technologies == ("playwright",)
    assert normalized.constraints.prohibited_technologies == ("playwright",)
    assert result.normalization.changes
    approved_change = next(
        change
        for change in result.normalization.changes
        if change.field_path == "constraints.approved_technologies[0]"
    )
    assert approved_change.trace_references == (
        RequirementTraceReference("constraints.approved_technologies[0]"),
    )
    assert result.completeness == analyze_requirements_completeness(normalized)
    assert result.conflicts == analyze_requirement_conflicts(normalized)
    assert tuple(conflict.conflicting_value for conflict in result.conflicts.conflicts) == (
        "playwright",
        "playwright",
    )
    assert result.conflicts.conflicts[0].trace_references == (
        RequirementTraceReference("constraints.approved_technologies"),
        RequirementTraceReference("constraints.prohibited_technologies"),
    )
    assert result.engineering_policies == evaluate_engineering_policies(normalized)
    assert result.engineering_policies.findings[0].trace_references == (
        RequirementTraceReference("automation.ui_testing"),
    )
    assert repr(requirements) == before
    assert requirements.constraints.approved_technologies == ("  PLAYWRIGHT  ",)


def test_contained_results_preserve_typed_traceability_and_value_semantics() -> None:
    requirements = ProjectRequirements(
        automation=AutomationRequirements(ui_testing=False, api_testing=None),
        execution=ExecutionRequirements(parallel_execution=False, browsers=()),
        constraints=ConstraintProfile(
            approved_technologies=None,
            prohibited_technologies=(),
        ),
    )

    result = analyze_project_requirements(requirements)
    normalized = result.normalization.normalized_requirements

    assert normalized.automation.ui_testing is False
    assert normalized.automation.api_testing is None
    assert normalized.execution.parallel_execution is False
    assert normalized.execution.browsers == ()
    assert normalized.constraints.approved_technologies is None
    assert normalized.constraints.prohibited_technologies == ()
    assert result.normalization.changes == ()
    assert result.completeness.missing_trace_references
    assert all(
        isinstance(reference, RequirementTraceReference)
        for reference in result.completeness.missing_trace_references
    )
    assert result.conflicts.conflicts == ()
    assert result.engineering_policies.findings == ()


def test_analysis_is_immutable_deterministic_and_supports_empty_requirements() -> None:
    requirements = ProjectRequirements()

    first = analyze_project_requirements(requirements)
    second = analyze_project_requirements(ProjectRequirements())

    assert first == second
    assert first.normalization == normalize_project_requirements(requirements)
    assert first.completeness == analyze_requirements_completeness(requirements)
    assert first.conflicts == RequirementConflictResult(())
    assert first.engineering_policies == EngineeringPolicyEvaluationResult(())
    with pytest.raises(FrozenInstanceError):
        first.conflicts = RequirementConflictResult(())  # type: ignore[misc]


def test_application_boundary_is_framework_independent_and_dependency_points_inward() -> None:
    repository_root = Path(__file__).parents[3]
    application_source = (
        repository_root / "app" / "application" / "requirement_analysis.py"
    ).read_text(encoding="utf-8")
    domain_sources = tuple((repository_root / "app" / "domain").rglob("*.py"))

    assert RequirementAnalysisResult.__module__ == "app.application.requirement_analysis"
    assert analyze_project_requirements.__module__ == "app.application.requirement_analysis"
    assert "fastapi" not in application_source.casefold()
    assert all(
        "app.application" not in source.read_text(encoding="utf-8")
        for source in domain_sources
    )
