# AI Automation Architect
## Engineering Standards

**Version:** 0.1
**Status:** Initial Engineering Baseline

---

## 1. Purpose

This document defines the engineering standards for the AI Automation Architect project.

The purpose is not to create process for its own sake.

These standards exist to protect the architecture from becoming inconsistent as the platform grows, especially once AI integration, persistence, and blueprint generation are introduced.

The project should remain:

- understandable
- testable
- reviewable
- modular
- reproducible
- explainable
- safe to extend

---

## 2. Engineering Principles

### Prefer Explicit Design Over Hidden Behavior

Core system behavior should be understandable from code, contracts, tests, and documentation.

Avoid designs that depend on implicit side effects or undocumented conventions.

---

### Keep AI Behind Engineering Boundaries

AI must participate through explicit interfaces and structured contracts.

The rest of the application should not depend on provider-specific SDK behavior.

---

### Use Deterministic Logic Where It Is Stronger

If a rule can be expressed clearly and tested deterministically, it should not be delegated to AI without a concrete reason.

Examples:

- required fields
- compatibility checks
- threshold-based risks
- schema validation
- state transitions

---

### Optimize for Maintainability

The project should favor designs that are easy to reason about and extend.

Avoid introducing architecture complexity only because it is technically possible.

---

## 3. Python Standards

Python 3.13 is the baseline runtime.

Application code should:

- use type hints
- use descriptive names
- keep functions focused
- avoid unnecessary inheritance
- avoid deeply nested control flow where practical
- avoid duplicate business logic
- separate domain behavior from framework-specific code
- avoid dead code

Public functions and classes should be understandable without requiring implementation-level guesswork.

---

## 4. Module Boundaries

The project uses the following primary modules:

```text
app/api/
app/application/
app/domain/
app/intelligence/
app/infrastructure/
```

These directories represent architecture boundaries.

They are not just organizational folders.

### API

May depend on:

- application contracts
- request/response schemas
- dependency wiring

Must not own:

- architecture reasoning
- domain rules
- provider-specific AI logic
- database implementation details

---

### Application

May depend on:

- domain models
- domain services
- repository abstractions
- intelligence abstractions

Should coordinate use cases.

It should not contain low-level infrastructure code.

---

### Domain

May contain:

- entities
- value objects
- domain models
- deterministic policies
- domain validation
- decision rules

Must not depend on:

- FastAPI
- OpenAI
- SQLAlchemy
- external HTTP clients
- PostgreSQL-specific libraries

---

### Intelligence

May contain:

- AI provider contracts
- structured AI schemas
- reasoning orchestration
- trade-off analysis
- prompt templates
- AI validation behavior

AI behavior must remain structured and testable.

---

### Infrastructure

May contain:

- database implementations
- repository implementations
- AI provider adapters
- external service clients
- configuration implementations
- logging setup

Infrastructure should implement contracts defined by inner layers where practical.

---

## 5. Type Safety

Type hints are required for application code.

The project uses mypy as a static type checker.

Code should avoid using `Any` unless there is a justified boundary where a stronger type is not practical.

If `Any` is required:

- keep it localized
- document why it is required
- convert it into a known type as soon as possible

---

## 6. Data Models and Schemas

Pydantic should be used for structured application and API data where appropriate.

Domain concepts should not become tightly coupled to transport concerns.

For example:

- an HTTP request model is not automatically the domain model
- an OpenAI response model is not automatically an approved architecture decision
- a database row is not automatically the domain entity

Mappings between layers should remain explicit when the models have different responsibilities.

---

## 7. AI Engineering Standards

AI integration is one of the highest-risk areas for architectural drift.

The following rules apply.

### Provider Abstraction

Direct provider SDK calls should be isolated behind an AI provider interface.

Application and domain code should not call OpenAI directly.

---

### Structured Output

Machine-consumed AI output must use structured schemas.

Do not base application decisions on unrestricted natural-language output.

---

### Validation

AI output must be validated before it enters application workflows.

Validation should cover:

- schema correctness
- required fields
- confidence ranges
- supported decision categories
- malformed responses
- unsupported recommendations where applicable

---

### Failure Handling

AI integrations must account for:

- timeouts
- rate limits
- malformed output
- empty responses
- provider errors
- retry limits

Failures must not silently produce approved architecture.

---

### Mockability

Normal unit and integration tests should not require live AI API calls.

A mock or fake provider should be available for deterministic testing.

---

### Prompt Ownership

Prompts are part of application behavior and should be version-controlled.

Prompt changes that materially affect system behavior should be reviewed like code changes.

---

## 8. Testing Standards

pytest is the primary test framework.

Tests should be deterministic and should explain behavior clearly.

### Unit Tests

Use for:

- domain rules
- completeness logic
- risk thresholds
- policy evaluation
- validation behavior
- state transitions

---

### Application Tests

Use for:

- workflow orchestration
- dependency interactions
- repository contracts
- AI provider interaction through mocks or fakes

---

### API Tests

Use for:

- endpoint behavior
- request validation
- response schemas
- status codes
- error mapping

---

### Intelligence Tests

Use for:

- schema parsing
- malformed AI output
- provider failure behavior
- reasoning contract validation

---

### Scenario Tests

Use representative project fixtures for broader behavior.

A scenario test should model a real engineering case rather than a synthetic one-line input.

---

## 9. Test Naming

Test names should describe behavior.

Prefer:

```text
test_missing_browser_requirement_reduces_completeness_score
test_high_ui_volume_raises_maintainability_risk
test_ai_provider_timeout_returns_controlled_application_error
```

Avoid:

```text
test_case_1
test_method
test_api
```

---

## 10. Code Quality Tooling

The initial quality toolchain is:

- Ruff
- mypy
- pytest

Before code is considered ready for review, these commands should pass:

```powershell
python -m ruff check .
python -m mypy app
python -m pytest -q
```

As the project grows, additional checks may be added when justified.

---

## 11. Formatting and Linting

Ruff is the primary linting tool.

Lint rules should support readability and consistency without becoming unnecessarily restrictive.

Do not disable lint rules globally just to make checks pass.

If a rule needs to be ignored:

- keep the ignore local where possible
- document the reason if it is not obvious

---

## 12. Git Branching

Primary long-lived branches:

```text
main
develop
```

Feature work should use branches such as:

```text
feature/day-01-platform-foundation
feature/project-domain-model
feature/requirement-completeness-engine
feature/ai-provider-abstraction
```

Feature work should not be committed directly to `main`.

---

## 13. Commit Messages

Commit messages should explain the engineering intent of the change.

Preferred examples:

```text
feat: add project requirements domain model
feat: implement requirement completeness policy
test: add high-volume execution risk scenarios
docs: document AI provider abstraction
refactor: isolate architecture decision validation
fix: reject unsupported decision categories
```

Avoid vague messages such as:

```text
changes
updates
fix stuff
work
misc
```

---

## 14. Pull Request Standards

A pull request should explain:

### Problem

What engineering problem is being solved?

### Implementation

What changed?

### Architecture Impact

Did the change affect module boundaries, contracts, data flow, persistence, AI behavior, or dependencies?

### Testing

How was the change verified?

### Trade-offs

Were alternatives considered?

### Out of Scope

What was intentionally not included?

A pull request should remain focused enough to review confidently.

---

## 15. Architecture Decision Records

Significant architecture decisions should be recorded under:

```text
docs/ADR/
```

An ADR is appropriate when a change affects areas such as:

- architecture style
- dependency direction
- persistence strategy
- provider abstraction
- AI contract design
- approval workflow
- major infrastructure choices
- cross-cutting engineering patterns

ADRs should capture:

- context
- decision
- alternatives considered where relevant
- consequences
- future review conditions

---

## 16. Security Standards

Secrets must never be committed.

This includes:

- API keys
- access tokens
- passwords
- connection strings containing credentials
- private certificates
- sensitive environment values

Secrets should be injected through environment variables or secure runtime configuration.

`.env` files containing real values should remain excluded from Git.

Example files should contain placeholders only.

---

## 17. Logging Standards

Logging should support debugging without exposing sensitive data.

Logs should avoid:

- secrets
- access tokens
- full credentials
- unnecessary personally identifiable information

Future AI logging should be handled carefully because prompts and responses may contain sensitive project context.

Logging should favor structured, searchable fields where practical.

---

## 18. Error Handling

Errors should be explicit.

Avoid broad exception handling such as:

```python
try:
    ...
except Exception:
    pass
```

Application errors should preserve useful context while preventing implementation details from leaking through external APIs.

Provider and infrastructure failures should be translated into application-level errors where appropriate.

---

## 19. Dependency Management

New dependencies should be added only when they provide clear value.

Before introducing a dependency, consider:

- whether the standard library is sufficient
- maintenance activity
- security posture
- compatibility with Python 3.13
- transitive dependency cost
- whether the dependency leaks into core domain code

Avoid adding libraries only for convenience when the problem is small.

---

## 20. Configuration

Configuration should be centralized.

Environment-specific behavior should not be scattered throughout the codebase.

Expected configuration categories may include:

- application environment
- logging level
- database settings
- AI provider
- AI model
- timeout settings
- retry settings

Real secrets must not be stored in source-controlled configuration files.

---

## 21. Documentation Standards

Documentation should explain engineering intent.

Avoid documentation that only repeats what the code already says.

Useful documentation should answer:

- why was this designed this way?
- what constraints influenced the decision?
- what alternatives were considered?
- what should a future engineer avoid breaking?
- when should the decision be revisited?

---

## 22. Definition of Done

A feature is complete when applicable criteria are satisfied:

1. implementation is complete
2. automated tests are added
3. existing tests pass
4. Ruff passes
5. mypy passes
6. architecture boundaries are preserved
7. documentation is updated where needed
8. ADRs are added for significant architecture decisions
9. no secrets are introduced
10. the pull request explains the change
11. known trade-offs are documented
12. out-of-scope work is identified

---

## 23. Review Expectations

Code review should focus on more than syntax.

Reviewers should consider:

- does this belong in the selected module?
- is the dependency direction correct?
- is deterministic logic being delegated to AI unnecessarily?
- is the behavior testable without external services?
- are contracts explicit?
- does the change introduce hidden coupling?
- is the implementation more complex than the requirement justifies?
- can the decision be explained in an interview or architecture review?

The project should remain easy to defend technically as it evolves.
