# /sdlc-studio epic - Epics

## Quick Reference

```
/sdlc-studio epic                   # Generate Epics from PRD
/sdlc-studio epic update            # Update Epic status
```

## Prerequisites

- PRD must exist at `sdlc-studio/prd.md`
- Run `/sdlc-studio prd` first if missing

## Actions

### generate (default)
Parse PRD and group features into Epics.

**What happens:**
1. Reads Feature Inventory from PRD
2. Groups related features (5-8 per Epic)
3. Creates Epic files with business context, scope, acceptance criteria
4. Creates `sdlc-studio/epics/_index.md` registry

**Grouping heuristics:**
- Features sharing same user type → same Epic
- Features with shared dependencies → same Epic
- Features forming complete user journey → same Epic

### update
Update Epic status based on Stories and codebase.

**What happens:**
1. Reads all Epics and their linked Stories
2. Calculates completion from Story status
3. Verifies against codebase implementation
4. Updates status and acceptance criteria checkboxes

## Output

**Files:**
- `sdlc-studio/epics/EP{NNNN}-{slug}.md` per Epic
- `sdlc-studio/epics/_index.md` registry

**Status values:** Draft | Ready for Review | Approved | In Progress | Done

**Epic sections:**
- Summary
- Business Context (problem, value, metrics)
- Scope (in/out, affected personas)
- Acceptance Criteria
- Dependencies
- Risks & Assumptions
- Technical Considerations
- Sizing & Effort
- Story Breakdown
- Test Plan link

## Examples

```
# Generate all Epics from PRD
/sdlc-studio epic

# Update Epic status after Stories complete
/sdlc-studio epic update

# Use custom PRD location
/sdlc-studio epic --prd ./docs/requirements.md
```

## Next Steps

After generating Epics:
```
/sdlc-studio story                # Generate Stories from Epics
/sdlc-studio test-plan            # Generate Test Plans for Epics
```

## Naming Convention

- ID format: `EP0001`, `EP0002`, etc. (global numbering)
- Slug: kebab-case from title, max 50 chars
- Example: `EP0001-user-authentication.md`

## See Also

- `/sdlc-studio prd help` - Create PRD (prerequisite)
- `/sdlc-studio story help` - Generate Stories from Epics
- `/sdlc-studio test-plan help` - Generate Test Plans for Epics
