# BG0879: US0977 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Closed with findings in:** US0977's discharge: its rejecting reviewer's APPROVE answered every finding (RUN-01M3VF2J critic-verdicts)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, changelog.d/US0977.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T17:04:21Z

## Summary

US0977 was rejected at round 2, the review cap, by qa-seat reviewer (subagent a5fd6530), so it was carried as a known issue rather than reviewed again. The findings still open: [regression] the repair lost the pin on saving a graduation (lessons.py:1944): dropping res graduated from the save condition survives every test because the rewritten AC1 fixture also retires LC-004 - isolated repro, a store with only a graduating LC-001 and CR0001 Complete prints graduated while the file still reads graduating; [new] the same-close-hit rule (hit\_now, lessons.py:1932) sees only REJECTs cited on the close's first pass: a retro Try-item hit lifted by the close's extract still graduates, and re-running the same close graduates a class the first close kept graduating, so reference-retro.md:131, changelog.d/US0977.md and the close\_pass docstring (same-close and Idempotent) are false - one-line fix: hit\_now /= ids of rows with a hit whose run is this run, before recent\_runs; [new] non-blocking: the retired\_run stamp on a Rejected CR is unpinned; [pre-existing] non-blocking: a class retired by a Rejected CR re-files a new graduation CR at its first repeat

## Steps to Reproduce

1. Read the round 2 REJECT of US0977 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0977 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [regression] the repair lost the pin on saving a graduation (lessons.py:1944): dropping res graduated from the save condition survives every test because the rewritten AC1 fixture also retires LC-004 - isolated repro, a store with only a graduating LC-001 and CR0001 Complete prints graduated while the file still reads graduating
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] the same-close-hit rule (hit\_now, lessons.py:1932) sees only REJECTs cited on the close's first pass: a retro Try-item hit lifted by the close's extract still graduates, and re-running the same close graduates a class the first close kept graduating, so reference-retro.md:131, changelog.d/US0977.md and the close\_pass docstring (same-close and Idempotent) are false - one-line fix: hit\_now /= ids of rows with a hit whose run is this run, before recent\_runs
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [new] non-blocking: the retired\_run stamp on a Rejected CR is unpinned
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: [pre-existing] non-blocking: a class retired by a Rejected CR re-files a new graduation CR at its first repeat
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** US0977 AC1 still passes: Given a fixture whose `lessons.jsonl` holds a `graduating` class whose `cr` names a CR at a terminal status, when `lessons.close_pass` runs (as `sprint.py close` runs it), then `lessons.py --root <fixture> classes` shows the class `graduated` when its CR is Complete or Superseded (the fix shipped) and `retired` when its CR is Rejected (nothing was fixed, so a later repeat revives it), and a `graduating` class whose CR is still open is unchanged. Fails on: HEAD leaves all of them `graduating`; graduating on any terminal status, which graduates a Rejected CR's class for good
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py::LessonLifecycleTests::test_a_class_graduates_when_its_cr_closes
  - **Verified:** yes (2026-10-01)
- [ ] **AC6** US0977 AC2 still passes: Given an `active` class whose `recorded_run` and hit runs are absent from this clone's run archive, and no hit in the last `QUIET_RUNS` runs this clone knows, when `lessons.close_pass` runs, then the class is `retired`; a class with a hit in those runs stays `active`. Fails on: HEAD keeps the unknown-run class `active` because its recording run is in no known window
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py::LessonLifecycleTests::test_a_class_recorded_in_another_clone_retires_when_quiet
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
