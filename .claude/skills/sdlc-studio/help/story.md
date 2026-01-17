# /sdlc-studio story - User Stories

## Quick Reference

```
/sdlc-studio story                  # Generate Stories from all Epics
/sdlc-studio story --epic EP0001    # Generate for specific Epic
/sdlc-studio story update           # Update Story status
```

## Prerequisites

- Epics must exist in `sdlc-studio/epics/`
- Personas must exist at `sdlc-studio/personas.md`
- Run `/sdlc-studio epic` and `/sdlc-studio persona` first if missing

## Actions

### generate (default)
Break Epic acceptance criteria into atomic User Stories.

**What happens:**
1. Checks for Epics and Personas (creates persona template if missing)
2. Creates Definition of Done if not exists
3. For each Epic, identifies distinct user actions
4. Generates Stories with Given/When/Then acceptance criteria
5. Updates Epic files with Story links
6. Creates `sdlc-studio/stories/_index.md` registry

**Breakdown heuristics:**
- One story per distinct user action
- Stories completable in one sprint
- Split by persona when multiple involved

### update
Update Story status based on codebase implementation.

**What happens:**
1. Reads all Stories and their acceptance criteria
2. Searches codebase for implementation evidence
3. Updates status and checks off completed criteria
4. Updates Definition of Done items

## Output

**Files:**
- `sdlc-studio/stories/US{NNNN}-{slug}.md` per Story
- `sdlc-studio/stories/_index.md` registry
- `sdlc-studio/personas.md` (created if missing)
- `sdlc-studio/definition-of-done.md` (created if missing)

**Status values:** Draft | Ready | In Progress | Review | Done

**Story sections:**
- User Story (As a... I want... So that...)
- Context (persona reference, background)
- Acceptance Criteria (Given/When/Then)
- Scope
- UI/UX Requirements
- Technical Notes
- Edge Cases & Error Handling
- Test Scenarios
- Test Cases (links)
- Definition of Done
- Dependencies
- Estimation

## Examples

```
# Generate Stories from all Epics
/sdlc-studio story

# Generate for specific Epic only
/sdlc-studio story --epic EP0001

# Update status after implementation
/sdlc-studio story update
```

## Story Format

```markdown
**As a** {persona name}
**I want** {capability}
**So that** {benefit}
```

## Acceptance Criteria Format

```markdown
### AC1: {name}
- **Given** {precondition}
- **When** {action}
- **Then** {expected outcome}
```

## Next Steps

After generating Stories:
```
/sdlc-studio test-suite           # Generate Test Suites
/sdlc-studio test-case            # Generate Test Cases from ACs
```

## Naming Convention

- ID format: `US0001`, `US0002`, etc. (global, not per-Epic)
- Global numbering allows Stories to move between Epics
- Slug: kebab-case from title

## See Also

- `/sdlc-studio epic help` - Generate Epics (prerequisite)
- `/sdlc-studio persona help` - Define Personas (prerequisite)
- `/sdlc-studio test-case help` - Generate Test Cases from Story ACs
