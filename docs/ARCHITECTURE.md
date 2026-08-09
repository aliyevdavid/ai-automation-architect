# AI Automation Architect
## System Architecture

**Version:** 0.2
**Status:** Initial Architecture Baseline

---

## 1. Architecture Goal

The system is designed to support one primary workflow:

turn incomplete automation requirements into a technically justified, reviewable, implementation-ready automation architecture.

The architecture therefore needs to support two different types of logic:

1. deterministic engineering logic that should behave predictably
2. AI-assisted reasoning for cases where interpretation, comparison, or trade-off analysis adds value

These responsibilities should remain separated.

The platform should not depend on an LLM for behavior that can be represented as normal engineering rules.

---

## 2. Architecture Style

The initial implementation will use a modular monolith.

This is a deliberate choice.

The product is still defining its domain model, architecture policies, reasoning flow, and data contracts. Splitting these capabilities into independently deployed services at this stage would increase operational complexity before there is a demonstrated need for independent scaling or deployment.

The modular monolith provides:

- one deployable application
- explicit internal boundaries
- simpler local development
- simpler integration testing
- easier refactoring while the domain is evolving
- a practical path to future service extraction if justified

The main risk is that module boundaries can degrade over time if dependencies are not controlled.

For that reason, dependency direction and module ownership are treated as architecture constraints rather than naming conventions.

---

## 3. High-Level Structure

The initial application is divided into five primary areas:

```text
API
Application
Domain
Intelligence
Infrastructure
```

These are logical boundaries inside one deployable application.

They are not separate services.

---

## 4. API Layer

Location:

`app/api/`

Responsibilities:

- expose HTTP endpoints
- validate transport-level input
- serialize responses
- map application errors to HTTP responses
- provide dependency wiring at the API boundary

The API layer should remain thin.

It should not contain architecture selection logic, framework comparison logic, AI prompts, or persistence implementation details.

Example future endpoints include:

```text
POST /api/v1/projects
PUT  /api/v1/projects/{project_id}/requirements
POST /api/v1/projects/{project_id}/requirements/analyze
POST /api/v1/projects/{project_id}/architecture/generate
GET  /api/v1/projects/{project_id}/architecture
POST /api/v1/projects/{project_id}/architecture/approve
POST /api/v1/projects/{project_id}/blueprints
```

---

## 5. Application Layer

Location:

`app/application/`

The application layer coordinates use cases.

It should decide the order in which domain services, policies, repositories, and intelligence components participate in a workflow.

Example future use cases:

- CreateProject
- SubmitRequirements
- AnalyzeRequirements
- GenerateArchitectureProposal
- ApproveArchitecture
- GenerateBlueprint

The application layer may depend on domain abstractions and defined interfaces.

It should not contain framework-specific database code or direct OpenAI SDK calls.

A representative workflow may look like:

```text
Submit Requirements
        ->
Validate Input
        ->
Normalize Domain Model
        ->
Run Completeness Analysis
        ->
Run Deterministic Policies
        ->
Build Reasoning Context
        ->
Invoke Architecture Reasoner
        ->
Validate Recommendation
        ->
Return Architecture Proposal
```

---

## 6. Domain Layer

Location:

`app/domain/`

The domain layer contains the most stable engineering concepts in the system.

Initial domain concepts are expected to include:

- Project
- ProjectRequirements
- Constraint
- ArchitectureDecision
- ArchitectureCandidate
- Tradeoff
- Risk
- Assumption
- Blueprint
- RequirementReference

The domain layer also owns deterministic engineering rules where those rules are part of product behavior.

Examples:

- requirement completeness rules
- framework compatibility constraints
- test-volume risk thresholds
- execution-policy rules
- decision validation rules

The domain layer must not depend on:

- FastAPI
- OpenAI SDKs
- SQLAlchemy
- PostgreSQL drivers
- HTTP clients for external services
- infrastructure-specific implementations

This is intentional.

Core architecture decisions must remain testable without a running web server, database, or AI provider.

---

## 7. Intelligence Layer

Location:

`app/intelligence/`

The intelligence layer contains AI-assisted capabilities.

Its purpose is not to replace the domain layer.

Its purpose is to handle engineering tasks that benefit from contextual reasoning, such as:

- comparing viable architecture candidates
- explaining trade-offs
- identifying assumptions that are not obvious from deterministic rules
- synthesizing architecture rationale
- evaluating competing recommendations against project context

Expected future components include:

```text
providers/
reasoning/
prompts/
schemas/
```

Possible services:

- RequirementInterpreter
- CandidateGenerator
- TradeoffAnalyzer
- RiskAnalyzer
- ArchitectureReasoner

The intelligence layer should receive structured context from the application/domain layers rather than operating primarily on unbounded raw user prompts.

---

## 8. Infrastructure Layer

Location:

`app/infrastructure/`

The infrastructure layer contains technical implementations required by the rest of the system.

Future responsibilities include:

- PostgreSQL persistence
- SQLAlchemy models
- repository implementations
- Alembic migrations
- external AI provider adapters
- configuration loading
- logging configuration
- external integration clients

Infrastructure is replaceable implementation detail.

For example, the application should depend on a project repository contract rather than PostgreSQL-specific code.

Similarly, AI reasoning should depend on an AI provider abstraction rather than direct OpenAI calls spread throughout the codebase.

---

## 9. Dependency Direction

The intended dependency direction is:

```text
API
 ->
Application
 ->
Domain
```

Infrastructure implements interfaces required by inner layers.

Intelligence participates through explicit contracts and structured models.

A simplified view:

```text
                 ┌───────────────┐
                 │      API      │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Application  │
                 └───────┬───────┘
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      ┌─────────────┐         ┌──────────────┐
      │   Domain    │         │ Intelligence │
      └──────┬──────┘         └──────┬───────┘
             │                       │
             └───────────┬───────────┘
                         ▼
                 ┌───────────────┐
                 │Infrastructure │
                 └───────────────┘
```

The diagram is conceptual.

The important rule is that domain code must not become dependent on infrastructure frameworks.

---

## 10. Requirement Processing Flow

Requirements should not be sent directly from an HTTP request to an LLM.

The intended processing flow is:

```text
Raw Input
   ->
Transport Validation
   ->
ProjectRequirements Domain Model
   ->
Completeness Analysis
   ->
Conflict Detection
   ->
Normalization
   ->
Architecture Context
```

Only after the architecture context is established should higher-order reasoning begin.

This allows the system to distinguish between:

- missing information
- invalid information
- conflicting constraints
- valid architecture inputs
- preferences that should not be treated as hard constraints

---

## 11. Deterministic Policy Engine

The policy engine exists because not every architecture decision requires AI.

Where a rule can be represented explicitly and tested deterministically, it should be.

Initial policy areas may include:

- UI framework suitability
- API framework suitability
- browser compatibility
- language alignment
- execution strategy
- parallelization risk
- CI/CD compatibility
- test-layer distribution
- maintainability risk

Example:

```text
IF expected UI automation volume is high
AND target regression duration is low
THEN raise execution and maintainability risk
AND recommend evaluating more coverage at API/integration layers
```

The purpose is not to encode every architecture decision as a rule.

The purpose is to establish engineering boundaries before AI reasoning is applied.

---

## 12. AI Provider Abstraction

The platform should not couple application logic directly to OpenAI.

A provider abstraction will be introduced.

Conceptual example:

```python
from typing import Protocol

class AIProvider(Protocol):
    async def generate_architecture(
        self,
        context: ArchitectureContext,
    ) -> ArchitectureProposal:
        ...
```

Expected implementations:

```text
OpenAIProvider
MockAIProvider
```

The mock provider is important for:

- deterministic unit and integration tests
- development without API cost
- failure simulation
- schema validation
- provider-independent application behavior

A future provider can be replaced without redesigning the domain model.

---

## 13. Structured AI Contracts

AI output consumed by the application must be structured.

The system should not treat unrestricted text as an architecture decision.

A future decision contract may include:

```text
decision_id
category
recommendation
rationale
alternatives
tradeoffs
risks
assumptions
confidence
requirement_references
```

Structured contracts provide:

- validation
- consistent downstream processing
- traceability
- persistence
- comparison between architecture versions
- testability

Free-form explanation may still be included for human readability, but machine behavior must depend on validated fields.

---

## 14. Architecture Candidate Model

The system should be capable of evaluating more than one viable solution.

For example:

```text
Candidate A
Playwright + Python

Candidate B
Selenium + Java

Candidate C
Cypress + TypeScript
```

Each candidate should be evaluated against the same requirement context.

The system should avoid presenting one technology as universally superior.

Suitability depends on project constraints.

Candidate evaluation may consider:

- browser requirements
- team language capability
- existing enterprise standards
- test volume
- parallel execution needs
- debugging requirements
- API integration
- infrastructure
- maintainability
- migration cost

The final recommendation should explain why one candidate has a stronger fit for the current project.

---

## 15. Human Approval Boundary

The platform is a decision-support system.

It is not intended to autonomously approve architecture.

A future architecture lifecycle may include:

```text
Draft
  ->
Analyzed
  ->
Proposed
  ->
Approved
```

Alternative terminal states may include:

```text
Rejected
Superseded
```

AI reasoning may create a proposal.

Only an explicit application action should mark that proposal as approved.

This boundary is important for both technical accountability and auditability.

---

## 16. Persistence Strategy

Persistence is intentionally deferred until the core domain model is stable enough to justify database contracts.

The expected direction is:

- PostgreSQL
- SQLAlchemy
- Alembic

Potential persisted entities include:

- projects
- project requirements
- requirement versions
- architecture runs
- architecture candidates
- architecture decisions
- risks
- assumptions
- blueprints
- approvals

Repository abstractions should be introduced before database-specific implementations are allowed into application workflows.

---

## 17. Testing Strategy

The platform should be heavily testable without external dependencies.

Expected test categories:

### Domain Unit Tests

Validate:

- requirement models
- completeness rules
- policy logic
- risk thresholds
- decision validation

### Application Tests

Validate use-case orchestration using test doubles for infrastructure and AI providers.

### API Tests

Validate:

- endpoint contracts
- status codes
- request validation
- response schemas

### Intelligence Contract Tests

Validate:

- structured output
- schema handling
- provider failure behavior
- malformed-response handling

### Scenario Tests

Use representative project fixtures to validate end-to-end architecture reasoning behavior.

Live AI calls should not be required for the normal automated test suite.

---

## 18. Initial Technology Stack

### Runtime

- Python 3.13
- FastAPI
- Pydantic

### Testing

- pytest
- pytest-asyncio
- HTTPX

### Engineering Quality

- Ruff
- mypy
- GitHub Actions

### Planned Persistence

- PostgreSQL
- SQLAlchemy
- Alembic

### Planned AI Integration

- OpenAI API behind the AIProvider abstraction

The stack should remain small until product requirements justify additional infrastructure.

---

## 19. Architecture Risks

### Overuse of AI

Risk:

Using an LLM for decisions that should be deterministic can reduce reliability and make behavior difficult to test.

Mitigation:

Keep explicit rules in the domain/policy layer.

---

### Prompt-Driven Architecture

Risk:

Allowing raw prompts to define architecture directly may produce inconsistent recommendations.

Mitigation:

Normalize requirements into structured architecture context before AI invocation.

---

### Boundary Erosion

Risk:

A modular monolith can become tightly coupled if modules import each other's implementation details.

Mitigation:

Define explicit contracts and enforce dependency rules through code review and tests where practical.

---

### Premature Complexity

Risk:

Adding agents, vector databases, distributed services, or orchestration infrastructure too early can distract from the core product.

Mitigation:

Require a concrete product or operational need before adding architectural complexity.

---

### False Confidence

Risk:

A technically polished AI explanation may appear more certain than the available requirements justify.

Mitigation:

Represent assumptions, missing inputs, risks, and confidence explicitly.

---

## 20. Architecture Decision Rules

The following rules apply to the project unless superseded by an approved ADR:

1. Domain logic must not depend on FastAPI.
2. Domain logic must not depend on a specific AI provider.
3. AI provider calls must remain behind an abstraction.
4. Machine-consumed AI output must be structured and validated.
5. Core business behavior must be testable without network access.
6. Deterministic engineering rules should not be delegated to AI unnecessarily.
7. Architecture decisions must expose rationale and relevant trade-offs.
8. Important decisions should retain requirement traceability.
9. Human approval must remain explicit.
10. Significant architecture changes require an ADR.
11. Secrets must not be committed.
12. New domain behavior requires automated tests.

---

## 21. Planned Evolution

The expected architecture evolution is:

```text
Platform Foundation
        ->
Domain Model
        ->
Requirement Intelligence
        ->
Deterministic Policy Engine
        ->
AI Provider Abstraction
        ->
Architecture Reasoning
        ->
Trade-off and Risk Analysis
        ->
Blueprint Generation
        ->
Persistence and Versioning
        ->
Artifact Generation
        ->
Engineering Console
```

This sequence is intentional.

AI integration is not the first milestone because the platform should establish a real engineering model before introducing generative reasoning.

Future architecture changes should continue to follow the same principle:

add complexity only when a demonstrated requirement justifies it.
