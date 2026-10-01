# BG0864: transition to Fixed admits a bug whose Verify lines have never been run, so a carried bug with red or manual-only criteria reaches Fixed with nothing executed

> **Status:** Won't Fix
> **Closed with findings in:** D0291, discovery backlog sweep 2026-10-01 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py,.claude/skills/sdlc-studio/scripts/tests/test_transition.py, changelog.d/BG0864.md
> **Evidence:** BG0829 QA review (subagent a302a39d), 2026-10-01
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T00:26:46Z

## Summary

Found by BG0829's QA review (RUN-01M3T8N1, 2026-10-01): at f075090c a hand-written bug at In Progress with `Verify: shell false` moves to Fixed (rc 0), as does one with only a manual verifier; the gate refuses a bug nothing speaks for (no Verify line) and one whose RECORDED `verify_ac` run is red, but reads 'never run' as passing. Since BG0829 a carried bug carries its unit's criteria and manual finding criteria, so a carried bug whose unit criteria are red reaches Fixed with no run, no review and no --force (refused only after `verify_ac run`). A unit with no criteria yields a carried bug with only manual verifiers, which reaches Fixed with nothing executed even after a run.

## Steps to Reproduce

On a bug at In Progress with `- **Verify:** shell false` and no `verify_ac` run, `transition.py set --id BGxxxx --status Fixed`: rc 0.

## Proposed Fix

Have the Fixed gate run the bug's executable verifiers when no current run exists (or refuse and say to run them), and refuse a bug whose only verifiers are manual unless an independent APPROVE covers it.

## Acceptance Criteria

- [ ] **AC1** Given a bug at In Progress whose only executable Verify is red and which has no `verify_ac` run, when `transition.py set --status Fixed` runs, then it is refused naming the unrun or red criterion. Fails on: f075090c, which moves it (rc 0)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::FixedGateTests::test_an_unrun_red_verifier_does_not_reach_fixed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
