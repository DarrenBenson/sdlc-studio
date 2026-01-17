# /sdlc-studio trd - Technical Requirements Document

Create and maintain Technical Requirements Documents that bridge product requirements and implementation.

## Usage

```
/sdlc-studio trd                     # Ask which mode (create/generate/update)
/sdlc-studio trd create              # Interactive TRD creation
/sdlc-studio trd generate            # Reverse-engineer TRD from codebase
/sdlc-studio trd update              # Update TRD with implementation changes
```

## Purpose

A TRD bridges the gap between **what** (PRD) and **how** (code). It captures:
- Architecture decisions with rationale
- Technology stack with justifications
- API contracts and data schemas
- Integration patterns
- Infrastructure approach
- Security considerations

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
1. Architecture pattern discussion
2. Technology stack decisions
3. API design choices
4. Data architecture planning
5. Infrastructure approach
6. Security considerations

**Best for:** Greenfield projects or major re-architecture

### generate

Reverse-engineer a TRD from an existing codebase.

**Prerequisites:** PRD should exist for context

**Process:**
1. Explore codebase structure and patterns
2. Extract technology stack from configs
3. Map API contracts from routes
4. Document data models from schemas
5. Analyse infrastructure from deployment configs
6. Assess security implementation

**Best for:** Brownfield projects needing documentation

### update

Sync TRD with implementation changes.

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
| Architecture Overview | Pattern, components, diagram |
| Technology Stack | Languages, frameworks, tools with rationale |
| API Contracts | Endpoints, schemas, authentication |
| Data Architecture | Models, relationships, storage |
| Integration Patterns | External services, events |
| Infrastructure | Deployment, environments, scaling |
| Security | Threats, controls, data classification |
| Performance | Targets and capacity |
| ADRs | Architecture Decision Records |
| Open Questions | Unresolved technical items |

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

# Update after adding new service
/sdlc-studio trd update

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
