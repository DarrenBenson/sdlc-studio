# BG1059: A retro's Batch field is never compared with the run's batch, so a unit added after the retro was scaffolded is left out of the run's measurement and its close accounting

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_batch_matches_run.py, changelog.d/BG1059.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M4R168, 2026-10-16: RETRO0134 `> **Batch:**` named 16 ids; sdlc-studio/.local/run-state.json `batch` held 18 (BG1056 and US1004 added by `batch add` after the scaffold); `sprint.py close --dry-run` printed `ok retro-validate: RETRO0134 valid` and the accuracy block read `0 of 16 unit(s) measured`. retro.py:793 `batch_count_check` compares parsed ids with the retro's declared count only.
> **Created:** 2026-10-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-16T08:00:52Z

## Summary

`sprint close` scaffolds the retro with the batch as it stands, and `sprint batch add` later adds units (a carried unit re-added on its carry's APPROVE, a repair unit joining the run) without touching the retro. `retro.py validate` cross-checks the Batch field only against the retro's own `Delivered: N / M` header (`batch_count_check`, retro.py:793), never against the run's batch, so the close's retro-validate step reads a stale field as valid. Everything downstream reads that field: `retro.py accuracy` measures only the units it names, `sprint_report` counts delivery from it (`sprint_report.py`:2904), and `close_owed` treats a unit no retro's Batch field names as a close still owed (`close_owed.py`:11). RETRO0134 named 16 units while RUN-01M4R168's batch held 18; BG1056 and US1004 were missing, and only a hand check of the run state caught it.

## Steps to Reproduce

1. `sprint.py close` with no retro on a run, which scaffolds RETROxxxx with the batch as it stands. 2. `sprint.py batch add <id>` for a further unit. 3. `retro.py validate --id RETROxxxx` -> valid; `sprint.py close --dry-run` -> `ok retro-validate`; `retro.py accuracy --id RETROxxxx --write` -> measures the original units only.

## Proposed Fix

Have `retro.py validate`, and so the close's retro-validate step, compare the Batch ids with the batch of the run the retro names, and refuse naming each id the field omits or adds; or have `batch add` and `batch drop` rewrite the Batch field of a retro the run has already scaffolded.

## Acceptance Criteria

- [ ] **AC1** With a retro naming a run whose batch holds a unit its Batch field omits, `retro.py validate` and the close's retro-validate step refuse, naming the omitted id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_batch_matches_run.py -k omitted_unit_is_refused

## Impact

A close measures, reports and accounts for a subset of the run without saying so: velocity omits the late units' points, and those units read as owed a close by every later `close_owed` check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-16 | Claude Opus 5.5 | Filed |
