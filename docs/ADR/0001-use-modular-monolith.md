# ADR-0001: Use a Modular Monolith

**Status:** Accepted
**Date:** 2026-08-08

---

## Context

AI Automation Architect is expected to grow across several areas:

- requirement intake
- requirement intelligence
- deterministic architecture policies
- AI-assisted reasoning
- trade-off analysis
- risk analysis
- blueprint generation
- persistence
- artifact generation
- a future engineering console

It would be possible to implement these capabilities as separate services from the beginning.

However, the product is still defining its core domain model, internal contracts, reasoning flow, and boundaries.

Introducing microservices at this stage would add:

- deployment complexity
- service-to-service communication
- distributed tracing needs
- versioned API contracts
- more difficult local development
- more difficult integration testing
- operational overhead that is not yet justified by product requirements

The project currently has no demonstrated need for independent scaling, independent deployment, or separate team ownership across services.

---

## Decision

The platform will begin as a modular monolith.

The application will be deployed as one unit while maintaining explicit internal boundaries between:

```text
API
Application
Domain
Intelligence
Infrastructure
```

These boundaries are architectural constraints, not just folder names.

The domain layer must remain independent from FastAPI, AI provider SDKs, database libraries, and external infrastructure implementations.

Infrastructure and AI providers will be accessed through explicit contracts where appropriate.

---

## Alternatives Considered

### Microservices

Advantages:

- independent deployment
- independent scaling
- strong runtime separation
- clearer ownership boundaries in large teams

Reasons not selected now:

- no current independent scaling requirement
- no current independent deployment requirement
- unnecessary network and operational complexity
- domain boundaries are still evolving
- higher testing and debugging cost
- slower iteration during early product development

---

### Single Unstructured Application

Advantages:

- fastest initial implementation
- minimal setup

Reasons not selected:

- high risk of business logic leaking into API handlers
- high risk of direct AI and database coupling
- difficult future refactoring
- poor fit for an architecture-focused portfolio project
- weak separation between deterministic and AI-assisted behavior

---

## Consequences

### Positive

- simpler local development
- one deployable application
- easier end-to-end testing
- lower infrastructure overhead
- easier refactoring while the product domain evolves
- clear path to future service extraction if justified
- better control over dependency direction

### Negative

- internal boundaries depend on engineering discipline
- modules still share one process and deployment unit
- poorly controlled imports could create hidden coupling
- future service extraction may require refactoring

---

## Guardrails

The modular monolith must preserve the following rules:

1. Domain code must not depend on FastAPI.
2. Domain code must not depend on OpenAI or another provider SDK.
3. Domain code must not depend on database implementations.
4. API handlers must remain thin.
5. Application services coordinate workflows rather than owning low-level infrastructure logic.
6. Infrastructure implements technical adapters and external integrations.
7. Significant cross-module dependencies should be explicit and reviewable.
8. New architecture complexity must be justified by a concrete requirement.

---

## Revisit This Decision When

This ADR should be revisited if one or more of the following becomes true:

- a module requires independent scaling
- a capability requires independent deployment
- different teams own different runtime boundaries
- reliability isolation becomes necessary
- release cadence differs materially between major modules
- infrastructure load characteristics differ enough to justify service separation
- the modular monolith becomes difficult to maintain despite enforced boundaries

Until one of these conditions is demonstrated, the added complexity of microservices is not justified.
