# US0333: Under carry-forward every finding is FILED or explicitly waived with a reason; narrative downgrade is refused, as it already is for a missing review leg

> **Status:** Done
> **Verification depth:** functional - node-addressed tests in test_critic/test_conformance/test_sprint, all green; carry_forward mutation-proven (7 mutants killed incl. a non-resolving ref)
> **Delivers:** CR0404
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0113
> **Points:** 5

## User Story

**As an** operator shipping with findings outstanding
**I want** every carried finding filed or explicitly waived
**So that** carrying forward is fail-forward rather than forgetting, and the difference is
mechanical rather than a matter of intent

## Acceptance Criteria

### AC1: an unfiled, unwaived finding blocks the close even under carry-forward

- **Given** carry-forward in force and a REJECT with three findings, two filed as artefacts
- **When** the close runs
- **Then** it refuses and names the third, so the policy changes what blocks - the verdict
  no longer does, the unfiled finding still does
- **Verify:** manual - retired by BG0831: the carry-forward review policy and its key `review.policy` were deleted: every project carries a unit whose REJECT stands at the round cap (`review.max_rounds`), filing its findings
- **Verified:** manual (2026-10-01) - retired, superseded by BG0831

### AC2: a waiver requires a reason and is refused without one

- **Given** a finding waived with an empty reason
- **When** the waiver is recorded
- **Then** it is refused, matching the treatment a missing review leg already gets
- **Verify:** manual - retired by BG0831: the carry-forward review policy and its key `review.policy` were deleted: every project carries a unit whose REJECT stands at the round cap (`review.max_rounds`), filing its findings
- **Verified:** manual (2026-10-01) - retired, superseded by BG0831

### AC3: narrative downgrade is refused in both directions

- **Given** an attempt to resolve a finding by restating it as an observation, or to
  downgrade a required review leg to optional
- **When** either is recorded
- **Then** both are refused, since `reference-review.md` already forbids resolving a missing
  leg by narrative downgrade and a carried finding gets the same two exits and no third
- **Verify:** manual - retired by BG0831: the carry-forward review policy and its key `review.policy` were deleted: every project carries a unit whose REJECT stands at the round cap (`review.max_rounds`), filing its findings
- **Verified:** manual (2026-10-01) - retired, superseded by BG0831

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
