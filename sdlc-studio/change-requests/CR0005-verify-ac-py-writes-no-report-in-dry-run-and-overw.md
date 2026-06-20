# CR-0005: verify_ac.py writes no report in dry-run and overwrites a single report with no run history

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The dry-run preview prints a non-zero change count but persists no machine-readable record of which ACs would flip, and live runs overwrite a single verify-report.json with no run-id or append log (it does carry a `generated_at` timestamp), so there is no audit trail or regression detection for the gate that makes Done mean done.

## Problem

Two gaps in the same report-writing path. (1) In verify_story a passing-but-unverified AC increments report.changed in both apply and dry-run branches (verify_ac.py:311-315) and stale flips at :328-332, and cmd_run prints 'changes=N' for the [DRY] tag (:400-406), but write_report is only called when not dry_run (:414-416). So 'verify_ac.py run --dry-run' reports 'changes=7' with no enumerable record of which ACs would change - the safe preview's most actionable output is non-recoverable. (2) Even on live runs write_report does path.write_text(json.dumps(...)) (:350-368), fully overwriting with no run-id or append history (it does set a `generated_at` timestamp), so Verified state can flip green->red->green across runs with zero forensic trail and you cannot answer 'when did AC-3 last pass?'. There is no retry/iterate loop either.

## Proposed Changes

### Item 1: verify_ac.py writes no report in dry-run and overwrites a single report with no run history

**Priority:** Medium **Effort:** TBD

Write the report in dry-run too (distinct path or dry_run flag) and include in StoryReport an explicit list of (ac_id, old_state, new_state) so the dry-run summary enumerates the pending flips rather than printing an opaque count. Additionally append each run as a line to .local/verify-history.jsonl (run timestamp, story id, per-AC pass/fail/stale, exit codes) alongside the snapshot, and optionally surface a 'regressed since last run' / 'flaky AC' signal in reconcile --verify.

## Impact Assessment

### Existing Functionality

The dry-run preview is not auditable (operators told N changes would occur with no list of which), and live runs leave no regression trail for the one gate that makes 'Done' trustworthy. Quality risk medium; reuses existing subprocess/JSON plumbing.

## Acceptance Criteria

- [x] A report is written in dry-run too (distinct path or `dry_run` flag), enumerating each pending `(ac_id, old_state, new_state)` flip rather than an opaque count.
- [x] Each run appends a line to `.local/verify-history.jsonl` (timestamp, story id, per-AC pass/fail/stale, exit code).
- [x] Unit-tested.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (backlog-closeout) | Complete - US0019: dry-run report enumerates flips + verify-history.jsonl append log |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism / external-benchmark; evidence: .claude/skills/sdlc-studio/scripts/verify_ac.py:311-315 (changed incremented in dry-run branch) and :414-416 (write_report only when not dry_run); :350-368 (write_report overwrites a single snapshot with no run-id/append; it does set generated_at)) |
