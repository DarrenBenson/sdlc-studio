# BG1576: The skill-tests lane's serial_only collection may read empty under an inherited -q, so serial tests could be skipped unseen

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG1519 repair hand-back, run sixteen, 2026-11-18.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T02:08:05Z

## Summary

BG1519's repair (run sixteen) pinned `--color=no --verbosity=-1` on every pytest the count floor reads, because an inherited `PYTEST_ADDOPTS`=-q or `addopts = -q` makes pytest print no summary. The skill-tests lane also runs `pytest --collect-only -q -m serial_only` (gate.py near line 1040) to find the serial tests to run after the parallel phase; under a second inherited -q its node list may come back in a form the lane does not parse. Not reproduced; named by the repair builder.

## Steps to Reproduce

`PYTEST_ADDOPTS`=-q python3 .claude/skills/sdlc-studio/scripts/gate.py --run-tests <a module holding a `serial_only` test>; check the serial test ran.

## Proposed Fix

Pin the verbosity on that collection the way BG1519 pinned it on the count readers, with a test under each inherited form.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1519's repair (run sixteen) pinned `--color=no --verbosity=-1` on every pytest the count floor reads, because an inherited `PYTEST_ADDOPTS`=-q or `addopts =...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: `PYTEST_ADDOPTS`=-q python3 .claude/skills/sdlc-studio/scripts/gate.py --run-tests <a module holding a `serial_only` test>; check the serial test ran.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pin the verbosity on that collection the way BG1519 pinned it on the count readers, with a test under each inherited form.

## Impact

A `serial_only` test silently not run under a user's pytest configuration.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
