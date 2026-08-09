from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Base configuration for the intentionally closed HTTP contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


class ApplicationProfileRequest(ApiModel):
    application_type: str | None = None
    frontend_technology: str | None = None
    backend_technology: str | None = None
    architecture_style: str | None = None


class InterfaceProfileRequest(ApiModel):
    web_ui: bool | None = None
    rest_api: bool | None = None
    graphql: bool | None = None
    database: bool | None = None
    messaging: bool | None = None


class AutomationRequirementsRequest(ApiModel):
    ui_testing: bool | None = None
    api_testing: bool | None = None
    integration_testing: bool | None = None
    performance_testing: bool | None = None
    accessibility_testing: bool | None = None


class ExecutionRequirementsRequest(ApiModel):
    expected_test_count: int | None = None
    target_execution_minutes: int | None = None
    parallel_execution: bool | None = None
    browsers: list[str] | None = None


class DeliveryProfileRequest(ApiModel):
    ci_provider: str | None = None
    release_frequency: str | None = None
    pull_request_validation: bool | None = None


class TeamProfileRequest(ApiModel):
    team_size: int | None = None
    languages: list[str] | None = None
    automation_experience: str | None = None


class ConstraintProfileRequest(ApiModel):
    approved_technologies: list[str] | None = None
    prohibited_technologies: list[str] | None = None
    compliance_requirements: list[str] | None = None


class ProjectRequirementsRequest(ApiModel):
    application: ApplicationProfileRequest = Field(default_factory=ApplicationProfileRequest)
    interfaces: InterfaceProfileRequest = Field(default_factory=InterfaceProfileRequest)
    automation: AutomationRequirementsRequest = Field(
        default_factory=AutomationRequirementsRequest
    )
    execution: ExecutionRequirementsRequest = Field(default_factory=ExecutionRequirementsRequest)
    delivery: DeliveryProfileRequest = Field(default_factory=DeliveryProfileRequest)
    team: TeamProfileRequest = Field(default_factory=TeamProfileRequest)
    constraints: ConstraintProfileRequest = Field(default_factory=ConstraintProfileRequest)


class ApplicationProfileResponse(ApiModel):
    application_type: str | None
    frontend_technology: str | None
    backend_technology: str | None
    architecture_style: str | None


class InterfaceProfileResponse(ApiModel):
    web_ui: bool | None
    rest_api: bool | None
    graphql: bool | None
    database: bool | None
    messaging: bool | None


class AutomationRequirementsResponse(ApiModel):
    ui_testing: bool | None
    api_testing: bool | None
    integration_testing: bool | None
    performance_testing: bool | None
    accessibility_testing: bool | None


class ExecutionRequirementsResponse(ApiModel):
    expected_test_count: int | None
    target_execution_minutes: int | None
    parallel_execution: bool | None
    browsers: tuple[str, ...] | None


class DeliveryProfileResponse(ApiModel):
    ci_provider: str | None
    release_frequency: str | None
    pull_request_validation: bool | None


class TeamProfileResponse(ApiModel):
    team_size: int | None
    languages: tuple[str, ...] | None
    automation_experience: str | None


class ConstraintProfileResponse(ApiModel):
    approved_technologies: tuple[str, ...] | None
    prohibited_technologies: tuple[str, ...] | None
    compliance_requirements: tuple[str, ...] | None


class ProjectRequirementsResponse(ApiModel):
    application: ApplicationProfileResponse
    interfaces: InterfaceProfileResponse
    automation: AutomationRequirementsResponse
    execution: ExecutionRequirementsResponse
    delivery: DeliveryProfileResponse
    team: TeamProfileResponse
    constraints: ConstraintProfileResponse


class TraceReferenceResponse(ApiModel):
    field_path: str


class NormalizationChangeResponse(ApiModel):
    field_path: str
    original_value: str
    normalized_value: str
    rule: str
    trace_references: tuple[TraceReferenceResponse, ...]


class NormalizationResponse(ApiModel):
    normalized_requirements: ProjectRequirementsResponse
    changes: tuple[NormalizationChangeResponse, ...]


class CompletenessResponse(ApiModel):
    required_count: int
    satisfied_count: int
    missing_requirements: tuple[str, ...]
    completeness_percentage: float
    is_complete: bool
    missing_trace_references: tuple[TraceReferenceResponse, ...]


class ConflictResponse(ApiModel):
    code: str
    severity: str
    field_paths: tuple[str, ...]
    message: str
    conflicting_value: str
    trace_references: tuple[TraceReferenceResponse, ...]


class ConflictsResponse(ApiModel):
    conflicts: tuple[ConflictResponse, ...]
    conflict_count: int
    has_conflicts: bool


class EngineeringPolicyFindingResponse(ApiModel):
    code: str
    field_paths: tuple[str, ...]
    message: str
    trace_references: tuple[TraceReferenceResponse, ...]


class EngineeringPoliciesResponse(ApiModel):
    findings: tuple[EngineeringPolicyFindingResponse, ...]
    finding_count: int
    has_findings: bool


class RequirementAnalysisResponse(ApiModel):
    normalization: NormalizationResponse
    completeness: CompletenessResponse
    conflicts: ConflictsResponse
    engineering_policies: EngineeringPoliciesResponse
