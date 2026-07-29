# US0553: A close-phase commit over an unchanged test-relevant surface reuses the gate verdict the close itself earned, rather than re-running the suites

> **Status:** Review
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-commit
> **Epic:** EP0189
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator closing a sprint
**I want** the close's own full gate run to record the verdict it earned
**So that** the commits that follow it over the same script tree reuse that verdict instead of re-running the whole suite each time

## Premise

US0493 already built the surface hash and the `reuse` branch of `suite_decision`, and the
commit hook already records a verdict after a green run. What is missing is the close's OWN
gate run: `sprint close` runs the full gate as step 4 and records nothing, so the first commit
that follows re-earns a verdict the close has just paid for. This story writes that verdict; it
does not rebuild the decision. The companion narrowing that keeps a filed artefact from moving
the surface hash is US0554 - without it, this reuse fires once and then stops.

## Acceptance Criteria

### AC1: the close's gate step records the verdict it earned

- **Given** `sprint close` runs its gate step and the suites pass
- **When** the step completes
- **Then** a green suite verdict is recorded for the tree it verified, carrying that tree's surface hash, in the same record the commit hook reads
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseVerdictReuseTests::test_the_close_gate_step_records_the_verdict_it_earned
- **Verified:** yes (2026-07-29)

### AC2: a close-phase commit over that unchanged surface reuses it

- **Given** a recorded green verdict whose surface hash matches the working tree
- **When** a close-phase commit follows that touches no script, template or tool
- **Then** `suite_decision` returns mode `reuse` and the unit suites do not run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseVerdictReuseTests::test_a_close_phase_commit_over_an_unchanged_surface_reuses_the_verdict
- **Verified:** yes (2026-07-29)

### AC3: the reuse is refused whenever the surface moved

- **Given** a recorded green verdict
- **When** any file inside the test-relevant surface changes after it was recorded
- **Then** the decision is not `reuse`, and the stated reason names the surface change rather than reporting a match
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseVerdictReuseTests::test_a_moved_surface_refuses_the_reuse
- **Verified:** yes (2026-07-29)

### AC4: the reuse is announced, never silent

- **Given** a commit that reuses a verdict
- **When** the hook reports its lanes
- **Then** the pre-commit hook names the reuse as a SKIP with its reason, so a reader can tell a skipped run from a passed one
- **Verify:** shell grep -q 'SKIP.*unit suites' .githooks/pre-commit
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
