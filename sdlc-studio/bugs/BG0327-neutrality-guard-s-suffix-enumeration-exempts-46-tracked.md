# BG0327: Neutrality guard's suffix enumeration exempts 46 tracked files, including shipped .template payload, .jsonl evidence log

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/check_neutrality.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The checker's contract is to fail on a private name in any tracked file, but it scans only a hardcoded suffix set; 46 tracked text files are silently exempt - all shipped templates/automation/*.template (instantiated by every consuming project, the highest-risk leak site), every retros/evidence/*.jsonl, the extensionless .githooks scripts, CODEOWNERS, and .version - so a leak in any of them commits and ships green.

## Steps to Reproduce

Evidence (`_TEXT_SUFFIXES` (lines 33-35) as consumed by `_tracked_text_files` (lines 61-75)): Lines 34-35 and 72-74 show the suffix filter; running the real matcher over the skipped population confirms 46 tracked files fall outside it (0 current hits, latent gap); the module applies LL0008 for git failures but the suffix list is the LL0013 enumeration failure.

## Proposed Fix

Invert the filter: scan every tracked file and skip a small binary/lockfile denylist (or sniff for null bytes), so .template, .jsonl, and extensionless text files are covered by default.

## Acceptance Criteria

### AC1: the neutrality guard scans every tracked text file, not an enumerated suffix set

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest tools/tests/test_check_neutrality.py::ScanCoverageTests, written red before the fix and green after
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-28 | Claude Fable 5 | Delivered in RUN-01KYJZGZ; acceptance criteria authored at review against the tests that landed |
