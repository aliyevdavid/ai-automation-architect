from dataclasses import dataclass

from app.domain.models import ProjectRequirements
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


@dataclass(frozen=True, slots=True)
class RequirementAnalysisResult:
    """Combined deterministic analysis of normalized project requirements."""

    normalization: RequirementNormalizationResult
    completeness: RequirementsCompletenessResult
    conflicts: RequirementConflictResult
    engineering_policies: EngineeringPolicyEvaluationResult


def analyze_project_requirements(
    requirements: ProjectRequirements,
) -> RequirementAnalysisResult:
    """Normalize requirements once, then run each deterministic domain analysis."""
    normalization = normalize_project_requirements(requirements)
    normalized_requirements = normalization.normalized_requirements

    return RequirementAnalysisResult(
        normalization=normalization,
        completeness=analyze_requirements_completeness(normalized_requirements),
        conflicts=analyze_requirement_conflicts(normalized_requirements),
        engineering_policies=evaluate_engineering_policies(normalized_requirements),
    )
