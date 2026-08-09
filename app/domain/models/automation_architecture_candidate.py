from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.models.requirement_trace_reference import RequirementTraceReference


def _required_text(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"{name} must not be blank.")
    return normalized_value


def _optional_text(name: str, value: str | None) -> str | None:
    if value is None:
        return None
    return _required_text(name, value)


def _typed_tuple(name: str, values: tuple[object, ...], expected_type: type[object]) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple.")
    if any(not isinstance(value, expected_type) for value in values):
        raise TypeError(f"{name} must contain only {expected_type.__name__} values.")


def _text_tuple(name: str, values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple.")
    for value in values:
        _required_text(name, value)


@dataclass(frozen=True, slots=True)
class ArchitectureLayer:
    """One responsibility boundary in a proposed automation architecture."""

    name: str
    responsibilities: tuple[str, ...]
    requirement_references: tuple[RequirementTraceReference, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text("name", self.name))
        _text_tuple("responsibilities", self.responsibilities)
        if not self.responsibilities:
            raise ValueError("responsibilities must not be empty.")
        _typed_tuple(
            "requirement_references", self.requirement_references, RequirementTraceReference
        )


@dataclass(frozen=True, slots=True)
class AutomationCapability:
    """A capability the proposed automation architecture is intended to provide."""

    name: str
    purpose: str
    requirement_references: tuple[RequirementTraceReference, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text("name", self.name))
        object.__setattr__(self, "purpose", _required_text("purpose", self.purpose))
        _typed_tuple(
            "requirement_references", self.requirement_references, RequirementTraceReference
        )


@dataclass(frozen=True, slots=True)
class ExecutionStrategy:
    """Proposed suite-execution directions, without execution-engine behavior."""

    parallelization: str | None = None
    browser_execution: str | None = None
    regression_execution: str | None = None
    test_distribution: str | None = None
    requirement_references: tuple[RequirementTraceReference, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "parallelization",
            "browser_execution",
            "regression_execution",
            "test_distribution",
        ):
            object.__setattr__(self, name, _optional_text(name, getattr(self, name)))
        _typed_tuple(
            "requirement_references", self.requirement_references, RequirementTraceReference
        )


@dataclass(frozen=True, slots=True)
class DeliveryStrategy:
    """Proposed CI and release-validation directions, independent of CI technology."""

    continuous_integration: str | None = None
    pull_request_validation: str | None = None
    release_validation: str | None = None
    requirement_references: tuple[RequirementTraceReference, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "continuous_integration",
            "pull_request_validation",
            "release_validation",
        ):
            object.__setattr__(self, name, _optional_text(name, getattr(self, name)))
        _typed_tuple(
            "requirement_references", self.requirement_references, RequirementTraceReference
        )


@dataclass(frozen=True, slots=True)
class ArchitectureDecision:
    """One explicit candidate decision and its architectural rationale."""

    decision: str
    rationale: str
    requirement_references: tuple[RequirementTraceReference, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision", _required_text("decision", self.decision))
        object.__setattr__(self, "rationale", _required_text("rationale", self.rationale))
        _typed_tuple(
            "requirement_references", self.requirement_references, RequirementTraceReference
        )


@dataclass(frozen=True, slots=True)
class AutomationArchitectureCandidate:
    """Immutable structured contract for a proposed automation architecture."""

    layers: tuple[ArchitectureLayer, ...] = ()
    capabilities: tuple[AutomationCapability, ...] = ()
    execution_strategy: ExecutionStrategy = field(default_factory=ExecutionStrategy)
    delivery_strategy: DeliveryStrategy = field(default_factory=DeliveryStrategy)
    assumptions: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    decisions: tuple[ArchitectureDecision, ...] = ()

    def __post_init__(self) -> None:
        _typed_tuple("layers", self.layers, ArchitectureLayer)
        _typed_tuple("capabilities", self.capabilities, AutomationCapability)
        if not isinstance(self.execution_strategy, ExecutionStrategy):
            raise TypeError("execution_strategy must be an ExecutionStrategy.")
        if not isinstance(self.delivery_strategy, DeliveryStrategy):
            raise TypeError("delivery_strategy must be a DeliveryStrategy.")
        _text_tuple("assumptions", self.assumptions)
        _text_tuple("risks", self.risks)
        _typed_tuple("decisions", self.decisions, ArchitectureDecision)
