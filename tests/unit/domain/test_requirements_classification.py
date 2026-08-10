from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import (
    ApplicationProfile,
    ConstraintProfile,
    DeliveryProfile,
    PreferenceProfile,
    ProjectRequirements,
    RequirementTraceReference,
    TeamProfile,
)
from app.domain.services import (
    RequirementClassification,
    RequirementClassificationKind,
    RequirementClassificationResult,
    classify_project_requirements,
)


def test_classifies_explicit_values_in_exact_stable_order_with_traceability() -> None:
    requirements = ProjectRequirements(
        preferences=PreferenceProfile(("playwright", "selenium", "selenium")),
        constraints=ConstraintProfile(
            approved_technologies=("selenium", "robot"),
            prohibited_technologies=("selenium",),
            compliance_requirements=("SOC 2", "SOC 2"),
        ),
    )

    result = classify_project_requirements(requirements)

    assert tuple((item.field_path, item.kind, item.value) for item in result.classifications) == (
        (
            "preferences.preferred_technologies[0]",
            RequirementClassificationKind.PREFERENCE,
            "playwright",
        ),
        (
            "preferences.preferred_technologies[1]",
            RequirementClassificationKind.PREFERENCE,
            "selenium",
        ),
        (
            "preferences.preferred_technologies[2]",
            RequirementClassificationKind.PREFERENCE,
            "selenium",
        ),
        (
            "constraints.approved_technologies[0]",
            RequirementClassificationKind.CONSTRAINT,
            "selenium",
        ),
        ("constraints.approved_technologies[1]", RequirementClassificationKind.CONSTRAINT, "robot"),
        (
            "constraints.prohibited_technologies[0]",
            RequirementClassificationKind.CONSTRAINT,
            "selenium",
        ),
        (
            "constraints.compliance_requirements[0]",
            RequirementClassificationKind.CONSTRAINT,
            "SOC 2",
        ),
        (
            "constraints.compliance_requirements[1]",
            RequirementClassificationKind.CONSTRAINT,
            "SOC 2",
        ),
    )
    assert result.classifications[0].trace_references == (
        RequirementTraceReference("preferences.preferred_technologies[0]"),
    )


def test_none_empty_and_unrelated_context_contribute_no_classifications() -> None:
    requirements = ProjectRequirements(
        application=ApplicationProfile("web", "React", "FastAPI", "layered"),
        delivery=DeliveryProfile(ci_provider="Jenkins"),
        team=TeamProfile(languages=("Python",)),
        preferences=PreferenceProfile(()),
        constraints=ConstraintProfile(None, (), None),
    )

    assert classify_project_requirements(requirements).classifications == ()


def test_classifier_preserves_unnormalized_input_and_is_deterministic() -> None:
    requirements = ProjectRequirements(preferences=PreferenceProfile((" PlayWright ",)))

    expected = RequirementClassificationResult(
        (
            RequirementClassification(
                "preferences.preferred_technologies[0]",
                " PlayWright ",
                RequirementClassificationKind.PREFERENCE,
            ),
        )
    )
    assert classify_project_requirements(requirements) == expected
    assert classify_project_requirements(requirements) == classify_project_requirements(
        requirements
    )


def test_classification_contracts_validate_and_are_immutable() -> None:
    item = RequirementClassification("field[0]", "value", RequirementClassificationKind.CONSTRAINT)
    result = RequirementClassificationResult((item,))

    with pytest.raises(FrozenInstanceError):
        item.value = "other"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.classifications = ()  # type: ignore[misc]
    with pytest.raises(ValueError, match="field_path"):
        RequirementClassification(" ", "value", RequirementClassificationKind.CONSTRAINT)
    with pytest.raises(ValueError, match="value"):
        RequirementClassification("field", " ", RequirementClassificationKind.CONSTRAINT)
    with pytest.raises(TypeError, match="kind"):
        RequirementClassification("field", "value", "constraint")  # type: ignore[arg-type]
