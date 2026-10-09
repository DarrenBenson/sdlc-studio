# US1001: The lane-yield appendix is read from the committed run record, as the close froze it

> **Status:** Draft
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py, changelog.d/US1001.md
> **Epic:** EP0276
> **Points:** 3
> **Depends on:** US0997, BG1010
> **Persona:** Maya Okafor

## User Story

**As** the operator deciding which commit gates have earned their place
**I want** the lane-yield tally the close read from this clone's refusal log frozen onto the run record
**So that** a signed page's delete-candidate verdicts can be re-read on any machine, not only the one whose hooks wrote the log

## Acceptance Criteria

- **AC1:** Given a clone whose refusal log holds a refusal inside the run and whose run archive holds an earlier run, when `sprint close` files the report, then the lane-yield rows are recorded on the run record, every lane-yield figure cites the tracked run record ahead of `git log`, and no figure anywhere on the page names a path under `.local/`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py::FrozenLaneYieldTests::test_close_freezes_the_tally_on_the_run_record
- **AC2:** Given that run signed and committed, when `sprint_report.py build --run <RUN-ID> --id <RETRO> --format json` runs in a fresh clone holding no refusal log and no run archive, then the lane-yield section is present with the rows the filed page carries.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py::FrozenLaneYieldTests::test_a_fresh_clone_reads_the_frozen_tally

## Notes

- Release: later (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: `_lane_yield_section` re-reading sdlc-studio/.local/refusals.jsonl at every derivation and citing REFUSALS_REL (sprint_report.py:4509 and 4607)
- AC2 must fail on: returning None when the clone holds no log, as `_lane_yield_section` does today, so the section vanishes everywhere but the closing machine
- Marked later: the panel recommends cutting it and amending CR0610's first criterion to exclude the appendix. The section is per clone by design and outside the digest; only this repository's hooks write the log; a run's refusals land on whichever machines committed to it, so a tally frozen from the closer's log is still partial; and it is machinery measuring machinery (LL0056). If kept, the page must say the tally is this clone's log as the close read it.
- The second criterion needs BG1010: `cmd_build` resolves --run but builds the default run (sprint_report.py:5612), so at HEAD the selector fails for that reason, not this story's.
- Two .local reads feed the section today: the refusal log (sprint_report.py:4600) and the run archive that bounds the last three runs (`_yield_windows`, sprint_report.py:4581). Freeze both beside freeze_ci_runs (sprint.py:9459).
- An unfrozen preview of an open run keeps reading the log, as `_ci_runs` does for an unfrozen open run, so test_lean_lane_yield.py stays green unchanged (test_the_appendix_shows_lane_yield builds an unfrozen live run).
- Refreshed on every prepare, as CI runs are; the section stays outside the digest, so no rule mark is needed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
