# US0412: reference-cr.md and reference-rfc.md state refine produces a plannable unit whose ACs still need grooming, opt-out per project

> **Status:** Done
> **Delivers:** CR0412
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-cr.md,.claude/skills/sdlc-studio/reference-rfc.md
> **Epic:** EP0155
> **Points:** 2

## User Story

**As an** operator relying on the two-backlog promise
**I want** the reference docs to state what refine actually produces
**So that** the promise that a refined request is delivery work is true rather than
aspirational

## Acceptance Criteria

### AC1: the reference docs state refine produces a plannable-but-ungroomed unit

- **Given** the refine sections of reference-cr.md and reference-rfc.md
- **When** they are read
- **Then** each states that refine produces a PLANNABLE unit (Affects present) whose
  acceptance criteria still need grooming, and names the opt-out
- **Verify:** manual - read the refine sections of reference-cr.md and reference-rfc.md and confirm each states the plannable-but-ungroomed contract and the opt-out
- **Verified:** yes (2026-07-24)

Evidence for the manual read: `reference-cr.md` "What `refine` produces" states the
plannable-but-ungroomed contract under both halves and names the opt-out
(`sprint.breakdown: judgement`); `reference-rfc.md`'s refine paragraph states the same
contract and the same opt-out, and cross-links `reference-cr.md#refine-output`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Back-annotated the manual AC's `Verified:` line, missing since the unit closed - the conformance lane's one non-conformant unit. THREE independent build agents each performed the read and reached the same conclusion before the annotation landed; the duplicated effort is the cost recorded in BG0279 |
