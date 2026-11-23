# BG1731: US1112 AC4 reads red in CI: a batched node over its per-verifier ceiling is also spawned on its own

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, changelog.d/BG1731.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** GitHub Actions scheduled run 45196238545 (corpus-verify, 65dc7d62): red-criteria 2, NEW US1112::AC4; passes locally on Python 3.14 at 94b4b86e
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T16:15:50Z

## Summary

In the scheduled corpus-verify run 45196238545 (GitHub runner, Python 3.12, commit 65dc7d62), `VerifyLaneBatchTests::test_a_batched_node_over_the_per_verifier_ceiling_reads_red` failed in the batch and again in its own run (13.99 s): the lane ran `[('test_fast', 'batch'), ('test_slow', 'batch'), ('test_slow', 'spawn')]`, so the 3 s node under a 2 s ceiling was read from the batch and then spawned on its own, which US1112 AC4 forbids. The same test passes locally on Python 3.14 (17 s), and was green in the scheduled run of 2026-11-16 (e356db80). The verdict stays red either way, so the cost is one extra ceiling-length spawn per slow criterion where it happens; but a Done story's criterion is red, which a release gate's executing verify refuses.

## Steps to Reproduce

Run the test on a GitHub-hosted Ubuntu runner with Python 3.12, as the scheduled corpus-verify job does: `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_a_batched_node_over_the_per_verifier_ceiling_reads_red`. Observe the extra ('`test_slow`', 'spawn') entry. Locally on Python 3.14 it passes.

## Proposed Fix

Find what differs on the runner first (Python version, core count, the batch's junit duration, or a change between e356db80 and 65dc7d62 in `verify_ac.py` or gate.py), reproducing it before changing code; then make the lane read an over-ceiling batched node as red without a second spawn on every supported Python, and pin that in the test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In the scheduled corpus-verify run 45196238545 (GitHub runner, Python 3.12, commit 65dc7d62)...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run the test on a GitHub-hosted Ubuntu runner with Python 3.12, as the scheduled corpus-verify job does: `python3 -m pytest...
- [ ] **AC3** The proposed fix lands, pinned by a test: Find what differs on the runner first (Python version, core count, the batch's junit duration, or a change between e356db80 and 65dc7d62 in `verify_ac.py` or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
