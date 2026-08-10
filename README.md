# AI Automation Architect

AI Automation Architect is an early-stage engineering platform for turning structured test-automation requirements into deterministic, reviewable analysis.

## v0.1.0 milestone status

The current repository implements the domain foundation and the first deterministic requirement-analysis services. It does **not** yet generate automation architectures or blueprints, call an AI provider, persist project data, or expose project and requirement workflows over HTTP.

Implemented today:

- a validated `Project` domain model and lifecycle status
- structured, immutable `ProjectRequirements` profiles
- deterministic requirement completeness analysis
- deterministic detection of explicit technology conflicts
- deterministic evaluation of explicitly requested engineering capabilities
- a FastAPI application with `GET /health`
- automated tests, Ruff, strict mypy, and GitHub Actions CI

Planned capabilities are documented in the [product requirements](docs/PRODUCT_REQUIREMENTS.md), [architecture](docs/ARCHITECTURE.md), and [roadmap](docs/ROADMAP.md). Those documents describe the intended product as well as the current implementation; their status sections distinguish the two.

## Design approach

The project is designed as a modular monolith with explicit API, application, domain, intelligence, and infrastructure boundaries. At v0.1.0, substantive product behavior exists in the domain layer. The other layers are foundations for later milestones.

Deterministic rules are intentionally established before AI-assisted reasoning. This keeps requirement validation and explicit engineering policies predictable, testable, and independent of network access.

## Repository structure

```text
app/
  api/              # future HTTP workflows
  application/      # future use-case orchestration
  domain/           # implemented models and deterministic services
  infrastructure/   # future technical adapters
  intelligence/     # future AI-assisted reasoning
  main.py           # FastAPI bootstrap and health endpoint
docs/               # product, architecture, standards, roadmap, and ADRs
tests/              # health and domain unit tests
```

## Requirements and setup

- Python 3.13 or newer

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The variables in `.env.example` are reserved for future configuration work and are not currently loaded by the application. No API key is required for the v0.1.0 test suite.

## Run the service

```powershell
python -m uvicorn app.main:app --reload
```

Then request `GET http://127.0.0.1:8000/health`.

## Run quality checks

```powershell
python -m ruff check .
python -m mypy app
python -m pytest -q
```

## Domain example

```python
from app.domain.models import AutomationRequirements, ProjectRequirements
from app.domain.services import evaluate_engineering_policies

requirements = ProjectRequirements(
    automation=AutomationRequirements(api_testing=True),
)
result = evaluate_engineering_policies(requirements)

assert result.findings[0].code == "capability.api_automation_required"
```

## Project documents

- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Engineering standards](docs/ENGINEERING_STANDARDS.md)
- [Engineering roadmap](docs/ROADMAP.md)
- [Architecture decisions](docs/ADR/)
- [Security policy](SECURITY.md)
- [Contribution guide](CONTRIBUTING.md)

## Security

Do not report secrets or exploitable details in a public issue. Follow [SECURITY.md](SECURITY.md) for private reporting guidance.

## License status

No license is currently granted for this repository. All rights are reserved unless the repository owner explicitly states otherwise.
