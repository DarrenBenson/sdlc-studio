# CR-0663: Run the commit-time suites on the gate host, as the push already does

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Affects:** .githooks/commit-msg, tools/remote-gate.sh, tools/tests/test_commit_suites_remote.py
> **Evidence:** run six landing logs, scratchpad run6/hand-*/commit.log and run6/batch-*-commit.log
> **Date:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:33:08Z

## Summary

2026-11-05, run six. A commit to a hub script (sprint.py, gate.py, `verify_ac.py)` ran 17 to over 50 minutes of selected suites on the 8-core laptop at load 23, against the hook's 90 s budget; BG1190's first commit timed out at 3,000 s, and one commit-lane cap test alone takes 765 s. Run six cut the count of such hooks by landing several units in one commit, but each still costs 30 minutes of wall-clock. The push gate already runs on the gate host (sdlc.gateHost); the commit hook's suite stage does not.

## Impact

Wall-clock per point: run six's builds took minutes, its landings hours.

## Acceptance Criteria

*None yet: add them here, or on the stories `refine` decomposes this into.*

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Raised |
