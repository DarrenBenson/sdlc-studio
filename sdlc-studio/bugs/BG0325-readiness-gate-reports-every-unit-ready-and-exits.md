# BG0325: Readiness gate reports every unit ready and exits 0 when the cross-epic AC checker crashes

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

`audit_batch` wraps the whole `ac_scope.check` sweep in a bare 'except Exception: cross = {}' with no message, silently erasing every cross-epic-ac finding including BLOCKING strength>1 hits that would flip units to not-ready and the exit code to 1 - the gate reports a verdict it never computed, and the 'advisory' comment mislabels a lane the surrounding code treats as blocking.

## Steps to Reproduce

Evidence (`audit_batch()` lines 483-496 (swallow at 493-494); `audit_unit()` lines 447-453; `cmd_tranche` line 536): Lines 489-494 show the keep-the-strongest-hit logic immediately above the swallow; line 453 appends the blocking issue; line 536 keys the exit code off `not_ready`; the unwrapped `detect_integrity` call in the same function shows the swallow is the anomaly.

## Proposed Fix

On `ac_scope.check` failure, print a stderr warning and either fail the command or mark affected units not-ready with a 'cross-check unavailable' issue - never return a clean verdict that was not computed.

## Acceptance Criteria

### AC1: a crashing cross-check is reported, not swallowed

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::CrossCheckUnavailableTests::test_crashing_cross_check_is_reported_not_swallowed`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
