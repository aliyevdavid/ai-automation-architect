from app.api.schemas import (
    ApplicationProfileResponse,
    AutomationRequirementsResponse,
    CompletenessResponse,
    ConflictResponse,
    ConflictsResponse,
    ConstraintProfileResponse,
    DeliveryProfileResponse,
    EngineeringPoliciesResponse,
    EngineeringPolicyFindingResponse,
    ExecutionRequirementsResponse,
    InterfaceProfileResponse,
    NormalizationChangeResponse,
    NormalizationResponse,
    ProjectRequirementsRequest,
    ProjectRequirementsResponse,
    RequirementAnalysisResponse,
    TeamProfileResponse,
    TraceReferenceResponse,
)
from app.application import RequirementAnalysisResult
from app.domain.models import (
    ApplicationProfile,
    AutomationRequirements,
    ConstraintProfile,
    DeliveryProfile,
    ExecutionRequirements,
    InterfaceProfile,
    ProjectRequirements,
    RequirementTraceReference,
    TeamProfile,
)


def request_to_domain(request: ProjectRequirementsRequest) -> ProjectRequirements:
    """Map the closed transport request to the framework-independent aggregate."""
    return ProjectRequirements(
        application=ApplicationProfile(
            application_type=request.application.application_type,
            frontend_technology=request.application.frontend_technology,
            backend_technology=request.application.backend_technology,
            architecture_style=request.application.architecture_style,
        ),
        interfaces=InterfaceProfile(
            web_ui=request.interfaces.web_ui,
            rest_api=request.interfaces.rest_api,
            graphql=request.interfaces.graphql,
            database=request.interfaces.database,
            messaging=request.interfaces.messaging,
        ),
        automation=AutomationRequirements(
            ui_testing=request.automation.ui_testing,
            api_testing=request.automation.api_testing,
            integration_testing=request.automation.integration_testing,
            performance_testing=request.automation.performance_testing,
            accessibility_testing=request.automation.accessibility_testing,
        ),
        execution=ExecutionRequirements(
            expected_test_count=request.execution.expected_test_count,
            target_execution_minutes=request.execution.target_execution_minutes,
            parallel_execution=request.execution.parallel_execution,
            browsers=_optional_tuple(request.execution.browsers),
        ),
        delivery=DeliveryProfile(
            ci_provider=request.delivery.ci_provider,
            release_frequency=request.delivery.release_frequency,
            pull_request_validation=request.delivery.pull_request_validation,
        ),
        team=TeamProfile(
            team_size=request.team.team_size,
            languages=_optional_tuple(request.team.languages),
            automation_experience=request.team.automation_experience,
        ),
        constraints=ConstraintProfile(
            approved_technologies=_optional_tuple(request.constraints.approved_technologies),
            prohibited_technologies=_optional_tuple(request.constraints.prohibited_technologies),
            compliance_requirements=_optional_tuple(request.constraints.compliance_requirements),
        ),
    )


def _optional_tuple(values: list[str] | None) -> tuple[str, ...] | None:
    return None if values is None else tuple(values)


def _trace(reference: RequirementTraceReference) -> TraceReferenceResponse:
    return TraceReferenceResponse(field_path=reference.field_path)


def _requirements(requirements: ProjectRequirements) -> ProjectRequirementsResponse:
    return ProjectRequirementsResponse(
        application=ApplicationProfileResponse(
            application_type=requirements.application.application_type,
            frontend_technology=requirements.application.frontend_technology,
            backend_technology=requirements.application.backend_technology,
            architecture_style=requirements.application.architecture_style,
        ),
        interfaces=InterfaceProfileResponse(
            web_ui=requirements.interfaces.web_ui,
            rest_api=requirements.interfaces.rest_api,
            graphql=requirements.interfaces.graphql,
            database=requirements.interfaces.database,
            messaging=requirements.interfaces.messaging,
        ),
        automation=AutomationRequirementsResponse(
            ui_testing=requirements.automation.ui_testing,
            api_testing=requirements.automation.api_testing,
            integration_testing=requirements.automation.integration_testing,
            performance_testing=requirements.automation.performance_testing,
            accessibility_testing=requirements.automation.accessibility_testing,
        ),
        execution=ExecutionRequirementsResponse(
            expected_test_count=requirements.execution.expected_test_count,
            target_execution_minutes=requirements.execution.target_execution_minutes,
            parallel_execution=requirements.execution.parallel_execution,
            browsers=requirements.execution.browsers,
        ),
        delivery=DeliveryProfileResponse(
            ci_provider=requirements.delivery.ci_provider,
            release_frequency=requirements.delivery.release_frequency,
            pull_request_validation=requirements.delivery.pull_request_validation,
        ),
        team=TeamProfileResponse(
            team_size=requirements.team.team_size,
            languages=requirements.team.languages,
            automation_experience=requirements.team.automation_experience,
        ),
        constraints=ConstraintProfileResponse(
            approved_technologies=requirements.constraints.approved_technologies,
            prohibited_technologies=requirements.constraints.prohibited_technologies,
            compliance_requirements=requirements.constraints.compliance_requirements,
        ),
    )


def result_to_response(result: RequirementAnalysisResult) -> RequirementAnalysisResponse:
    """Map the stable application result fields to the explicit HTTP response contract."""
    normalization = result.normalization
    completeness = result.completeness
    conflicts = result.conflicts
    policies = result.engineering_policies
    return RequirementAnalysisResponse(
        normalization=NormalizationResponse(
            normalized_requirements=_requirements(normalization.normalized_requirements),
            changes=tuple(
                NormalizationChangeResponse(
                    field_path=change.field_path,
                    original_value=change.original_value,
                    normalized_value=change.normalized_value,
                    rule=change.rule.value,
                    trace_references=tuple(map(_trace, change.trace_references)),
                )
                for change in normalization.changes
            ),
        ),
        completeness=CompletenessResponse(
            required_count=completeness.required_count,
            satisfied_count=completeness.satisfied_count,
            missing_requirements=completeness.missing_requirements,
            completeness_percentage=completeness.completeness_percentage,
            is_complete=completeness.is_complete,
            missing_trace_references=tuple(map(_trace, completeness.missing_trace_references)),
        ),
        conflicts=ConflictsResponse(
            conflicts=tuple(
                ConflictResponse(
                    code=conflict.code,
                    severity=conflict.severity.value,
                    field_paths=conflict.field_paths,
                    message=conflict.message,
                    conflicting_value=conflict.conflicting_value,
                    trace_references=tuple(map(_trace, conflict.trace_references)),
                )
                for conflict in conflicts.conflicts
            ),
            conflict_count=conflicts.conflict_count,
            has_conflicts=conflicts.has_conflicts,
        ),
        engineering_policies=EngineeringPoliciesResponse(
            findings=tuple(
                EngineeringPolicyFindingResponse(
                    code=finding.code,
                    field_paths=finding.field_paths,
                    message=finding.message,
                    trace_references=tuple(map(_trace, finding.trace_references)),
                )
                for finding in policies.findings
            ),
            finding_count=policies.finding_count,
            has_findings=policies.has_findings,
        ),
    )
