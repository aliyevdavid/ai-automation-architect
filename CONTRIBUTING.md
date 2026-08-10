# Contributing

AI Automation Architect is currently maintained as an actively evolving engineering project. Contact the repository owner before investing in a substantial external contribution so that scope and direction can be confirmed.

## Development setup

Use Python 3.13 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quality checks

Run all checks before requesting review:

```powershell
python -m ruff check .
python -m mypy app
python -m pytest -q
```

Changes should include focused tests when behavior changes. Keep pull requests narrow and explain the problem, implementation, architecture impact, testing, trade-offs, and intentionally excluded work.

## Architecture expectations

- Keep domain code independent of FastAPI, AI provider SDKs, database libraries, and infrastructure implementations.
- Keep HTTP handlers thin and place workflow coordination in the application layer as it is introduced.
- Prefer deterministic, structured rules where normal engineering logic is sufficient.
- Record significant or difficult-to-reverse decisions in `docs/ADR/`.
- Update public documentation so implemented and planned capabilities remain unambiguous.

## Git and security

Use a focused feature branch and do not commit directly to `main`. Never commit real `.env` values, credentials, customer data, employer data, proprietary project context, or generated local artifacts. Follow [SECURITY.md](SECURITY.md) for vulnerability reports.

## Licensing

This repository does not currently grant an open-source license or general reuse rights. Submitting a proposed contribution does not change the repository's license status. Contributors must have the right to submit their work and must not include third-party or proprietary material without authorization.
