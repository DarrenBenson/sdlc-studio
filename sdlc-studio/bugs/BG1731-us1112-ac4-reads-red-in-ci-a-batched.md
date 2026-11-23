# BG1731: US1112 AC4 reads red in CI: a batched node over its per-verifier ceiling is also spawned on its own

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py, conftest.py, tools/tests/test_conftest_env.py, changelog.d/BG1731.md
> **Evidence:** GitHub Actions scheduled run 45196238545 (corpus-verify, 65dc7d62): red-criteria 2, NEW US1112::AC4; passes locally on Python 3.14 at 94b4b86e
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T16:15:50Z

## Summary

In the scheduled corpus-verify run 45196238545 (GitHub runner, Python 3.12.16, commit 65dc7d62), `VerifyLaneBatchTests::test_a_batched_node_over_the_per_verifier_ceiling_reads_red` failed in the batch and again in its own run (13.99 s): the lane ran `[('test_fast', 'batch'), ('test_slow', 'batch'), ('test_slow', 'spawn')]`, so the 3 s node under a 2 s ceiling was read from the batch and then spawned on its own, which US1112 AC4 forbids.

The cause is not the Python version. The corpus-verify step sets `SDLC_VERIFY_RED_DETAIL` (`.github/workflows/lint.yml`), and the test's `_env()` copies the outer environment into the nested lane. With that variable set, `verify_ac._record_red` is handed a `rerun` for every red the batch answered (`verify_ac.py`, the `rerun=` at the second `_record_red` call) and runs the verifier alone "for this record". For a node the batch read as over its ceiling that rerun can only time out again: CI's record of it is `exit 124 after 2013 ms`, `timeout`, nothing the batch had not said. Both the variable in CI and the rerun arrived in 663edcd12 (BG1578, 2026-11-22), between the green run of 2026-11-16 (e356db80) and this one. The same test fails locally on Python 3.14.8 with the variable set, and passes without it.

The verdict stays red either way, so the cost is one extra ceiling-length spawn per over-ceiling criterion in any run that records red detail (the corpus job's ceiling is 450 s); but a Done story's criterion reads red, which a release gate's executing verify refuses.

## Steps to Reproduce

1. At HEAD 3791e5193, run
   `python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_a_batched_node_over_the_per_verifier_ceiling_reads_red`:
   it passes (measured, Python 3.14.8).
2. Run it again with `SDLC_VERIFY_RED_DETAIL=<a scratch file>` set, as the corpus-verify step
   sets it: it fails with `+ [('test_fast', 'batch'), ('test_slow', 'batch'), ('test_slow', 'spawn')]`,
   the CI failure word for word (measured).

## Proposed Fix

In `verify_ac.py`, give a batch's ceiling-timeout answer (exit 124 from the batch's ceiling
branch) no rerun for the record: write the batch's answer as the record, since its own spawn
can only time out at the same ceiling. A red the batch answered by a test failure keeps its
rerun, which is what BG1578 asked for. In `test_verify_lane_batch.py`, have `_env()` drop
`SDLC_VERIFY_RED_DETAIL` so the fixture's reds stop landing in the outer job's file, and add a
test that runs the lane with the variable set to a scratch file.

## Acceptance Criteria

- [ ] **AC1** Given `SDLC_VERIFY_RED_DETAIL` set to a scratch file, as the corpus-verify step sets it, when US1112 AC4's test runs, then it passes. Fails on: HEAD, where the lane logs `('test_slow', 'spawn')` beside the two batch entries (measured locally on Python 3.14.8, the CI failure's exact diff).
  - **Verify:** shell f="$(mktemp)"; SDLC_VERIFY_RED_DETAIL="$f" python3 -m pytest -q -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_a_batched_node_over_the_per_verifier_ceiling_reads_red; rc=$?; rm -f "$f"; exit $rc
- [ ] **AC2** Given a lane run with `SDLC_VERIFY_RED_DETAIL` set to a scratch file and a batched node over its per-verifier ceiling, then the node is never spawned on its own, and the file records it once as `red: US9101::AC1` with the batch's timeout answer and exit 124. This is the root cause found: `_record_red`'s rerun for the record, active only when the variable is set. Fails on: HEAD's rerun, which spawns the node again for a ceiling's length to record `timeout`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_a_ceiling_timeout_is_recorded_without_its_own_run
- [ ] **AC3** Given a red the batch answered by a failing test, with the variable set, then it is still run alone and its own output (`rerun-marker`) is recorded under the batch's answer. Fails on: a fix that drops the rerun for every batch answer, undoing BG1578.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_corpus_verify_red_detail.py::CorpusVerifyRedDetailTests::test_a_red_the_batch_answered_is_run_alone_for_its_output

- [ ] **AC4** Given `SDLC_VERIFY_RED_DETAIL` set to a file in the environment that starts the test session, as CI's corpus-verify step sets it, when a test verifies a Done fixture story whose criterion is red, then nothing is written to that file: the repository's `conftest.py` unsets the variable for the session as it unsets the harness homes, so only the corpus lane's own reds reach the record. Fails on: HEAD, where fixture stories wrote 129 of the 131 red blocks in run 45196238545's red-detail file (US0001 46 times, US9101 15, US0002 14), burying US0253::AC2 and US1112::AC4.
  - **Verify:** shell f="$(mktemp)"; SDLC_VERIFY_RED_DETAIL="$f" python3 -m pytest -q -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py tools/tests/test_conftest_env.py; rc=$?; test "$rc" -eq 0 && test ! -s "$f"; r=$?; rm -f "$f"; exit $r

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: root cause found from the CI log and the code, and reproduced locally on 3.14.8: CI sets `SDLC_VERIFY_RED_DETAIL`, the test passes it to the nested lane, and `_record_red` reruns the over-ceiling node for the record (663edcd12, BG1578); Python 3.12 is not the cause. Three executable criteria, a control among them; Affects narrowed to verify_ac.py and the lane test; 3 to 2 points |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | AC4 folds in the same-class leak the qa groom found: every fixture inherits CI's SDLC_VERIFY_RED_DETAIL and writes its own reds into the corpus record; the fix unsets it in conftest.py. Affects + conftest.py, tools/tests/test_conftest_env.py; Points 3 |
