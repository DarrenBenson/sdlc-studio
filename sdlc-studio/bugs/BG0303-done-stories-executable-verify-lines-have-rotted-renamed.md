# BG0303: Done stories' executable Verify lines have rotted: renamed and deleted tests leave terminal stories whose proof can neve

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 5
> **Affects:** sdlc-studio/stories/US0187-refine-copies-the-request-s-acceptance-criteria-into.md, sdlc-studio/stories/US0212-fix-the-trd-section-6-migrations-paragraph-to.md, sdlc-studio/stories/US0013-tranche-audit-step.md, sdlc-studio/stories/US0022-checks-remediation-guidance.md, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

At least four Done stories carry executable Verify lines that fail or match nothing today: US0187 AC3's unittest selector was renamed away by US0411 (which also reversed the behaviour AC3 asserts), US0212 AC2's grep target was rewritten by CR0365 because the pinned claim was false, and US0013/US0022 point at `test_audit.py`, deleted by the US0345 rename. The 'Done only when executable ACs pass' doctrine is violated on disk, test renames/deletions never repair coupled units, and neither reconcile detect nor any gate catches it.

## Steps to Reproduce

Evidence (US0187 AC3 (lines 35-41); US0212 AC2 (lines 27-33); US0013 AC Verify lines 32/40/48; US0022 line 59): `verify_ac` run --story US0187 reports 'FAIL AC3' (raw shell run collects 0 tests, exits 0); `verify_ac` run --id US0212 reports 'FAIL AC2'; ls scripts/tests/ shows no `test_audit.py` (only `test_audit_cost.py`, `test_audit_profiles.py`, `test_command_audit.py)`; all four stories are Status: Done and reconcile.py detect exits with `drift_items`=0.

## Proposed Fix

Repair the four stories (re-point or supersede the dead selectors with a revision note), then add a scheduled or gate lane that re-runs `verify_ac` (or at least existence-checks pytest/unittest targets) over terminal stories so a rename or deletion surfaces at the commit that causes it.

## Acceptance Criteria

### AC1: the four repaired stories verify green again

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `.claude/skills/sdlc-studio/scripts/verify_ac.py run --id US0187`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
