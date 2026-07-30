# BG0302: conformance.adopt_after still 310 after D0055's restore condition fired twice

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 5
> **Affects:** sdlc-studio/.config.yaml, sdlc-studio/decisions.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

D0055 and the config comment commit to restoring `adopt_after` to 82 when CR0404 lands or an APPROVE round returns, whichever comes first; both triggers have occurred (CR0404 Complete 2026-07-23, RV0020 APPROVE 2026-07-27) and the restore never happened, leaving 228 units exempt from the conformance gate past the exemption's stated expiry.

## Steps to Reproduce

Evidence (`conformance.adopt_after`, line 38 (and decisions.md row D0055)): CR0404 is Status: Complete (commit 0c474114, 2026-07-23); RV0020 records APPROVE ratified 2026-07-27; .config.yaml line 38 still reads '`adopt_after`: 310' and was edited as recently as 2026-07-26 without the restore.

## Proposed Fix

Set `conformance.adopt_after` back to 82, note the restore in the D0055 row, and run the conformance sweep to surface what the re-armed gate now flags.

## Acceptance Criteria

### AC1: the restored threshold is in force

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `shell grep -q 'adopt_after: 82' sdlc-studio/.config.yaml`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
