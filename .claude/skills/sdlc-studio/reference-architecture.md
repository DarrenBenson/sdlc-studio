# SDLC Studio Reference - Architecture

Architecture decision guidance for TRD creation and review.

<!-- Load when: TRD create, TRD generate, TRD update -->

---

# Project Type Classification

Before choosing architecture patterns, identify what you're building.

## Decision Tree {#decision-tree}

```
Q1: Does this serve a web frontend (browser UI)?
    Yes -> Web Application
    No -> continue

Q2: Does this expose APIs for other systems?
    No -> Is it a library/SDK? -> SDK/Library
    No -> Desktop/CLI Application
    Yes -> continue

Q3: Will mobile apps be primary API consumers?
    Yes -> Mobile Backend
    No -> API Backend

Q4: Multiple independently deployable services?
    Yes -> Add "Monorepo" modifier
```

## Project Types {#project-types}

| Type | Description | Examples |
|------|-------------|----------|
| Web Application | Frontend + backend in one project | Dashboards, admin panels, SaaS apps |
| API Backend | REST/GraphQL API, no UI | Payment service, data processing |
| Mobile Backend | APIs designed for iOS/Android | App backends with push, offline sync |
| Desktop Application | Local app, possibly with sync | Electron apps, CLI tools |
| SDK/Library | Reusable code for developers | Python packages, npm modules |
| Monorepo | Multiple services, shared code | Platform with multiple deployables |

---

# Architecture Pattern Guidance

## Pattern-to-Project-Type Matrix {#pattern-to-project-type-matrix}

| Project Type | Default Pattern | When to Deviate |
|--------------|-----------------|-----------------|
| Web Application | Monolith | >10 developers, independent scaling needs |
| API Backend | Modular Monolith | Clear domain boundaries, separate teams |
| Mobile Backend | API Gateway + Services | Simple app (<5 endpoints) |
| Desktop Application | Layered/Clean Architecture | (rarely deviate) |
| SDK/Library | Modular with clear API | (rarely deviate) |
| Monorepo | Depends on service count | <3 services -> Modular Monolith |

## Start Simple Rule {#start-simple-rule}

> **Default to monolith unless you have specific reasons not to.**
>
> Premature decomposition is harder to fix than a monolith that needs splitting.
> "Monolith" doesn't mean "big ball of mud" - it means single deployable unit with good internal structure.

---

# Pattern Explanations

## Monolith {#monolith}

**What it is:** Single deployable unit containing all application code.

**When to use:**
- Team size <10 developers
- Single deployment target
- Shared data model across features
- Rapid iteration phase
- No independent scaling requirements

**When NOT to use:**
- Multiple teams need independent deployments
- Features have vastly different scaling needs
- Compliance requires isolation
- Different features need different tech stacks

**Key considerations:**
- Internal modularity still matters (packages, layers)
- Can evolve to microservices later if needed
- Simpler ops, debugging, and deployment

**ADRs typically needed:**
- ADR: Monolith over microservices rationale
- ADR: Internal module boundaries
- ADR: Database schema approach

## Modular Monolith {#modular-monolith}

**What it is:** Monolith with enforced module boundaries that could be split later.

**When to use:**
- Team growing beyond 5 developers
- Clear domain boundaries emerging
- Want microservices benefits without ops complexity
- Planning eventual decomposition

**When NOT to use:**
- Very small team (overhead not worth it)
- No clear domain boundaries
- No future scaling concerns

**Key considerations:**
- Modules communicate through defined interfaces
- Each module owns its data (schema per module)
- Can extract to services when needed

**ADRs typically needed:**
- ADR: Module boundary definitions
- ADR: Inter-module communication patterns
- ADR: Data ownership per module

## Microservices {#microservices}

**What it is:** Multiple independently deployable services communicating over network.

**When to use:**
- >10 developers across multiple teams
- Features require independent scaling
- Different features need different tech stacks
- Compliance requires service isolation
- Organisational structure matches service boundaries

**When NOT to use:**
- Small team (<5 developers)
- MVP or early-stage product
- Shared data model across features
- Limited ops capability

**Key considerations:**
- Requires service mesh, tracing, log aggregation
- Data consistency becomes complex
- Network failures become your problem
- CI/CD per service

**ADRs typically needed:**
- ADR: Service boundary definitions
- ADR: Inter-service communication (sync vs async)
- ADR: Data consistency strategy
- ADR: Service discovery approach
- ADR: API gateway selection

## Serverless {#serverless}

**What it is:** Functions as units of deployment, managed infrastructure.

**When to use:**
- Highly variable load
- Event-driven workloads
- Cost sensitivity with low baseline traffic
- No server management capability
- Background processing, webhooks

**When NOT to use:**
- Consistent high traffic
- Long-running processes
- Cold start latency unacceptable
- Complex stateful workflows
- Cost concerns at scale

**Key considerations:**
- Vendor lock-in
- Cold start latency
- Debugging complexity
- Cost at scale may exceed containers

**ADRs typically needed:**
- ADR: Serverless over containers rationale
- ADR: Cold start mitigation strategy
- ADR: State management approach
- ADR: Vendor selection

---

# Technology Selection

## Language Selection Matrix {#language-selection-matrix}

| Factor | Python | TypeScript | Go | Rust |
|--------|--------|------------|-----|------|
| Rapid prototyping | 3/3 | 2/3 | 1/3 | - |
| Type safety | 1/3 (with hints) | 2/3 | 3/3 | 3/3 |
| Performance | 1/3 | 1/3 | 3/3 | 3/3 |
| Web APIs | 3/3 | 3/3 | 2/3 | 1/3 |
| Data/ML | 3/3 | - | 1/3 | - |
| CLI/DevOps | 2/3 | 1/3 | 3/3 | 2/3 |
| Learning curve | Low | Low-Medium | Medium | High |

### Recommendation by Project Type {#language-recommendation}

| Project Type | Primary Recommendation | Alternative |
|--------------|----------------------|-------------|
| Web Application | Python (FastAPI) or TypeScript (Next.js) | Go for high-performance |
| API Backend | Python, TypeScript, or Go | Rust for extreme performance |
| Mobile Backend | Any (consider team skills) | Go for high concurrency |
| CLI/DevOps | Go or Python | Rust for distribution |
| High-performance | Go or Rust | - |
| Data/ML | Python | - |

### Weak Justifications to Avoid {#weak-justifications}

These are NOT sufficient rationale for technology choice:
- "Team familiarity" (only valid if learning time is critical constraint)
- "It's popular" (popularity doesn't mean fit)
- "We've always used it" (evaluate fit for this project)

### Strong Justifications {#strong-justifications}

- "Existing codebase uses X, consistency reduces cognitive load"
- "Ecosystem has required libraries (specific names)"
- "Performance requirements demand compiled language"
- "Type safety critical for domain complexity"
- "Team has 3+ years production experience, timeline is aggressive"

## Database Selection {#database-selection}

| Question | Yes -> Consider | No -> Consider |
|----------|-----------------|----------------|
| Need ACID transactions? | PostgreSQL, SQLite | MongoDB, DynamoDB |
| Flexible/evolving schema? | MongoDB | PostgreSQL |
| Self-contained deployment? | SQLite | PostgreSQL |
| Scale beyond single server? | PostgreSQL, MongoDB | SQLite |
| Complex queries/joins? | PostgreSQL | MongoDB |
| Embedded/local-first? | SQLite, DuckDB | PostgreSQL |

### Default Recommendation {#database-default}

**PostgreSQL** for most production systems - it covers 90% of use cases with:
- ACID compliance
- JSON support for flexibility
- Excellent tooling
- Proven scalability
- Extensions (pgvector, PostGIS)

**SQLite** for:
- Local-first applications
- Single-user systems
- Development/testing
- Embedded applications

## API Style Selection {#api-style-selection}

| Style | Best For | Avoid When |
|-------|----------|------------|
| REST + OpenAPI | Public APIs, mobile backends, most web apps | Real-time heavy, complex nested queries |
| GraphQL | Complex data relationships, multiple clients | Simple CRUD, internal APIs |
| gRPC | Service-to-service, high performance | Browser clients, public APIs |
| WebSocket | Real-time bidirectional | Request-response patterns |

### Default Recommendation {#database-default}

**REST with OpenAPI 3.1** - it covers 90% of use cases with:
- Excellent tooling (code generation, documentation)
- Universal client support
- Caching support
- Simple debugging

---

# Brownfield Review Checklist

For `trd generate`, assess existing architecture against best practices.

## Pattern Detection {#pattern-detection}

| Files Present | Indicates |
|---------------|-----------|
| Dockerfile, docker-compose.yml | Containerised deployment |
| serverless.yml, terraform/ | Serverless/IaC |
| /services/ or /apps/ directories | Multi-service architecture |
| /src/routes/ or /api/ | REST API patterns |
| /graphql/ | GraphQL |
| package.json + pyproject.toml | Mixed stack (may be intentional or smell) |
| /cmd/ (Go) | CLI or multi-binary |
| /internal/ (Go) | Private packages (good structure) |

## Architecture Smell Detection {#architecture-smell-detection}

| Smell | Detection | Severity |
|-------|-----------|----------|
| Big Ball of Mud | >50 files in root, no clear layers | High |
| Distributed Monolith | Services must deploy together, sync calls everywhere | High |
| Golden Hammer | One tech for everything (e.g., NoSQL for relational data) | Medium |
| Premature Decomposition | <5 developers but 10+ services | Medium |
| Missing API Gateway | Clients call multiple backends directly | Medium |
| No Error Handling | Missing try/catch, no error responses defined | High |
| Hardcoded Config | Secrets in code, no environment variables | Critical |
| Circular Dependencies | Modules import each other | High |
| God Object | Single class/module with >1000 lines | Medium |
| Missing Dependency Injection | Hard-coded dependencies throughout | Medium |

## Assessment Output Format {#assessment-output-format}

When generating a TRD for brownfield projects, include:

```markdown
## Architecture Assessment {#architecture-assessment-section}

**Detected Pattern:** {{pattern}}
**Detected Project Type:** {{type}}

### Alignment with Best Practices {#alignment-best-practices}

| Aspect | Finding | Status |
|--------|---------|--------|
| Pattern matches project type | {{analysis}} | Good/Warning/Issue |
| Clear layer separation | {{analysis}} | Good/Warning/Issue |
| API standards | {{analysis}} | Good/Warning/Issue |
| Database choice | {{analysis}} | Good/Warning/Issue |

### Architecture Smells {#architecture-smells-table}

| Smell | Found | Notes |
|-------|-------|-------|
| {{smell}} | Yes/No | {{notes}} |

### Recommendations {#architecture-recommendations}

1. [CRITICAL/REVIEW/INFO] {{recommendation}}
```

---

# Greenfield Recommendations

For `trd create`, guide users to good defaults.

## Recommendation Workflow {#recommendation-workflow}

After project type classification, present recommended stack:

```
Based on your project type ({{type}}), recommended stack:

**Architecture:** {{pattern}} ({{rationale}})
**Language:** {{language}}
**Backend:** {{framework}}
**Frontend:** {{if applicable}}
**Database:** {{database}}
**API Style:** {{style}}

Would you like to:
1. Accept these recommendations
2. Customise selections
3. Learn more about alternatives
```

## Key ADRs by Project Type {#key-adrs-by-project-type}

Prompt users to document these decisions:

### Web Application {#adrs-web-application}
- ADR: Frontend framework choice (React/Vue/Svelte)
- ADR: Backend framework choice
- ADR: Database selection
- ADR: Authentication approach
- ADR: State management (if complex)

### API Backend {#adrs-api-backend}
- ADR: API versioning strategy
- ADR: Authentication mechanism
- ADR: Rate limiting approach
- ADR: Database selection
- ADR: Error response format

### Mobile Backend {#adrs-mobile-backend}
- ADR: API versioning for backwards compatibility
- ADR: Push notification strategy
- ADR: Offline sync strategy (if needed)
- ADR: Authentication (consider refresh tokens)
- ADR: API pagination strategy

### SDK/Library {#adrs-sdk-library}
- ADR: Public API design principles
- ADR: Versioning strategy (semver)
- ADR: Dependency policy (minimal deps)
- ADR: Documentation approach

---

# API Standards Integration

Link OpenAPI best practices into TRD workflow.

## REST API Checklist {#rest-api-checklist}

When using REST, verify:

- [ ] OpenAPI 3.1.0 specification exists
- [ ] All endpoints have operationId
- [ ] Request/response schemas documented
- [ ] Error responses standardised (RFC 7807 or consistent format)
- [ ] Authentication documented
- [ ] Pagination for collections
- [ ] Versioning strategy (header, path, or query param)
- [ ] Rate limiting documented
- [ ] CORS configuration documented

## Error Response Standard {#error-response-standard}

Recommend consistent error format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": {
      "field": "email",
      "reason": "Invalid format"
    }
  }
}
```

Or RFC 7807 Problem Details:

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "The email field has an invalid format",
  "instance": "/users/123"
}
```

---

# See Also

- `reference-prd.md, reference-trd.md, reference-persona.md` - TRD create/generate/update workflows
- `best-practices/architecture.md` - Quick-reference patterns
- `best-practices/openapi.md` - OpenAPI best practices
- `templates/trd-template.md` - TRD template with architecture sections
