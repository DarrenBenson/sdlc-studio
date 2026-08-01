# CR-0519: a suite verdict is read from a file, never from a pipe that can swallow the exit code

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** tools/run-suite.sh, tools/tests/test_run_suite.sh, AGENTS.md
> **Date:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

The suite runners set `set -uo pipefail` correctly. The failure is one level up, in how an agent INVOKES them: `npm test 2>&1 | tail -15` reports tail's exit status, not the suite's, and the pipeline's own shell has no pipefail. A red suite then reads as green.

This happened twice in one session. A commit was reported here as landed on the strength of a masked exit 0 when the hook had in fact refused it, and a full suite was reported green when a real failure (a `__main__` guard no longer last in the file) was sitting in it. Both were caught later by accident rather than by anything that would reliably catch them. The output of a 6-minute suite does not fit in a terminal read, so piping to `tail` is the natural thing to do and will keep being done.

The gate already writes `sdlc-studio/.local/gate-suite-verdict.json`. Nothing equivalent exists for a suite an agent runs by hand, which is precisely when nobody is checking.

## Impact

Every 'the suite is green' claim made through a pipe is unverified, and the two most expensive mistakes of this session were both of that shape. It is not fixable by resolving to be careful: the pipe is there because the output is too long to read, so the incentive recurs on every run. A wrapper that writes the verdict to a file removes the incentive rather than asking the agent to resist it.

## Acceptance Criteria

- [ ] `tools/run-suite.sh <scripts|tools|all>` runs the suite and writes {suite, `exit_code`, passed, failed, duration, `head_sha`} to sdlc-studio/.local/suite-verdict.json.
- [ ] It prints only the verdict line, so there is nothing worth piping to `tail` and the incentive that causes the masking is removed rather than resisted.
- [ ] A non-zero suite writes a verdict recording the failure - a red run must not leave a file that reads as green, or the wrapper reproduces the defect it replaces.
- [ ] The verdict records the HEAD sha it was taken at, so a stale verdict is distinguishable from a current one.
- [ ] The commit gate refuses a greenness claim whose verdict file is absent or stale against HEAD, so the rule is enforced by the command people run rather than stated in AGENTS.md (LL0027).
- [ ] A test pins that a failing suite produces `exit_code` != 0 in the file - the mutant is a wrapper that always writes zero.

## Recommendation

Ship `tools/run-suite.sh <scripts|tools|all>` which runs the suite, writes `{suite, exit_code, passed, failed, duration, head_sha}` to `sdlc-studio/.local/suite-verdict.json`, and prints only the verdict line. The agent then READS a fact instead of interpreting a stream. State in AGENTS.md that a suite claim cites that file, and have the commit gate refuse a claim of greenness whose verdict file is absent or stale against HEAD - which is the gate-it-in-the-command-people-run form (LL0027), not another line of guidance.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Raised |
