# BG0641: there is no pre-push hook, so the two lanes AGENTS.md says bind at the push boundary bind nowhere

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-push, tools/enable-hooks.sh, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Created:** 2026-09-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

AGENTS.md states that `release-rehearsal` and `revert-check` bind at the push and release boundaries, and `gate.py --boundary push` exists to run them. Nothing invokes it. There is no `.githooks/pre-push` and none in `.git/hooks/`, and `core.hooksPath` points at `.githooks`, so a push runs no gate at all - it completes in seconds. Both lanes are therefore documented as binding at a boundary that has no hook behind it, which is the rule-with-no-gate shape AGENTS.md itself names as the weakest available fix.

## Steps to Reproduce

1. `git config core.hooksPath` reports `.githooks`.
2. `ls .githooks/pre-push` and `ls .git/hooks/pre-push` both report no such file.
3. `git push origin main` completes in seconds with no gate output.
4. AGENTS.md's own roster says release-rehearsal and revert-check bind at `push|release`.

## Proposed Fix

Add `.githooks/pre-push` invoking `gate.py --boundary push`, and have `tools/enable-hooks.sh` install and name it beside the other two. Then pin the roster the way `check_spec_claims` already pins the pre-commit lanes: a test that reads AGENTS.md's boundary claims and asserts a hook exists for each named boundary, so the next lane documented at a boundary cannot be documented into a hook nobody wrote.

## Acceptance Criteria

- [ ] **AC1** Given a push, when the pre-push hook runs, then `gate.py --boundary push` is invoked and a failing boundary lane refuses the push
- [ ] **AC2** Given `tools/enable-hooks.sh`, when it runs in a fresh clone, then it installs and NAMES the pre-push hook alongside pre-commit and commit-msg - a hook nobody is told about is one nobody notices missing
- [ ] **AC3** Given AGENTS.md's boundary roster, when the guard reads it, then every boundary it names has a hook that invokes the gate for it, and a boundary with no hook is REFUSED rather than reported

## Impact

Two lanes this project relies on for release confidence have never run at the boundary they claim. `release-rehearsal` walks greenfield init and a v4 upgrade - the two states the repo cannot occupy - and it was written because walking them by hand once found three consumer-facing defects the whole suite had missed. `revert-check` catches a test that passes without the change it covers. Both are off, and the documentation says otherwise.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Filed |
