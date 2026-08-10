# AI Automation Architect
## Engineering Roadmap

**Version:** 0.1
**Status:** Active delivery plan; updated for v0.1.0

---

## Current Milestone Status

Completed for v0.1.0:

- platform bootstrap, health endpoint, quality tooling, CI, and core engineering documents
- `Project`, `ProjectStatus`, and structured `ProjectRequirements` domain models
- deterministic completeness and missing-information analysis
- deterministic detection of explicit technology conflicts
- deterministic normalization, preference-versus-constraint classification, and typed requirement traceability
- application-level deterministic requirement analysis through a versioned HTTP endpoint
- deterministic findings for explicitly requested engineering capabilities

Partially complete:

- domain foundation: later decision, risk, assumption, candidate, and blueprint models remain planned
- deterministic policy engine: the first narrow capability policies exist; broader suitability, compatibility, and risk policies remain planned

Project CRUD and workflow APIs beyond health and the versioned requirement-analysis endpoint, AI integration, multi-option candidate generation and evaluation, proposal lifecycle, blueprint generation, persistence, artifact generation, and the engineering console remain planned. A deterministic structured candidate can now be generated from analyzed engineering-policy findings.

---

## 1. Roadmap Purpose

This roadmap defines the planned engineering sequence for AI Automation Architect.

The order is intentional.

The project should prove the engineering model before adding AI complexity. Each phase should produce a working, testable increment that can stand on its own.

The guiding sequence is:

```text
Foundation
->
Domain
->
Requirement Intelligence
->
Deterministic Policies
->
AI Reasoning
->
Trade-off and Risk Analysis
->
Blueprint Generation
->
Persistence
->
Artifact Generation
->
Engineering Console
```

The roadmap should be treated as a delivery plan, not a fixed contract. Architecture decisions may change as implementation reveals better boundaries or new constraints.

---

## 2. Phase 0 - Platform Foundation

### Goal

Establish a professional, reproducible engineering baseline before implementing product behavior.

### Scope

- repository structure
- Python virtual environment
- FastAPI application bootstrap
- health endpoint
- pytest baseline
- Ruff configuration
- mypy configuration
- GitHub Actions CI
- PRD
- architecture documentation
- engineering standards
- ADR structure
- Git branching strategy
- environment configuration baseline

### Exit Criteria

Phase 0 is complete when:

- the application starts locally
- `/health` responds successfully
- baseline tests pass
- Ruff passes
- mypy passes
- CI runs automatically
- core engineering documentation exists
- first ADR exists
- feature branch workflow is verified

### Intentionally Out of Scope

- AI integration
- persistence
- project domain behavior
- requirement analysis
- architecture recommendations

---

## 3. Phase 1 - Domain Foundation

### Goal

Define the core engineering concepts without depending on FastAPI, databases, or AI providers.

### Domain Models

- Project (implemented)
- ProjectStatus (implemented)
- ProjectRequirements (implemented)
- ApplicationProfile (implemented)
- InterfaceProfile (implemented)
- AutomationRequirements (implemented)
- ExecutionRequirements (implemented)
- DeliveryProfile (implemented)
- TeamProfile (implemented)
- Constraint
- RequirementReference
- ArchitectureDecision
- ArchitectureCandidate
- Risk
- Assumption
- Tradeoff
- Blueprint

### Engineering Focus

This phase should establish:

- clear domain boundaries
- explicit types
- validation rules
- stable naming
- testable domain behavior

### Exit Criteria

- primary domain models are implemented
- models have unit tests
- domain package does not import FastAPI
- domain package does not import OpenAI
- domain package does not depend on database libraries
- representative project fixtures exist

---

## 4. Phase 2 - Requirement Intelligence

**Status:** Complete for the currently defined scope and exit criteria.

### Goal

Convert submitted project information into reliable architecture context.

### Capabilities

- requirement validation (implemented for the current structured requirement model)
- completeness scoring (implemented)
- missing-information detection (implemented)
- conflict detection (implemented for currently defined explicit technology contradiction policies)
- normalization (implemented)
- preference-versus-constraint distinction (implemented for explicit structured fields)
- requirement traceability (implemented)

### Example

Input:

```text
We want Selenium.
We have 1,500 regression scenarios.
Nightly execution must finish quickly.
Chrome and Edge are required.
The team has strong Python experience.
```

The system should not immediately approve Selenium.

It should first determine:

- whether enough information exists
- whether the framework request is a preference or hard constraint
- which important inputs are still missing

Later deterministic engineering policies use this normalized context to determine implications such as whether test volume introduces execution risk or browser requirements are supported. Those suitability and risk policies are not Phase 2 completion requirements.

### Exit Criteria

- requirements can be submitted through domain/application services
- completeness score is deterministic
- missing fields are reported
- conflicts are reported
- normalized architecture context is produced
- no AI dependency is required

---

## 5. Phase 3 - API Foundation for Projects and Requirements

### Goal

Expose the domain and requirement workflows through stable HTTP contracts.

### Planned Endpoints

```text
POST /api/v1/projects
GET  /api/v1/projects/{project_id}

PUT  /api/v1/projects/{project_id}/requirements
GET  /api/v1/projects/{project_id}/requirements

POST /api/v1/projects/{project_id}/requirements/analyze
```

### Engineering Focus

- thin API layer
- clear request/response contracts
- application-service orchestration
- controlled error handling
- API tests

### Exit Criteria

- project creation works through HTTP
- requirements can be submitted
- requirement analysis can be requested
- invalid requests produce controlled errors
- endpoint behavior is covered by tests

---

## 6. Phase 4 - Deterministic Architecture Policy Engine

### Goal

Introduce explicit engineering rules before introducing generative reasoning.

### Initial Policy Areas

- UI framework suitability
- API framework suitability
- browser compatibility
- team-language alignment
- test-volume risk
- execution strategy
- parallelization
- CI/CD compatibility
- test-layer distribution
- maintainability risk

### Example Policy

```text
IF UI test volume is high
AND target runtime is aggressive
THEN raise execution risk
AND recommend shifting suitable coverage to API or integration layers
```

### Design Requirement

Policies should return structured results rather than plain text.

Example output concepts:

- policy identifier
- status
- rationale
- severity
- related requirements
- recommendation impact

### Exit Criteria

- policy abstraction exists
- multiple policies can run against one architecture context
- results are deterministic
- results are unit tested
- policy outputs can be consumed by later AI reasoning

---

## 7. Phase 5 - Architecture Candidate Generation

### Goal

Generate multiple technically viable options rather than jumping directly to one recommendation.

### Initial Candidate Categories

#### UI Automation

- Playwright
- Selenium
- Cypress

#### API Automation

- Playwright API
- Python HTTP client approach
- REST Assured
- Karate

#### Language

- Python
- Java
- TypeScript

#### CI/CD

- Jenkins
- GitHub Actions
- Azure DevOps

### Candidate Evaluation Factors

- application type
- browser requirements
- team skills
- enterprise standards
- execution volume
- target runtime
- API requirements
- infrastructure
- maintainability
- migration cost

### Exit Criteria

- candidate model is implemented
- at least two viable candidates can be generated for supported scenarios
- unsupported combinations are filtered or flagged
- candidate reasoning inputs are testable without AI

---

## 8. Phase 6 - AI Provider Abstraction

### Goal

Introduce AI without coupling the application to a specific provider.

### Planned Components

```text
AIProvider
MockAIProvider
OpenAIProvider
```

### Responsibilities

The provider layer should handle:

- provider communication
- timeout handling
- retry behavior
- structured response parsing
- malformed output handling
- provider-specific errors

### Testing Requirement

Normal automated test runs must use `MockAIProvider` or controlled fixtures.

Live provider calls should be isolated from standard unit tests.

### Exit Criteria

- provider abstraction exists
- mock provider works
- application behavior can be tested without network access
- OpenAI integration is behind the abstraction
- provider failures are controlled

---

## 9. Phase 7 - AI Architecture Reasoning

### Goal

Use AI for higher-order comparison and explanation after deterministic context is established.

### Planned Reasoning Flow

```text
Normalized Requirements
->
Policy Results
->
Architecture Candidates
->
Reasoning Context
->
AI Architecture Reasoner
->
Structured Proposal
->
Validation
```

### AI Responsibilities

AI may assist with:

- comparing viable candidates
- synthesizing rationale
- identifying assumptions
- explaining trade-offs
- identifying contextual risks
- ranking recommendations

### AI Non-Responsibilities

AI should not be solely responsible for:

- required-field validation
- unsupported combinations
- basic compatibility rules
- approval state
- unvalidated final architecture

### Exit Criteria

- structured proposal schema exists
- reasoning output references project context
- alternatives are included
- rationale is included
- confidence is represented
- malformed AI output is rejected
- deterministic policies remain visible in the final proposal

---

## 10. Phase 8 - Trade-off and Risk Intelligence

### Goal

Make recommendations challengeable and explainable.

### Planned Trade-off Model

A comparison should include areas such as:

- implementation effort
- maintainability
- execution performance
- team adoption cost
- CI/CD fit
- debugging experience
- ecosystem maturity
- migration cost
- long-term scalability

### Planned Risk Model

Each risk should support:

- risk identifier
- description
- severity
- probability
- mitigation
- requirement references
- source

Possible sources:

- deterministic policy
- AI reasoning
- human input

### Exit Criteria

- candidate trade-offs are structured
- risks are structured
- risks can be traced to requirements
- mitigations are represented
- final recommendation is not presented without known material trade-offs

---

## 11. Phase 9 - Architecture Proposal Lifecycle

### Goal

Introduce explicit lifecycle and human approval.

### Planned States

```text
Draft
->
Analyzed
->
Proposed
->
Approved
```

Additional states:

```text
Rejected
Superseded
```

### Planned Capabilities

- generate architecture proposal
- retrieve proposal
- approve proposal
- reject proposal
- supersede previous proposal
- retain decision rationale

### Exit Criteria

- proposal state changes are explicit
- invalid transitions are rejected
- AI cannot mark a proposal approved
- approval is represented as an application action
- lifecycle behavior has unit tests

---

## 12. Phase 10 - Blueprint Generation

### Goal

Turn an approved architecture proposal into an implementation-ready blueprint.

### Blueprint Sections

The first blueprint format should include:

- project summary
- requirements summary
- recommended automation stack
- test-layer strategy
- UI automation architecture
- API automation architecture
- repository structure
- execution model
- parallelization approach
- CI/CD integration
- configuration strategy
- test data strategy
- reporting strategy
- observability
- risks
- assumptions
- architecture decisions
- implementation phases

### Exit Criteria

- approved proposal can generate a blueprint
- blueprint is structured
- blueprint can be rendered for human review
- blueprint contains requirement traceability
- blueprint does not depend on unapproved AI output

---

## 13. Phase 11 - Persistence and Versioning

### Goal

Make architecture work durable and auditable.

### Planned Stack

- PostgreSQL
- SQLAlchemy
- Alembic

### Planned Persisted Data

- projects
- project requirements
- requirement versions
- policy results
- architecture candidates
- architecture runs
- decisions
- risks
- assumptions
- proposals
- approvals
- blueprints

### Versioning Goals

The system should eventually answer:

- what requirements existed at the time of a recommendation?
- what changed between architecture versions?
- why was a previous architecture superseded?
- which decision changed?
- who approved the current blueprint?

### Exit Criteria

- repository abstractions exist
- PostgreSQL implementation exists
- migrations are automated
- architecture history is retained
- application tests can still use non-production repository implementations

---

## 14. Phase 12 - Starter Artifact Generation

### Goal

Convert approved architecture into implementation accelerators.

### Initial Artifacts

Potential outputs:

- repository folder structure
- configuration templates
- test package skeletons
- CI/CD templates
- example environment configuration
- README template
- framework bootstrap

### Example

An approved Playwright + Python blueprint may generate:

```text
tests/
pages/
api/
fixtures/
config/
utils/
reporting/
```

The first implementation should generate structure and safe starter files rather than autonomous production code.

### Exit Criteria

- artifact generation depends on approved blueprint data
- generated output is deterministic where possible
- generated files can be validated automatically
- generation does not overwrite user code without explicit action

---

## 15. Phase 13 - Engineering Console

### Goal

Add a web interface after the backend decision workflow is mature.

### Planned Screens

- Projects
- Requirement Intake
- Requirement Analysis
- Architecture Candidates
- Trade-off Matrix
- Risk Register
- Architecture Proposal
- Approval
- Blueprint
- Generated Artifacts

### UI Principle

The interface should resemble an engineering console, not a chatbot.

The primary interaction model should be structured forms, decision views, comparison views, and review workflows.

Natural-language assistance may be added where useful, but it should not replace the structured engineering flow.

### Exit Criteria

- major backend capabilities are accessible through the UI
- architecture decisions remain structured
- users can review rationale and traceability
- approval remains explicit

---

## 16. Scenario-Driven Development

A permanent representative project scenario should be introduced early and reused as the platform evolves.

Initial scenario:

```text
Application:
React web application

Backend:
Java REST services

Database:
PostgreSQL

Infrastructure:
AWS

CI/CD:
Jenkins

Browsers:
Chrome
Edge

Regression Volume:
Approximately 1,500 scenarios

Execution:
PR smoke suite
Nightly regression

Team:
3 automation engineers
Strong Python experience
```

This fixture should evolve into a scenario test that exercises:

```text
Requirements
->
Completeness Analysis
->
Normalization
->
Policy Evaluation
->
Candidate Generation
->
AI Reasoning
->
Trade-off Analysis
->
Risk Analysis
->
Architecture Proposal
->
Blueprint
```

This scenario becomes the primary end-to-end product demonstration.

---

## 17. Delivery Strategy

Development should proceed through focused feature branches and pull requests.

Preferred pattern:

```text
Architecture Decision
->
GitHub Issue
->
Feature Branch
->
Implementation
->
Automated Tests
->
Pull Request
->
CI
->
Merge to develop
```

Each implementation issue should be narrow enough that its architectural impact can be reviewed clearly.

---

## 18. Initial GitHub Milestones

Suggested milestones:

### Milestone 1
Platform Foundation

### Milestone 2
Domain and Requirement Intelligence

### Milestone 3
Architecture Policy Engine

### Milestone 4
AI Reasoning Foundation

### Milestone 5
Trade-off and Risk Intelligence

### Milestone 6
Blueprint Generation

### Milestone 7
Persistence and Auditability

### Milestone 8
Artifact Generation

### Milestone 9
Engineering Console

---

## 19. Near-Term Development Order

The next implementation priorities after v0.1.0 should be:

```text
1. Add a representative scenario fixture
2. Define application services for project and requirement workflows
3. Expose project and requirements APIs
4. Expose deterministic requirement analysis through an API
5. Expand deterministic requirement intelligence beyond normalization and explicit preference-versus-constraint modeling
6. Define ArchitectureDecision and ArchitectureCandidate models
7. Expand deterministic policies beyond capability findings
8. Preserve requirement traceability in structured results
```

AI integration should not begin before the requirement model and first deterministic policies are stable.

---

## 20. Roadmap Review Rule

The roadmap should be revisited when:

- a major architecture assumption changes
- a phase reveals a better domain boundary
- implementation complexity is materially different from expected
- a new requirement changes the delivery order
- a planned technology no longer fits the architecture
- product clarity and engineering value can be improved without compromising engineering quality

The roadmap is intended to keep development deliberate.

It should not prevent better engineering decisions when new evidence appears.
