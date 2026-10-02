# BG0861: Nothing opens a delivery batch since US0918, so every finding is stamped raised outside a batch and the close's finding-placement figure is always empty

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_busy_eacces.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_span_retired.py, changelog.d/BG0861.md
> **Evidence:** BG0856-BG0858 Raised-in-batch stamps; run-state.json batches []; git log -S 'start_batch(' -> 2bc6eb15 (US0918)
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:53:30Z

## Summary

> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: `start_batch(` has no caller outside tests (definition at lib/run_state.py:1652); 357 bug files carry 'none open - raised outside a delivery batch'; `close_batch` has no non-test caller. Groomed as the retirement option, a deletion.

RUN-01M3RPSK (2026-09-30): BG0856, BG0857 and BG0858, filed while the run was open and its units were being delivered, all carry 'Raised-in-batch: none open - raised outside a delivery batch', and the close dry run reports 'finding placement: 0 raised at a batch boundary, 72 raised outside one, across 0/0 reviewed batch(es)'. run-state holds `batches: []`. `run_state.start_batch` has no caller: `git log -S 'start_batch('` shows US0918 (2026-09-26, one verdict ledger; the review-batch verbs retired) removed the last one. The attribution US0561 built (a finding priced where the work was, not as close overhead) and the report's placement figure are fed by nothing (LC-003).

## Steps to Reproduce

grep -rn '`start_batch(`' .claude/skills/sdlc-studio/scripts: only the definition. Then any finding filed during an open run carries the 'none open' stamp.

## Proposed Fix

Retire, do not revive. Delete the delivery-batch span API nothing opens (`run_state.batches`, `open_batch`, `start_batch`, `close_batch`, `note_finding` and the `batches` key's writers), `file_finding._open_batch_key` / `_attribute_to_open_batch`, and the close's `finding placement` clause (`sprint._finding_placement`, `_findings_outside_batches`) with the tests that pin them. The `Raised-in-batch` stamp stays as written today: `sprint_report` and `close_owed` read its timestamp to place a finding in a run, so its text and readers are untouched. Old run records keep their `batches` key; nothing reads it.

## Acceptance Criteria

- [ ] **AC1** Given a fixture open run with one batch unit and a bug filed during it by `file_finding.py`, when `sprint.py close --dry-run` runs, then its output carries no `finding placement` text, the bug still carries a `Raised-in-batch` stamp ending in an ISO-8601 timestamp, and `lib/run_state` exposes no `start_batch`, `open_batch` or `close_batch`. Fails on: HEAD prints 'finding placement: 0 raised at a batch boundary, N raised outside one' and keeps the uncalled span API
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_span_retired.py::BatchSpanRetiredTests::test_the_close_reports_no_finding_placement_and_the_span_api_is_gone
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
| 2026-10-01 | backlog value pass (D0291) | Groomed: premise executed at HEAD; the retirement option chosen (a deletion; reviving a span would add machinery); the stamp's timestamp kept for its readers; Affects names the lock tests that call start_batch; Points 3 kept |
