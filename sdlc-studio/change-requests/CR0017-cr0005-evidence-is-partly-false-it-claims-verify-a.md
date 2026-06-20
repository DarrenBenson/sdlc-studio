# CR-0017: CR0005 evidence is partly false: it claims verify_ac writes the report 'with no timestamp', but write_report emits generated_at

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** CR0005-verify-ac-py-writes-no-report-in-dry-run-and-overw.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

CR0005's Problem/Summary assert the report is overwritten 'with no timestamp, run-id, or append', but write_report writes a generated_at timestamp; the genuine gap is the missing run-id and append-history.

## Problem

CR0005:18 and :46 state the report is overwritten 'with no timestamp, run-id, or append' and that you 'cannot answer when did AC-3 last pass'. The 'no timestamp' clause is wrong: write_report sets data['generated_at'] = sdlc_md.now_iso8601() (verify_ac.py:353). The real defect is the lack of a per-run-id and an append-only history (single overwriting snapshot), plus the dry-run branch writing nothing. Over-stating it as 'no timestamp' misdescribes the cited code and weakens an otherwise-sound CR.

## Proposed Changes

### Item 1: CR0005 evidence is partly false: it claims verify_ac writes the report 'with no timestamp', but write_report emits generated_at

**Priority:** Low **Effort:** TBD

Reword CR0005 to say the snapshot carries a generated_at timestamp but no run-id and no append history (single overwriting file), and the dry-run branch writes nothing. Keep the proposed verify-history.jsonl append-log fix; drop the inaccurate 'no timestamp' assertion.

## Impact Assessment

### Existing Functionality

A reviewer checking the cited line sees a generated_at timestamp and may reject the whole CR as inaccurate, when only the framing is wrong; the actionable defect (no run-id, no append-history, dry-run writes nothing) survives and should be corrected so the CR is acted on rather than dismissed.

## Acceptance Criteria

- [ ] Reword CR0005 to say the snapshot carries a generated_at timestamp but no run-id and no append history (single overwriting file), and the dr

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: design-rfc) |
