# BG0743: a signed report's digest covers prose that is edited in place, so an unrelated amendment to a decision rationale invalidates a signature over an unchanged run

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Raised by the independent engineering seat across two rounds of BG0719's review, 2026-09-22, and ruled non-blocking for that unit because it is a design question about what the digest should cover at all. The seat noted that BG0719's lower bound shrank the exposure from 67 rows spanning the project to the handful authored inside the run being signed, which is a different order of risk but not zero. D0074's in-place amendment is the concrete proof that rationales are edited after the fact.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0719 puts each in-force waiver's rationale into the report of record, and it enters the fingerprint like any other figure. Decision rationales are amended in place - D0074 carries `SCOPE CORRECTED 2026-07-28 (BG0361)` appended long after it was written - and `decisions.backfill_superseded` rewrites statuses wholesale. Either changes the digest of a page that was signed over a run whose facts did not move. The window bound BG0719 applies covers WHEN a decision was dated, not when its text was last edited, so it cannot help. This is BG0718's scar arriving through a figure's CONTENT rather than its date, and it is shared with every other prose figure on the page.

## Steps to Reproduce

1. Derive and sign a report whose window contains an accepted waiver.
2. Amend that decision's Rationale cell in place, as D0074 was amended.
3. Re-derive the report: the fingerprint has moved and the signature no longer validates, though nothing about the run changed.

## Proposed Fix

Decide deliberately what the digest covers. Either freeze the prose into the report at derivation time so a later edit cannot reach it, or exclude free-text figures from the digest and digest their identity instead - the decision id and date rather than its rationale. The second is cheaper and keeps the disclosure readable; the first keeps the page self-contained. Either way it should be one recorded ruling covering every prose figure, not a per-section judgement.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0719 puts each in-force waiver's rationale into the report of record, and it enters the fingerprint like any other figure.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_an_amended_waiver_rationale_does_not_invalidate
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** The proposed fix lands, pinned by a test: Decide deliberately what the digest covers.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_listed_waiver_amended_or_superseded_and_an_unlisted_one_do_not_invalidate
  - **Verified:** yes (2026-09-25)

## Impact

A signature is a claim about a run. If it can be broken by editing prose in an unrelated file, the signature measures the repository's current text rather than the run's facts - which is the property BG0718 was filed to establish and this reintroduces through a different door.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Verify lines added: fixed by US0941/BG0775 (the digest leaves waiver prose that moves independently out; an amended rationale no longer invalidates) |
