# BG1105: AGENTS.md names the local push-cost series as the current push figure, which a clone with a gate host never adds to

> **Status:** Superseded
> **Superseded by:** BG1098
> **Severity:** Low
> **Points:** 1
> **Affects:** AGENTS.md, tools/tests/test_agents_md_push_figure.py, changelog.d/BG1105.md
> **Evidence:** US1086 QA review, round 2 (REJECT, the review cap), qa-seat-US1086-r1, 2026-10-20: a [pre-existing] item outside US1086's Affects that no open Bug or CR covered. It was carried into BG1095 as its AC4, and is moved here because a carried unit's redelivery cannot fix a file outside its Affects (BG1079).
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T20:29:55Z

## Summary

AGENTS.md's 'What will refuse you' table says `python3 tools/gate_timing.py estimate --suite boundary-push --warn-seconds 0` prints the current push figure. A clone that names a gate host records its pushes as `boundary-push@<host>` (.githooks/pre-push:222 and :259), so the command AGENTS.md names reads a local series that a host run never enters. On this clone it prints a stale local figure, or none.

## Steps to Reproduce

With `sdlc.gateHost` set, push once, then run `python3 tools/gate_timing.py estimate --suite boundary-push --warn-seconds 0`. The host run was recorded under `boundary-push@<host>`, not the series the command reads.

## Proposed Fix

Name the figure the hook itself announces. With a gate host that is the `boundary-push@<host>` series, and without one `boundary-push`. Or point at the hook's own cost line, so the table carries no series name to drift.

## Acceptance Criteria

- [ ] **AC1** AGENTS.md's push-figure command reads the series the pre-push hook records for this clone's configuration, with a gate host and without one
  - **Verify:** pytest tools/tests/test_agents_md_push_figure.py

## Impact

Someone reading AGENTS.md to judge how long a push takes reads the wrong series and gets a figure the gate host never produced.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
| 2026-10-20 | Claude Opus 5.5 | Superseded by BG1098, which already holds this finding; filed in error from BG1095's carried AC4 |
