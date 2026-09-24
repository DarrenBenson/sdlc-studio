# BG0754: A commit touching a widely imported script runs well over the 90-second budget

> **Status:** Open
> **Measured at close:** RUN-01M39MC0 close (2026-09-24, load 0.7): a one-line gate.py change committed through both hooks in a clone of 016f29c7 took 93s against the 90s budget (229s at sprint start); its unit suites took 43s over 14 modules, and the rest is the pre-commit lanes, still sequential because US0891 was carried (BG0759). AC1 misses by 3s and AC2 is unmet while US0891 is open, so this stays Open until BG0759 lands
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/close_owed.py
> **Evidence:** US0880 hand-back and commit 315ec358 (247s), RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0880 reports the commit's time against 90s and never refuses. A change to gate.py or sprint.py selects the modules that import it, and `test_sprint.py` alone takes about 50s, so such a commit took 218-390s under load (US0880's own: 247s).

## Steps to Reproduce

1. Change `gate.py`. 2. Commit. 3. The hook prints `over budget ... reported, not refused`.

## Proposed Fix

Remove the measured causes rather than split `test_sprint.py` (a split saves at most 5s and repoints 148 Verify selectors): cache the decisions scan (US0890), run the pre-commit lanes concurrently (US0891), hand xdist one test at a time (US0892), keep boundary-only tests out of the commit run (US0893), walk the corpus once in `close_owed` (US0894), and take the eight advisory gate lanes off the per-commit path (US0895).

## Acceptance Criteria

- [ ] **AC1** Given a one-line change to `gate.py` committed on an idle machine after US0890-US0895 land, when the commit-msg hook records the run, then the commit's `total.selected` entry in `sdlc-studio/.local/gate-timings.json` reads 90 seconds or less (it read 229s at the start of the sprint).
  - **Verify:** manual - measured at the close from the recorded `total.selected` series for a commit touching `gate.py`; a wall-clock assertion on a shared machine is not a stable unit test, so the run's own recorded commit is the evidence
- [ ] **AC2** Given the measured causes (the uncached decisions scan, sequential pre-commit lanes, xdist chunking, live-repository tests per commit, the quadratic `close_owed` walk, advisory lanes per commit), then each is removed by US0890-US0895 and pinned by that story's own criteria; `test_sprint.py` is not split.
  - **Verify:** manual - the reviewer confirms US0890-US0895 are Done with their criteria green and no test module was split

## Impact

US0880 reports the commit's time against 90s and never refuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Proposed fix reworded at Sprint 3 planning from measurement: the previous fix was refuted or would add a hand-kept pin (LC-008) |
