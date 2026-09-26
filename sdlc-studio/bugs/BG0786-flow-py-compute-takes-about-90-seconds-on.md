# BG0786: flow.py compute takes about 90 seconds on this repository, so its CLI grammar control times out at 120 under load and reddens the push gate

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T13:24:08Z

## Summary

`test_cli_grammar.py`::RootIsReadNotJustParsed::`test_every_listed_verb_can_actually_fail_the_guard` runs flow.py compute against the real repository with a 120s timeout. Measured 2026-09-26 at load ~8: 89s at 93d37f16, 92s at HEAD, so not a regression, but under the push gate's parallel full suite it exceeded 120s and refused the push.

## Steps to Reproduce

time python3 -B .claude/skills/sdlc-studio/scripts/flow.py --root . compute

## Proposed Fix

Profile flow.py compute and cut its cost; or point the control at a fixture root that still names a real artefact, since the control only needs the verb to discriminate.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `test_cli_grammar.py`::RootIsReadNotJustParsed::`test_every_listed_verb_can_actually_fail_the_guard` runs flow.py compute against the real repository with a...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: time python3 -B .claude/skills/sdlc-studio/scripts/flow.py --root .
- [ ] **AC3** The proposed fix lands, pinned by a test: Profile flow.py compute and cut its cost; or point the control at a fixture root that still names a real artefact, since the control only needs the verb to...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
