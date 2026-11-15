# BG1466: A signed report's signoff principal and signed_at figures still read not yet signed, though the evidence schema says they hold who signed and when

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, changelog.d/BG1466.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Run fourteen grooming at 8abcfb17: all 29 signed reports under sdlc-studio/reports/ show it.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:23:31Z

## Summary

Every signed sprint report (29 of them, RPT0031 included) carries the figures signoff.principal, `signoff.signed_at` and `signoff.signed_fingerprint` with the value 'not yet signed', in both the JSON record and the rendered page, because the page is sealed before the signature and the signature is held in the separate top-level `signature` block. reference-evidence-schema.md (near lines 207-209) describes those figures as who signed and when, or 'not yet signed', and says `signed_fingerprint` is filled from `signature` when the page renders. A consumer parsing the record, such as a change board's tooling or a head of engineering reading the evidence, reads the wrong answer for a signed run.

## Steps to Reproduce

1. Open sdlc-studio/reports/RPT0031.json, a signed run's record.
2. Read the signoff figures: each is 'not yet signed'.
3. Compare with the record's top-level signature block, which names the principal and the time.

## Proposed Fix

Either have the record's reader (and the evidence verb) fill the signoff figures from the signature block when they render, as the schema says for `signed_fingerprint`, or reword the schema to say the figures are frozen at the close and the signature block is the one to read.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Every signed sprint report (29 of them, RPT0031 included) carries the figures signoff.principal, `signoff.signed_at` and `signoff.signed_fingerprint` with the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Either have the record's reader (and the evidence verb) fill the signoff figures from the signature block when they render, as the schema says for...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
