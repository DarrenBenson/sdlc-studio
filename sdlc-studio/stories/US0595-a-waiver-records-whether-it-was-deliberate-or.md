# US0595: A waiver records whether it was deliberate or its window had already expired, and the retro counts them apart

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 3

## User Story

**As a** maintainer reading the record a year later
**I want** a waiver to record whether it was chosen or forced
**So that** a process failure is not laundered as a decision

## Acceptance Criteria

### AC1: a waiver records its kind

- **Given** two waivers, one taken deliberately and one for an item already unsatisfiable when it fired
- **When** each is recorded
- **Then** each carries its kind, so a process failure is not laundered as a decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverKindTests::test_a_waiver_records_its_kind

### AC2: the retro counts the two kinds apart

- **Given** a run holding one of each
- **When** the sprint report is composed
- **Then** it reports how many items expired before anyone was asked, separately from those set aside on purpose
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverKindTests::test_expired_and_deliberate_are_counted_apart

### AC3: a waiver recorded before kinds existed counts as neither

- **Given** a waiver row written before the kind was recorded, as every waiver in every
  existing decision log is
- **When** the kinds are read and counted
- **Then** it counts into neither bucket and is reported as unkinded, because defaulting it to
  `deliberate` launders every historic process failure on read - the sibling `waiver_authoriser`
  already documents that None is a real answer rather than a blank
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverKindTests::test_a_legacy_unkinded_waiver_counts_as_neither

## Test-plan notes

Written after a plan review rejected the first draft.

1. **The kind is a marker inside an existing cell, not a seventh column.** `decisions.md` has a
   fixed six-column header shipped in `templates/decisions.md`, `list_decisions` parses by
   position, and a seventh cell trips MD056 on a tracked, root-linted file. The precedent is
   `[authorised by: <who>]` in the same module. The mutants are therefore stated against the
   read-back API - what `waiver_kind` answers - not against a storage shape.
2. **Drive the shipped lane, not the library.** The `waive` subparser is what an operator runs
   and it has no kind flag today; a test that calls `record_waiver` directly stays green while
   no waiver anybody records carries a kind. AC1's test goes through `decisions.main(["waive",
   ...])`. This is the `brief_fingerprint` scar, which passed in-process for a whole sprint
   while the CLI printed nothing.
3. **AC2's fixture is asymmetric - two expired and one deliberate.** With one of each, both
   figures are 1 and an implementation that reports the expired count under the deliberate
   label is byte-identical to a correct one. Each figure is asserted against its own number.
4. AC2 names the function and the field the figures live in, so a test asserting on one
   renderer while the figures land in another cannot pass in both directions.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change `record_waiver` in decisions.py to compose the row with a constant kind whatever it was given, so both waivers read back the same | a waiver records its kind |
| AC2 | collapse both figures into one in sprint_report.py | the retro counts the two kinds apart |
| AC3 | change decisions.py to read an unkinded legacy row as deliberate | a waiver recorded before kinds existed counts as neither |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
