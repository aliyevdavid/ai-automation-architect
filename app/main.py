from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="AI Automation Architect",
    description=(
        "Early-stage engineering service with a deterministic domain foundation "
        "for structured test-automation requirement analysis."
    ),
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return basic service health information."""
    return {
        "status": "healthy",
        "service": "ai-automation-architect",
    }
