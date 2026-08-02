# BG0492: the suite verdict binds to HEAD rather than the tree, and --check ignores which suite ran

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/run-suite.sh, .githooks/commit-msg, tools/tests/test_run_suite.py
> **Severity:** Medium
> **Points:** 3

## Summary

Two fail-opens in the verdict mechanism, both outside US0610/US0611's ACs as written and both real.

The verdict records `head_sha` only, so it authorises the COMMIT rather than the tree. Since a verdict is necessarily taken at the parent commit, any subsequent edit is covered by it: with a green verdict at HEAD, staging a syntactically broken .py and running the commit-msg hook on a 'Both suites green.' message returns rc=0. That is the stale-green-looking-current case the epic exists for; AC2 defines staleness by commit only.

And `--check` never reads the `suite` field, so a verdict from `run-suite.sh scripts` satisfies a claim of 'both suites green' - which is the exact phrasing the commit-msg lane's own regex matches.

## Steps to Reproduce

1. `tools/run-suite.sh all`, commit. Verdict is green at HEAD.
2. Stage a file with a syntax error. Run `bash .githooks/commit-msg` on a message saying 'Both suites green.' -> rc=0.
3. `SUITE_CMD_OVERRIDE='exit 0' tools/run-suite.sh scripts` then `tools/run-suite.sh --check` -> GREEN, though only one suite ran.

## Proposed Fix

Record a hash of the tracked working tree beside `head_sha` and refuse when it moves. Record and check the `suite` field, so a claim naming both suites needs a verdict from `all`. Both are cheap; the second is a one-line comparison.

## Impact

The verdict is the repo's answer to 'was it green', and both holes let it answer yes for a state it never observed. The first is the more dangerous: it authorises uncommitted edits, which is the normal state of a working tree mid-session.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
