from __future__ import annotations

from dataclasses import dataclass, field


def _validate_collection(name: str, values: tuple[str, ...] | None) -> None:
    if values is None:
        return
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple or None.")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} must not contain blank values.")


def _validate_optional_bool(name: str, value: bool | None) -> None:
    if value is not None and not isinstance(value, bool):
        raise TypeError(f"{name} must be a bool or None.")


def _validate_optional_int(name: str, value: int | None) -> None:
    if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
        raise TypeError(f"{name} must be an int or None.")


def _validate_optional_string(name: str, value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string or None.")
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"{name} must not be blank.")
    return normalized_value


@dataclass(frozen=True, slots=True)
class ApplicationProfile:
    """Technologies and architecture that characterize the application."""

    application_type: str | None = None
    frontend_technology: str | None = None
    backend_technology: str | None = None
    architecture_style: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "application_type",
            "frontend_technology",
            "backend_technology",
            "architecture_style",
        ):
            object.__setattr__(self, name, _validate_optional_string(name, getattr(self, name)))


@dataclass(frozen=True, slots=True)
class InterfaceProfile:
    """Interfaces exposed by the application, preserving unknown versus absent."""

    web_ui: bool | None = None
    rest_api: bool | None = None
    graphql: bool | None = None
    database: bool | None = None
    messaging: bool | None = None

    def __post_init__(self) -> None:
        for name in ("web_ui", "rest_api", "graphql", "database", "messaging"):
            _validate_optional_bool(name, getattr(self, name))


@dataclass(frozen=True, slots=True)
class AutomationRequirements:
    """Automation capabilities requested for the project."""

    ui_testing: bool | None = None
    api_testing: bool | None = None
    integration_testing: bool | None = None
    performance_testing: bool | None = None
    accessibility_testing: bool | None = None

    def __post_init__(self) -> None:
        for name in (
            "ui_testing",
            "api_testing",
            "integration_testing",
            "performance_testing",
            "accessibility_testing",
        ):
            _validate_optional_bool(name, getattr(self, name))


@dataclass(frozen=True, slots=True)
class ExecutionRequirements:
    """Test-suite scale and execution constraints."""

    expected_test_count: int | None = None
    target_execution_minutes: int | None = None
    parallel_execution: bool | None = None
    browsers: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        _validate_optional_int("expected_test_count", self.expected_test_count)
        _validate_optional_int("target_execution_minutes", self.target_execution_minutes)
        _validate_optional_bool("parallel_execution", self.parallel_execution)
        if self.expected_test_count is not None and self.expected_test_count < 0:
            raise ValueError("expected_test_count must not be negative.")
        if self.target_execution_minutes is not None and self.target_execution_minutes <= 0:
            raise ValueError("target_execution_minutes must be greater than zero.")
        _validate_collection("browsers", self.browsers)


@dataclass(frozen=True, slots=True)
class DeliveryProfile:
    """Continuous-delivery context for the project."""

    ci_provider: str | None = None
    release_frequency: str | None = None
    pull_request_validation: bool | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ci_provider",
            _validate_optional_string("ci_provider", self.ci_provider),
        )
        object.__setattr__(
            self,
            "release_frequency",
            _validate_optional_string("release_frequency", self.release_frequency),
        )
        _validate_optional_bool("pull_request_validation", self.pull_request_validation)


@dataclass(frozen=True, slots=True)
class TeamProfile:
    """Team capacity and relevant implementation experience."""

    team_size: int | None = None
    languages: tuple[str, ...] | None = None
    automation_experience: str | None = None

    def __post_init__(self) -> None:
        _validate_optional_int("team_size", self.team_size)
        if self.team_size is not None and self.team_size <= 0:
            raise ValueError("team_size must be greater than zero.")
        _validate_collection("languages", self.languages)
        object.__setattr__(
            self,
            "automation_experience",
            _validate_optional_string("automation_experience", self.automation_experience),
        )


@dataclass(frozen=True, slots=True)
class ConstraintProfile:
    """Technology and compliance constraints that recommendations must respect."""

    approved_technologies: tuple[str, ...] | None = None
    prohibited_technologies: tuple[str, ...] | None = None
    compliance_requirements: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        _validate_collection("approved_technologies", self.approved_technologies)
        _validate_collection("prohibited_technologies", self.prohibited_technologies)
        _validate_collection("compliance_requirements", self.compliance_requirements)


@dataclass(frozen=True, slots=True)
class ProjectRequirements:
    """Structured engineering context used by later architecture analysis."""

    application: ApplicationProfile = field(default_factory=ApplicationProfile)
    interfaces: InterfaceProfile = field(default_factory=InterfaceProfile)
    automation: AutomationRequirements = field(default_factory=AutomationRequirements)
    execution: ExecutionRequirements = field(default_factory=ExecutionRequirements)
    delivery: DeliveryProfile = field(default_factory=DeliveryProfile)
    team: TeamProfile = field(default_factory=TeamProfile)
    constraints: ConstraintProfile = field(default_factory=ConstraintProfile)

    def __post_init__(self) -> None:
        expected_types = (
            ("application", self.application, ApplicationProfile),
            ("interfaces", self.interfaces, InterfaceProfile),
            ("automation", self.automation, AutomationRequirements),
            ("execution", self.execution, ExecutionRequirements),
            ("delivery", self.delivery, DeliveryProfile),
            ("team", self.team, TeamProfile),
            ("constraints", self.constraints, ConstraintProfile),
        )
        for name, value, expected_type in expected_types:
            if not isinstance(value, expected_type):
                raise TypeError(f"{name} must be a {expected_type.__name__}.")
