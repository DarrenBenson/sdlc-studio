# BG0861: Nothing opens a delivery batch since US0918, so every finding is stamped raised outside a batch and the close's finding-placement figure is always empty

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0861.md
> **Evidence:** BG0856-BG0858 Raised-in-batch stamps; run-state.json batches []; git log -S 'start_batch(' -> 2bc6eb15 (US0918)
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:53:30Z

## Summary

RUN-01M3RPSK (2026-09-30): BG0856, BG0857 and BG0858, filed while the run was open and its units were being delivered, all carry 'Raised-in-batch: none open - raised outside a delivery batch', and the close dry run reports 'finding placement: 0 raised at a batch boundary, 72 raised outside one, across 0/0 reviewed batch(es)'. run-state holds `batches: []`. `run_state.start_batch` has no caller: `git log -S 'start_batch('` shows US0918 (2026-09-26, one verdict ledger; the review-batch verbs retired) removed the last one. The attribution US0561 built (a finding priced where the work was, not as close overhead) and the report's placement figure are fed by nothing (LC-003).

## Steps to Reproduce

grep -rn '`start_batch(`' .claude/skills/sdlc-studio/scripts: only the definition. Then any finding filed during an open run carries the 'none open' stamp.

## Proposed Fix

Either open a delivery batch span where the lean loop's delivery starts (sprint plan --write, or lane brief) so `file_finding`'s attribution has a span to read, or retire the Raised-in-batch attribution and the close's placement figure together, as a deletion on the record.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose delivery has started, when `file_finding` files a bug, then its Raised-in-batch stamp names the open span, or the stamp and the close's placement figure no longer exist. Fails on: HEAD, where no span can open and every stamp reads 'none open'
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::BatchAttributionTests::test_a_finding_filed_during_delivery_names_the_open_span

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
