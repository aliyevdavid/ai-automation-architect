from fastapi import APIRouter, HTTPException, status

from app.api.mappings import request_to_domain, result_to_response
from app.api.schemas import ProjectRequirementsRequest, RequirementAnalysisResponse
from app.application import analyze_project_requirements

router = APIRouter(prefix="/requirements", tags=["requirements"])


@router.post(
    "/analyze",
    response_model=RequirementAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze project requirements",
    description="Run deterministic requirement normalization and analysis.",
)
def analyze_requirements(request: ProjectRequirementsRequest) -> RequirementAnalysisResponse:
    """Analyze one requirement set through the application orchestration boundary."""
    try:
        requirements = request_to_domain(request)
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return result_to_response(analyze_project_requirements(requirements))
