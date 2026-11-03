# BG1190: A verifier that times out is killed alone, so its children run on and load every verifier after it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py, changelog.d/BG1190.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** US1113 builder report, 2026-11-03: the sleep probe, and the 8-worker against 1-worker red-id comparison on the real corpus.
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T08:24:42Z

## Summary

2026-11-03, US1113's build (run five). `verify_ac.run_verifier` spawns a criterion's command with `subprocess.run(..., timeout=...)` (`verify_ac.py`:521-526), and under `shell=True` a timeout kills only the shell. US1113's builder ran `shell sleep 37 && echo x` under a 1 s ceiling and `sleep 37` was still running afterwards. On the release verify lane's worker pool, two verifiers that timed out (US0926 AC1 and US0944 AC3) left their children running, and US0164 AC1, whose `serial_only` tests bound wall-clock time, then failed in 38 s against 29 s alone. With 8 workers the lane read 4 criteria red, against 1 on one worker. The cause is the builder's reading and is not yet confirmed; the leak itself is reproduced. US1112's batch already kills its phases as a process group (`verify_ac.py`:1861-1871).

## Steps to Reproduce

1. A story with `- **Verify:** shell sleep 37 && echo x`.
2. `verify_ac.py run --id <it> --timeout 1`: the criterion reads red as a timeout.
3. `pgrep -f 'sleep 37'` still finds the child.

## Proposed Fix

Start each verifier in its own session and kill its process group on a timeout, the way `pytest_batch_cache` kills a phase, then reap it before the verdict is returned.

## Acceptance Criteria

- [ ] **AC1** A shell verifier that times out leaves no process of its group running once `verify_ac.run_verifier` returns, and still reads red as a timeout.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py

## Impact

Every timeout leaves work running that the next verifiers compete with, so one slow criterion can turn passing criteria red, most of all on the release lane's worker pool.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
