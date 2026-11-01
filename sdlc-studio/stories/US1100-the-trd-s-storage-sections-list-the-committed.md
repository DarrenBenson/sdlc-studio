# US1100: The TRD's storage sections list the committed evidence and describe the run state and lifecycle through close and sign, and the .local writer pin fails on a writer that stops writing

> **Status:** Done
> **Delivers:** CR0645
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, tools/tests/test_lean_trd_refresh.py, changelog.d/US1100.md
> **Epic:** EP0293
> **Points:** 5
> **Depends on:** US1099
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer releasing 6.2
**I want** the TRD's storage sections to list the committed evidence and describe the run's state and lifecycle through close and sign
**So that** its storage blueprint carries the records every checkout now reads, and a `.local` writer that stops writing is caught (RV0028 TRD-3, TRD-5, TRD-6, TRD-10)

## Acceptance Criteria

- **AC1:** Given the committed evidence (the actuals and forecasts shards, lessons.jsonl, the verdict logs, the RPT reports and the run records), when the TRD's storage sections are read, then each is listed with its path
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdStorageTests::test_every_committed_record_is_listed
  - **Verified:** yes (2026-11-01)
- **AC2:** Given a run, when the TRD is read, then it says which run state is live in `.local` and which is tracked, and describes the run from plan through close to sign
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdStorageTests::test_the_run_lifecycle_reaches_sign
  - **Verified:** yes (2026-11-01)
- **AC3:** Given a `.local` file the TRD documents with its writer, when that writer no longer writes it, then the pin in the residue module fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::LocalWriterPinTests::test_a_writer_that_stops_writing_fails_the_pin
  - **Verified:** yes (2026-11-01)

## Notes

- Serves: Rowan Achterberg, End goal 3.
- Source: sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md, findings TRD-3, TRD-5, TRD-6 and TRD-10.
- AC1 must fail on: a committed record dropped from the TRD; the record set is read from the tree (the tracked paths), never typed into the test.
- AC2 must fail on: the TRD showing run state as `.local` only, or leaving out the sign step.
- AC3 must fail on: a documented writer edited so it no longer writes the file while the pin still passes.
- Overlap: US1099 and US1101 share trd.md and the test module. Covers CR0645 AC2 and AC5.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
