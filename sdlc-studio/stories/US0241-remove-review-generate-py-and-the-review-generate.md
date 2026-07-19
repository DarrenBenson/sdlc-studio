# US0241: remove review_generate.py and the review generate route; review keeps only the consistency job

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_generate.py, .claude/skills/sdlc-studio/scripts/review.py
> **Epic:** EP0078
> **Points:** 2

## User Story

**As a** skill maintainer
**I want** `review generate` gone from the script surface with no alias left behind
**So that** `review` means the consistency pass and nothing else, and no reader is offered two names for one hunt

## Acceptance Criteria

### AC1: The script and its suite are deleted

- **Given** `scripts/review_generate.py` and `scripts/tests/test_review_generate.py`, whose bootstrap, policy and secret-scan duties are covered by the repo profile (US0239)
- **When** the shipped skill tree is inspected after the removal
- **Then** neither file is present, and the suite discovery run in the gate finds nothing to collect for them
- **Verify:** shell test ! -f .claude/skills/sdlc-studio/scripts/review_generate.py && test ! -f .claude/skills/sdlc-studio/scripts/tests/test_review_generate.py

### AC2: No route, import or catalogue row survives

- **Given** the script was reachable through the `review generate` route and listed in `reference-scripts.md`
- **When** the whole shipped skill tree is searched for the stem
- **Then** nothing matches: no route, no sibling import, no catalogue row and no alias pointing the reader back at the retired command
- **Verify:** shell ! grep -rl "review_generate" .claude/skills/sdlc-studio

### AC3: The on-ramp prompt template goes with it

- **Given** `templates/workflows/repo-review.md` existed only as the prompt `review_generate.py prompt` rendered
- **When** the template tree and the shipped files that reference it are checked
- **Then** the template is gone and no shipped file still points at it, leaving `review` with the unified PRD/TRD/TSD consistency job alone
- **Verify:** shell test ! -f .claude/skills/sdlc-studio/templates/workflows/repo-review.md && ! grep -rl "repo-review.md" .claude/skills/sdlc-studio

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
