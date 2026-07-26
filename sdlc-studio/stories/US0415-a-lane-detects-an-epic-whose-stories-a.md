# US0415: a lane detects an epic whose stories a delivered sprint already satisfied and reports it as derivable

> **Status:** Done
> **Delivers:** CR0414
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As an** operator planning a batch off a long-lived backlog
**I want** a unit whose work a delivered one already did to be named before it is built
**So that** a sprint does not pay again for something a previous sprint shipped

## Acceptance Criteria

### AC1: overlap is detected without depending on any verifier

- **Given** an ungroomed skeleton carrying no `Verify:` lines, whose work a terminal unit already delivered
- **When** `reconcile detect` runs
- **Then** it is reported, naming the delivered id - the existing `built-not-closed` check reads the verification report, so a unit with no executable criteria can never appear in it, and the check built for "this is already done" is structurally blind to work minted before it was groomed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::AlreadyDeliveredAdvisoryTests::test_a_skeleton_a_delivered_unit_satisfies_is_reported
- **Verified:** yes (2026-07-24)

### AC2: overlap is distinguished from mere file-sharing

- **Given** two units that touch the same file but do different work
- **When** the lane runs
- **Then** they are NOT reported - a shared `Affects` alone is already the planner's clustering signal, and recycling it as a duplicate claim would bury the real cases
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::AlreadyDeliveredAdvisoryTests::test_a_shared_file_alone_is_not_reported
- **Verified:** yes (2026-07-24)

### AC3: matching wording alone is not enough either

- **Given** two units whose titles match closely but which declare different files
- **When** the lane runs
- **Then** they are NOT reported - both signals or nothing, otherwise the lane reports on vocabulary
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::AlreadyDeliveredAdvisoryTests::test_matching_wording_on_different_files_is_not_reported
- **Verified:** yes (2026-07-24)

### AC4: the lane is advisory and never moves the exit code

- **Given** a reported overlap and no mechanical drift
- **When** `reconcile detect` runs
- **Then** it prints the advisory and still exits 0 - whether two units mean the same thing is a judgement, and the exit code answers a mechanical question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::AlreadyDeliveredAdvisoryTests::test_the_lane_is_advisory_and_never_moves_the_exit_code
- **Verified:** yes (2026-07-24)

## Detail

**Scope, stated plainly.** CR0414 carries four criteria. This story delivers the detection lane
(its AC1 and AC2). CR0414's AC3 (document the blind spot beside the `built-not-closed` behaviour)
and AC4 (check a request's factual premise against the source before it is sized) are NOT delivered
here: AC3 lands in the sprint/audit docs and AC4 in `refine`, neither of which is in this story's
`Affects`. They remain open against CR0414.

**Measured on this repo's own workspace.** The settled rule - a shared declared file AND at least 4
shared distinctive title words AND 40% containment of the shorter title - yields 19 candidate pairs
over 13 open units. Suppressing pairs already wired together (`Parent`/`Decomposed-into`/`Delivers`/
`Epic`) removed 2 pairs that were the decomposition showing through, not an overlap.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed to the lane this story's `Affects` covers, and delivered as `already_delivered_advisory` |
