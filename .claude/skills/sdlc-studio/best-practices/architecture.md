# Architecture Best Practices

Quick-reference guide for architecture decisions.

---

## Project Type Quick Reference

| Type | Default Pattern | Default Language | Default Database |
|------|-----------------|------------------|------------------|
| Web Application | Monolith | Python/TypeScript | PostgreSQL |
| API Backend | Modular Monolith | Python/TypeScript/Go | PostgreSQL |
| Mobile Backend | Monolith | Python/Go | PostgreSQL |
| CLI Tool | Layered | Go/Python | SQLite (if any) |
| SDK/Library | Modular | Matches ecosystem | N/A |

---

## Pattern Selection

### When to Use Monolith

- Team size <10 developers
- Shared data model across features
- Single deployment target
- Rapid iteration phase
- MVP or early-stage product

### When to Use Microservices

- >10 developers across multiple teams
- Independent scaling required
- Compliance requires isolation
- Different tech stacks per feature
- Teams need deployment independence

### Warning Signs You're Over-Engineering

- <5 developers but planning microservices
- No clear domain boundaries but adding service mesh
- Calling it "microservices" but deploying everything together
- More infrastructure code than business logic

---

## Technology Selection

### Language Quick Guide

| Need | Choose |
|------|--------|
| Rapid prototyping | Python |
| Type safety | TypeScript, Go |
| High performance | Go, Rust |
| Data/ML | Python |
| CLI tools | Go |
| Web APIs | Python, TypeScript, Go |

### Database Quick Guide

| Need | Choose |
|------|--------|
| General purpose | PostgreSQL |
| Embedded/local | SQLite |
| Document store | MongoDB |
| Flexible schema | MongoDB, PostgreSQL (JSONB) |
| Time-series | TimescaleDB |
| Key-value | Redis |

### API Style Quick Guide

| Need | Choose |
|------|--------|
| Public API | REST + OpenAPI |
| Multiple clients, complex data | GraphQL |
| Service-to-service | gRPC |
| Real-time updates | WebSocket |
| Default choice | REST + OpenAPI |

---

## Architecture Smells

### Critical (Fix Immediately)

| Smell | Signs | Fix |
|-------|-------|-----|
| Hardcoded secrets | API keys in code | Use environment variables |
| No error handling | Empty catch blocks, crashes on errors | Add error handling layer |
| Circular dependencies | A imports B imports A | Refactor module boundaries |

### High Priority

| Smell | Signs | Fix |
|-------|-------|-----|
| Big Ball of Mud | >50 files in root, no structure | Introduce layers/modules |
| Distributed Monolith | Services can't deploy independently | Consolidate or properly decouple |
| God Object | Single file >1000 lines | Split by responsibility |

### Medium Priority

| Smell | Signs | Fix |
|-------|-------|-----|
| Golden Hammer | One tech for everything | Right tool for each job |
| Premature Decomposition | <5 devs, 10+ services | Consolidate services |
| Missing API Gateway | Clients call multiple backends | Add gateway layer |

---

## Good Structure Examples

### Python Web Application

```
project/
    src/
        api/          # Route handlers
        services/     # Business logic
        models/       # Data models
        repositories/ # Data access
    tests/
    pyproject.toml
```

### Go API Service

```
project/
    cmd/
        server/       # Main entry point
    internal/
        api/          # HTTP handlers
        domain/       # Business logic
        repository/   # Data access
    pkg/              # Public packages (if any)
    go.mod
```

### TypeScript Web App

```
project/
    src/
        pages/        # Route components
        components/   # UI components
        services/     # API clients
        types/        # Type definitions
    tests/
    package.json
```

---

## API Design Checklist

### REST API

- [ ] OpenAPI 3.1.0 specification
- [ ] Consistent URL patterns (kebab-case)
- [ ] Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Proper status codes (200, 201, 400, 401, 403, 404, 500)
- [ ] Consistent error format
- [ ] Pagination for collections
- [ ] Authentication documented

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### Pagination Format

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

---

## Technology Rationale

### Weak Justifications (Avoid)

- "Team knows it" (unless timeline critical)
- "It's popular"
- "We've always used it"
- "Industry standard"

### Strong Justifications (Use These)

- "ACID transactions required for financial data"
- "Ecosystem has required libraries: X, Y, Z"
- "Performance requirements demand compiled language"
- "Existing codebase uses X, consistency reduces cognitive load"
- "Type safety critical for domain complexity"

### Rationale Template

```markdown
**Choice:** {{technology}}
**Problem it solves:** {{what need}}
**Alternatives considered:** {{options}}
**Trade-offs accepted:** {{downsides}}
```

---

## Common Decisions by Project Type

### Web Application ADRs

1. Frontend framework (React/Vue/Svelte)
2. Backend framework (FastAPI/Express/Next.js)
3. Database selection
4. Authentication approach
5. State management (if complex)

### API Backend ADRs

1. API versioning strategy
2. Authentication mechanism
3. Rate limiting approach
4. Database selection
5. Error response format

### Mobile Backend ADRs

1. API versioning for backwards compatibility
2. Push notification strategy
3. Offline sync strategy
4. Token refresh strategy
5. Pagination approach

---

## Quick Decision Flowchart

```
Start new project?
    |
    v
How many developers?
    |
    +-- <5 developers --> Monolith
    |
    +-- 5-10 developers --> Modular Monolith
    |
    +-- >10 developers, multiple teams --> Consider Microservices

Need high performance?
    |
    +-- Yes --> Go or Rust
    |
    +-- No --> Python or TypeScript

Need ACID transactions?
    |
    +-- Yes --> PostgreSQL or SQLite
    |
    +-- No, need flexibility --> MongoDB

Public API?
    |
    +-- Yes --> REST + OpenAPI
    |
    +-- No, internal services --> gRPC or REST
```

---

## See Also

- `reference-architecture.md` - Full architecture guidance
- `openapi.md` - API documentation standards
- `templates/core/trd.md` - TRD template
