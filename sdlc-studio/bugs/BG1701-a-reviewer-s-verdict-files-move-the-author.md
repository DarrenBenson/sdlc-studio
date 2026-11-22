# BG1701: A reviewer's verdict files move the author's self-check digest, so a unit declaring sdlc-studio/reviews/ is read as stale after its first review

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_review_writes.py, changelog.d/BG1701.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Run twenty-two repair lane RC1, 2026-11-22: `critic.py` `_REVIEW_TOOL_WRITES` (near line 3123) lists only `SELF_CHECK_FILE` and the delivery ledger
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T11:34:02Z

## Summary

critic.py leaves the review tooling's own writes out of the self-check digest (`_REVIEW_TOOL_WRITES`: the self-check log and the verdict ledger), but not the verdict files a reviewer writes under sdlc-studio/reviews/verdicts/<unit>/. For a unit whose Affects declares sdlc-studio/reviews/ or a directory above it, each verdict file a reviewer writes changes the digest, so the author's self-check reads as stale and critic.py brief refuses the next round's brief until the author records the self-check again over an unchanged diff.

## Steps to Reproduce

1. In a fixture, give a unit Affects: sdlc-studio/reviews/ and record its self-check with critic.py self-check record. 2. Write a verdict file at sdlc-studio/reviews/verdicts/<unit>/<name>.txt as a reviewer does. 3. Run critic.py brief --unit <unit> --seat qa: it reports the self-check stale although the unit's own change did not move.

## Proposed Fix

Leave the verdicts directory (sdlc-studio/reviews/verdicts/) out of the digest alongside the self-check log and the ledger, and pin it with a test that writes a verdict file under a unit declaring sdlc-studio/reviews/ and finds the self-check still current.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects declares `sdlc-studio/reviews/` and whose self-check is recorded, when a reviewer writes a verdict file under `sdlc-studio/reviews/verdicts/<unit>/` and `critic.py brief --unit <unit> --seat qa` runs, then the self-check reads as current and the brief is issued. Fails on: the verdict file moving the Affects digest, so the brief refuses a stale self-check.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_review_writes.py::VerdictFilesLeaveDigestTests
  - **Verified:** yes (2026-11-22)
- [ ] **AC2** Given the same unit, when a file under `sdlc-studio/reviews/` other than the review tooling's own writes changes, then the self-check still reads as stale. Fails on: the exclusion widened to the whole reviews directory.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_review_writes.py::OtherReviewFilesStillStaleTests
  - **Verified:** yes (2026-11-22)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Acceptance criteria authored for building in lane C2 |
