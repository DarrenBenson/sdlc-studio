<!--
Load: On /sdlc-studio trd or /sdlc-studio trd help
Dependencies: SKILL.md (always loaded first)
Related: reference-trd.md (deep workflow), reference-architecture.md, templates/trd-template.md
-->

# /sdlc-studio trd - Technical Requirements Document

Create and maintain Technical Requirements Documents that bridge product requirements and implementation.

## Usage

```
/sdlc-studio trd                     # Ask which mode (create/generate/review)
/sdlc-studio trd create              # Interactive TRD creation
/sdlc-studio trd generate            # Reverse-engineer TRD from codebase
/sdlc-studio trd review              # Review TRD against implementation
```

## Purpose

A TRD bridges the gap between **what** (PRD) and **how** (code). It captures:
- **Project type classification** and architecture implications
- Architecture decisions with rationale
- Technology stack with strong justifications
- API contracts and data schemas
- Integration patterns
- Infrastructure approach
- Security considerations
- **Architecture assessment** (brownfield projects)

## Pipeline Position

```
PRD --> TRD --> Personas --> Epics --> Stories --> Code
```

The TRD should be created after the PRD but before detailed planning begins.

## Actions

### create

Interactive conversation to build a TRD from scratch.

**Prerequisites:** PRD must exist at `sdlc-studio/prd.md`

**Process:**
1. **Project type classification** (Web App, API Backend, Mobile Backend, etc.)
2. **Architecture recommendations** based on project type
3. Architecture pattern discussion (accept defaults or customise)
4. Technology stack decisions with strong justifications
5. API design choices
6. Data architecture planning
7. Infrastructure approach
8. Security considerations

**Architecture Guidance:**
- Presents recommended stack based on project type
- Requires strong rationale for technology choices (not just "familiarity")
- Captures deviations from defaults as ADRs

**Best for:** Greenfield projects or major re-architecture

### generate

Reverse-engineer a TRD from an existing codebase.

**Prerequisites:** PRD should exist for context

**Process:**
1. **Detect project type** from codebase patterns
2. **Detect architecture pattern** (monolith, microservices, etc.)
3. Explore codebase structure and patterns
4. Extract technology stack from configs
5. Map API contracts from routes
6. Document data models from schemas
7. Analyse infrastructure from deployment configs
8. Assess security implementation
9. **Architecture assessment** against best practices

**Architecture Assessment:**
Evaluates existing architecture for:
- Pattern alignment with project type
- Architecture smells (Big Ball of Mud, Distributed Monolith, etc.)
- Technology selection appropriateness
- Standards compliance (API, error handling)

Produces recommendations with severity markers: [CRITICAL], [REVIEW], [INFO]

**Best for:** Brownfield projects needing documentation and assessment

### review

Review TRD against implementation and sync changes.

**Prerequisites:** TRD must exist at `sdlc-studio/trd.md`

**Process:**
1. Compare codebase against current TRD
2. Identify new components or changes
3. Update relevant sections
4. Add new ADRs for significant decisions
5. Resolve answered questions

**Best for:** Keeping documentation current after changes

## Output

**Location:** `sdlc-studio/trd.md`

**Status Values:** Draft | Approved

## TRD Structure

| Section | Content |
|---------|---------|
| Executive Summary | Purpose, scope, key decisions |
| **Project Classification** | Project type, default pattern, deviation rationale |
| Architecture Overview | Pattern, components, diagram |
| Technology Stack | Languages, frameworks, tools with rationale |
| API Contracts | Endpoints, schemas, authentication |
| Data Architecture | Models, relationships, storage |
| Integration Patterns | External services, events |
| Infrastructure | Deployment, environments, scaling |
| Security | Threats, controls, data classification |
| Performance | Targets and capacity |
| **Architecture Checklist** | Pattern, technology, standards, infrastructure |
| ADRs | Architecture Decision Records |
| Open Questions | Unresolved technical items |
| **Architecture Assessment** | (generate only) Best practice alignment, smells, recommendations |

## Project Types

Classification determines architecture recommendations:

| Type | Description | Default Pattern |
|------|-------------|-----------------|
| Web Application | Frontend + backend | Monolith |
| API Backend | REST/GraphQL API, no UI | Modular Monolith |
| Mobile Backend | APIs for iOS/Android | Monolith with API layer |
| Desktop Application | Local app, CLI tool | Layered |
| SDK/Library | Reusable code | Modular |
| Monorepo | Multiple services | Depends on count |

See `reference-architecture.md` for full guidance and decision trees.

## Architecture Decision Records (ADRs)

The TRD includes ADRs for significant decisions:

```markdown
### ADR-001: Use PostgreSQL for primary storage

**Status:** Accepted

**Context:** Need reliable ACID-compliant storage for user data.

**Decision:** Use PostgreSQL 15 with pgvector extension.

**Consequences:**
- Positive: Strong consistency, good tooling, vector search
- Negative: Requires more ops than managed NoSQL
```

## Options

| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing TRD |
| `--prd` | Specify PRD path (default: sdlc-studio/prd.md) |

## Examples

```
# Interactive creation for new project
/sdlc-studio trd create

# Generate from existing codebase
/sdlc-studio trd generate

# Review after adding new service
/sdlc-studio trd review

# Generate using specific PRD
/sdlc-studio trd generate --prd docs/requirements.md
```

## Confidence Markers

When generating, use confidence markers:

| Marker | Meaning |
|--------|---------|
| [HIGH] | Clear evidence in codebase |
| [MEDIUM] | Inferred from patterns |
| [LOW] | Best guess, needs validation |
| [INFERRED] | Reverse-engineered, not explicit |

## Next Steps

After TRD:
- Run `/sdlc-studio persona` to define user types
- Run `/sdlc-studio epic` to generate feature groupings
- Use TRD as reference during implementation planning

## See Also

- `/sdlc-studio prd help` - Product requirements (prerequisite)
- `/sdlc-studio epic help` - Feature groupings (next step)
- `/sdlc-studio status` - Check pipeline state
- `reference-architecture.md` - Full architecture guidance
- `best-practices/architecture.md` - Quick reference patterns
