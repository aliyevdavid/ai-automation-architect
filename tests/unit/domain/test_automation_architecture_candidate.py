from collections.abc import Callable
from dataclasses import FrozenInstanceError

import pytest

from app.domain.models import (
    ArchitectureDecision,
    ArchitectureLayer,
    AutomationArchitectureCandidate,
    AutomationCapability,
    DeliveryStrategy,
    ExecutionStrategy,
    RequirementTraceReference,
)


def _representative_candidate() -> AutomationArchitectureCandidate:
    ui_reference = RequirementTraceReference("automation.ui_testing")
    execution_reference = RequirementTraceReference("execution.parallel_execution")
    delivery_reference = RequirementTraceReference("delivery.pull_request_validation")
    return AutomationArchitectureCandidate(
        layers=(
            ArchitectureLayer(
                "Browser tests",
                ("Exercise user journeys", "Collect diagnostic artifacts"),
                (ui_reference,),
            ),
        ),
        capabilities=(
            AutomationCapability(
                "Browser automation", "Validate supported user experiences", (ui_reference,)
            ),
        ),
        execution_strategy=ExecutionStrategy(
            parallelization="Partition independent tests across workers",
            browser_execution="Exercise each supported browser",
            regression_execution="Run the complete regression suite on schedule",
            test_distribution="Keep independently executable test partitions",
            requirement_references=(execution_reference,),
        ),
        delivery_strategy=DeliveryStrategy(
            continuous_integration="Run automated suites in the delivery pipeline",
            pull_request_validation="Run fast validation for proposed changes",
            release_validation="Require regression evidence before release",
            requirement_references=(delivery_reference,),
        ),
        assumptions=("Test environments support isolated workers",),
        risks=("Shared test data may constrain concurrency",),
        decisions=(
            ArchitectureDecision(
                "Separate browser journeys from lower-level checks",
                "Keeps responsibility boundaries explicit",
                (ui_reference,),
            ),
        ),
    )


def test_representative_candidate_preserves_its_structured_contract() -> None:
    candidate = _representative_candidate()

    assert candidate.layers[0].responsibilities == (
        "Exercise user journeys",
        "Collect diagnostic artifacts",
    )
    assert candidate.capabilities[0].purpose == "Validate supported user experiences"
    assert candidate.execution_strategy.parallelization == (
        "Partition independent tests across workers"
    )
    assert candidate.delivery_strategy.release_validation == (
        "Require regression evidence before release"
    )
    assert candidate.assumptions == ("Test environments support isolated workers",)
    assert candidate.risks == ("Shared test data may constrain concurrency",)
    assert candidate.decisions[0].rationale == "Keeps responsibility boundaries explicit"


def test_candidate_and_supporting_values_are_immutable() -> None:
    candidate = _representative_candidate()

    with pytest.raises(FrozenInstanceError):
        candidate.risks = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        candidate.layers[0].name = "Changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        candidate.execution_strategy.parallelization = None  # type: ignore[misc]


def test_order_and_duplicates_are_preserved_in_all_collection_concepts() -> None:
    reference_a = RequirementTraceReference("execution.browsers[1]")
    reference_b = RequirementTraceReference("execution.browsers[0]")
    layer = ArchitectureLayer(
        "Browser tests", ("Second", "First", "Second"), (reference_a, reference_b, reference_a)
    )
    capability = AutomationCapability("Browser support", "Exercise browsers", (reference_b,))
    decision = ArchitectureDecision("Keep order", "Input order is meaningful")
    candidate = AutomationArchitectureCandidate(
        layers=(layer, layer),
        capabilities=(capability, capability),
        assumptions=("Second", "First", "Second"),
        risks=("Repeated", "Repeated"),
        decisions=(decision, decision),
    )

    assert layer.responsibilities == ("Second", "First", "Second")
    assert layer.requirement_references == (reference_a, reference_b, reference_a)
    assert candidate.layers == (layer, layer)
    assert candidate.capabilities == (capability, capability)
    assert candidate.assumptions == ("Second", "First", "Second")
    assert candidate.risks == ("Repeated", "Repeated")
    assert candidate.decisions == (decision, decision)


def test_empty_collections_and_unset_strategy_recommendations_are_supported() -> None:
    assert AutomationArchitectureCandidate() == AutomationArchitectureCandidate(
        layers=(),
        capabilities=(),
        execution_strategy=ExecutionStrategy(),
        delivery_strategy=DeliveryStrategy(),
        assumptions=(),
        risks=(),
        decisions=(),
    )


@pytest.mark.parametrize(
    "factory",
    [
        lambda: ArchitectureLayer(" ", ()),
        lambda: ArchitectureLayer("Layer", ("\t",)),
        lambda: AutomationCapability("", "Purpose"),
        lambda: AutomationCapability("Capability", "\n"),
        lambda: ExecutionStrategy(parallelization=" "),
        lambda: DeliveryStrategy(release_validation=""),
        lambda: ArchitectureDecision("Decision", " "),
        lambda: AutomationArchitectureCandidate(assumptions=("",)),
        lambda: AutomationArchitectureCandidate(risks=("\t",)),
    ],
)
def test_required_text_rejects_blank_values(factory: Callable[[], object]) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        factory()


def test_layer_requires_at_least_one_responsibility() -> None:
    with pytest.raises(ValueError, match="responsibilities must not be empty"):
        ArchitectureLayer("Layer", ())


@pytest.mark.parametrize(
    "factory",
    [
        lambda: ArchitectureLayer(1, ()),  # type: ignore[arg-type]
        lambda: ArchitectureLayer("Layer", ["Responsibility"]),  # type: ignore[arg-type]
        lambda: AutomationCapability("Capability", False),  # type: ignore[arg-type]
        lambda: ExecutionStrategy(browser_execution=3),  # type: ignore[arg-type]
        lambda: DeliveryStrategy(requirement_references=("delivery.ci_provider",)),  # type: ignore[arg-type]
        lambda: ArchitectureDecision("Decision", 2),  # type: ignore[arg-type]
        lambda: AutomationArchitectureCandidate(layers=[]),  # type: ignore[arg-type]
        lambda: AutomationArchitectureCandidate(assumptions=["Assumption"]),  # type: ignore[arg-type]
        lambda: AutomationArchitectureCandidate(execution_strategy=object()),  # type: ignore[arg-type]
    ],
)
def test_invalid_types_are_rejected(factory: Callable[[], object]) -> None:
    with pytest.raises(TypeError, match="must (be|contain)"):
        factory()


def test_required_scalar_text_is_trimmed_consistently() -> None:
    layer = ArchitectureLayer("  Layer  ", ("Responsibility",))
    capability = AutomationCapability("  Capability  ", "  Purpose  ")
    strategy = ExecutionStrategy(parallelization="  Use independent workers  ")

    assert layer.name == "Layer"
    assert capability == AutomationCapability("Capability", "Purpose")
    assert strategy.parallelization == "Use independent workers"


def test_trace_reference_instances_are_reused_directly() -> None:
    references = (
        RequirementTraceReference("constraints.approved_technologies[1]"),
        RequirementTraceReference("automation.ui_testing"),
    )
    layer = ArchitectureLayer("Layer", ("Responsibility",), references)

    assert layer.requirement_references is references
    assert layer.requirement_references[0] is references[0]


def test_equal_inputs_produce_equal_values_without_generated_identity() -> None:
    first = _representative_candidate()
    second = _representative_candidate()

    assert first == second
    assert not hasattr(first, "candidate_id")
    assert not hasattr(first, "created_at")


def test_candidate_models_have_only_domain_model_dependencies() -> None:
    model_types = (
        ArchitectureLayer,
        AutomationCapability,
        ExecutionStrategy,
        DeliveryStrategy,
        ArchitectureDecision,
        AutomationArchitectureCandidate,
    )

    assert {model_type.__module__ for model_type in model_types} == {
        "app.domain.models.automation_architecture_candidate"
    }
