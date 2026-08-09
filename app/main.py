from fastapi import FastAPI

app = FastAPI(
    title="AI Automation Architect",
    description=(
        "AI-assisted engineering platform for automation architecture "
        "analysis and blueprint generation."
    ),
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return basic service health information."""
    return {
        "status": "healthy",
        "service": "ai-automation-architect",
    }
