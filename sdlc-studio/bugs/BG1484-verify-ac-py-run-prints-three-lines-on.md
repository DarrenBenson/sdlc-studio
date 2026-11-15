# BG1484: verify_ac.py run prints three lines on a clean single-story success since BG1395 added its total line, turning test_quiet_success red at the push boundary

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py, .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py, changelog.d/BG1484.md
> **Evidence:** Push boundary on devserver1 for 46db0430, 2026-11-15: test_quiet_success subtest verify_ac.py run success, 3 lines.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T21:56:36Z

## Summary

BG1395 (f446773f) added a `total:` line to `verify_ac.py run`. On a clean run over one story the command now prints the story line, the total line and the `wrote .../verify-report.json` line, and `test_quiet_success.py`::QuietSuccessTests::`test_each_command_is_quiet_on_success_and_verbose_on_refusal` (subtest `verify_ac.py` run success) requires one or two. The push boundary for 46db0430 failed on it (1 failed, 9078 passed), so main cannot be pushed. The lane's selected tests did not include `test_quiet_success`, a repeat of LC-019 (a push-gate guard the per-commit run skips).

## Steps to Reproduce

1. At 46db0430, run pytest .claude/skills/sdlc-studio/scripts/tests/`test_quiet_success.py.`
2. See the `verify_ac.py` run success subtest fail with 3 lines.

## Proposed Fix

Keep a clean single-story run to two lines: print the total line only when the run covers more than one artefact or when a criterion is partly skipped, or drop the wrote-line on a quiet success, while BG1395's criteria still pass.

## Acceptance Criteria

- [ ] **AC1** Given a story whose one criterion passes, when `verify_ac.py run --id <story>` runs, then it prints one or two lines and exits 0, while a run over two stories or with a partly-skipped criterion still prints the total line BG1395 added. Fails on: a third line on a clean single-story success.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py
  - **Verified:** yes (2026-11-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
