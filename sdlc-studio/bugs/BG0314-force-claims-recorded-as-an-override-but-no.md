# BG0314: --force claims 'recorded as an override' but no record of a forced bypass is ever written

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

The flag's help promises the bypass is recorded, but force only short-circuits gate checks: neither the artefact file, the result dict, nor the telemetry close event carries any override marker, so a forced close of a red-AC story is byte-indistinguishable from a verified one - contradicting the file's own doctrine at lines 366-368 that 'a force flag is not' auditable.

## Steps to Reproduce

Evidence (`cmd_set` --force help text (lines 1114-1115); `_pre_write_gates` lines 690/705/730; `_post_write_sync_and_record)`: grep across transition.py shows force used only in gate conditions and help text; telemetry.py has no override field; `_post_write_sync_and_record` writes only status stamp, index sync, cascade and metrics.

## Proposed Fix

On a forced transition, annotate the artefact (and the telemetry event) with an override record naming the bypassed gate and the flag - or, failing that, correct the help text to stop claiming auditability.

## Acceptance Criteria

### AC1: a forced bypass is recorded on the artefact

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ForcedOverrideRecordTests::test_forced_bypass_is_recorded_on_the_artefact`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
