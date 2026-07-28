# BG0336: Review-currency close-bookkeeping carve-out is direction-blind: any hand-edited Status flip, including to Done, is exemp

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

A changed diff line is classed as close bookkeeping whenever it merely contains one of five substrings (Status:, Verified:, etc.) with no check of direction or value, so a hand-flip of Status from Blocked/Draft straight to Done, or a reopen of Done, passes the review-currency lane as 'changed only in close bookkeeping' and gate --require-review prints PASS over a status change no reviewer ever judged.

## Steps to Reproduce

Evidence (`_CLOSE_OWNED_FIELDS` line 1152, `_close_owned_change_only` lines 1196-1204, consumed by `_review_current` lines 1250-1271): gate.py 1196-1204: a '+> **Status:** Done' line matches the 'Status:' substring for any from/to pair; `_review_current` returns count 0 non-blocking; the baseline is the last commit touching LATEST.md, so the exemption spans every status edit since the last review.

## Proposed Fix

Make the carve-out value-aware: exempt a Status: line only when the transition is one the close tooling itself records (e.g. Review to Done alongside sign-off fields), and treat any other status flip - especially any line whose new value is Done or that reopens a terminal status - as a substantive change requiring review currency.

## Acceptance Criteria

### AC1: a status change the close did not record still demands re-review

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseBookkeepingTests
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | Claude Fable 5 | Acceptance criterion authored at review - the unit reached Fixed without one, which CR0459 exists to refuse |
