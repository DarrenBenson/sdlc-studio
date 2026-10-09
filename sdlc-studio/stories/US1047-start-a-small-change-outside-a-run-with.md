# US1047: Start a small change outside a run with one command that records its base commit

> **Status:** Draft
> **Delivers:** CR0626
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/small_change.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_small_change_start.py, changelog.d/US1047.md
> **Epic:** EP0286
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer with a one-file bug to fix
**I want** one command that starts the fix outside a run and records the commit the change is measured against
**So that** I skip the run's ceremony and every later step knows which commit is the change's base

## Acceptance Criteria

- **AC1:** Given an Open bug whose executable criterion fails at HEAD, in a git tree with no open run, when `small_change.py start --unit BG0001` runs, then the bug is In Progress, carries `Small-change: <HEAD sha>`, and the output names the remaining commands of the path.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_start.py::SmallChangeStartTests::test_start_moves_the_unit_and_records_its_base
- **AC2:** Given a change request id, when `small_change.py start` runs on it, then it exits non-zero naming `refine.py apply`, and nothing is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_start.py::SmallChangeStartTests::test_a_request_is_refused_until_refined
- **AC3:** Given a bug whose criteria carry no Verify line, when `small_change.py start` runs on it, then it exits non-zero saying the path keeps an executable criterion, and nothing is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_start.py::SmallChangeStartTests::test_a_unit_without_an_executable_criterion_is_refused
- **AC4:** Given a started small change whose recorded base is an earlier commit, when `small_change.py start` runs again at a later HEAD, then the recorded base is unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_start.py::SmallChangeStartTests::test_a_second_start_keeps_the_first_base
- **AC5:** Given an Open bug whose fix is already committed, so every executable criterion passes at HEAD, when `small_change.py start` runs without `--base`, then it exits non-zero naming `--base <ref>`, and nothing is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_start.py::SmallChangeStartTests::test_a_base_that_already_holds_the_change_is_refused

## Notes

- Release: 6.2 (D0355 breakdown G12, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: start moves the status and writes no base.
- AC2 must fail on: request types (CR, RFC, epic) are accepted as deliverable units.
- AC3 must fail on: start accepts a unit with only manual criteria, which the terminal transition would later refuse.
- AC4 must fail on: a re-run overwrites the base with HEAD, so revert-check later reverts to a commit that already holds the fix and reverts nothing.
- AC5 must fail on: start records HEAD unconditionally, so the base already holds the change and revert-check has nothing to revert.
- One field, `> **Small-change:** <base sha>`, is both the marker that the unit took the path and its base. It is written through the artefact field writer, never by hand, and committed with the change, so a reviewer in another clone reads it (LL0029). reference-schema.md lists it for story and bug, beside `Revert-check-exempt`, as a field that gates a check.
- Before recording HEAD, start runs the unit's executable criteria without stamping (verify_ac's dry run). If every one passes, the base would already hold the change (LL0007), so start refuses and names `--base <ref>`. A criterion whose test does not exist yet, or that cannot run, does not pass, so test-first work is unaffected. `--base` must be an ancestor of HEAD, and applies to an In Progress unit too.
- The status move goes through transition.py's own function, so the In Progress gates and the index sync are the transition's, not a copy. A unit already at a terminal status is refused.
- The refusal of a unit an open run holds now sits with the check story's run-collision criterion, which start runs (panel change 7 split its arms). Until the check story lands, start alone does not refuse it; both are 6.2 and start builds first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G12 after the refine panel's review |
