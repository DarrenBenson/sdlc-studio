# BG1247: US1128's benchmark runner kills only the CLI on a timeout, never cross-checks Claude Code's own dollar total, and leaves its wall time, timeout and skill switches unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_headless.py
> **Evidence:** run seven (RUN-01M6RAP7) US1128 review rounds 1 and 2
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:36:30Z

## Summary

Run seven, US1128 rounds 1 and 2 (round 2 APPROVE). Non-blocking findings outside the High bug on authentication and a nested `--dest`: (1) A timeout kills only the CLI process, not its process group (`runner.py:328` at round 1): a grandchild the fake CLI spawned wrote `LATE.txt` into the workspace after the run was refused at 1.2 s, so an unattended agent's background commands outlive the run. (2) `run_headless` does not pass prices to `harness_usage.parse` (`runner.py:333` at round 1), so Claude Code's `total_cost_usd` cross-check is always unchecked and `usage_disagreements` can never report a cost mismatch. (3) Test gaps by mutation (25 mutants in round 1 with 15 killed, 14 in round 2 with 10 killed): a constant `wall = 0.0` survives (`runner.py:386`; the test at :250 checks only the type); dropping the git and `CLAUDECODE` environment scrub survives; dropping the subprocess timeout survives; a partial dollar figure for a half-priced mix survives (`runner.py:512`, "never a partial one"); removing the prompt from the copilot or opencode command survives, because neither CLI is run even as a fake; removing claude's `bypassPermissions` or codex's `--sandbox` survives; dropping OpenCode's singular global `skill` directory (`runner.py:271`) survives, because `test_bench_headless.py:300` seeds only `skills` while OpenCode 1.18.34 globs `{skill,skills}/**/SKILL.md`; and dropping `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` alone (`runner.py:258`) survives, because the fake models `OPENCODE_DISABLE_EXTERNAL_SKILLS` as its superset.

## Steps to Reproduce

1. Run `tools/bench/runner.py run` with a fake CLI that spawns a grandchild which sleeps past `--timeout` and then writes a file: the file appears in the workspace after the run is refused. 2. Apply the mutants above in a scratch copy and run `pytest tools/tests/test_bench_headless.py`: each passes.

## Proposed Fix

Start the CLI with `start_new_session=True` and kill its process group on timeout; pass the loaded price table to `harness_usage.parse`; assert a measured wall time above zero with a fake that sleeps, a refused run for a fake that outlives the timeout, the scrubbed variables in the CLI's environment, no dollar figure for a half-priced mix, the prompt and permission flags in every harness's command, the singular OpenCode `skill` directory, and each OpenCode switch on its own.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US1128 rounds 1 and 2 (round 2 APPROVE).
- [ ] **AC2** The proposed fix lands, pinned by a test: Start the CLI with `start_new_session=True` and kill its process group on timeout; pass the loaded price table to `harness_usage.parse`; assert a measured wall...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
