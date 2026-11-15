# BG1427: file_finding.py --parent writes the parent's Decomposed-into but not its index row's spawned-work cell, so the next commit is refused for reconcile drift

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_parent_index_cell.py, changelog.d/BG1427.md, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Backlog triage 2026-11-14: CR0702 filed under RFC0063; the D0474 commit refused on reconcile drift
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (backlog triage orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-14T21:00:03Z

## Summary

Filing CR0702 with --parent RFC0063 on 2026-11-14 added CR0702 to RFC0063's `Decomposed-into:` line, but left the spawned-work cell of RFC0063's row in sdlc-studio/rfcs/_index.md without it. The pre-commit gate's reconcile lane then refused the commit with one spawned-column drift item, cleared only by a separate `reconcile.py apply`.

## Steps to Reproduce

Run `file_finding.py` file --type cr --parent <an RFC with an index row> --title ..., then reconcile.py detect: one spawned-column drift item names the parent.

## Proposed Fix

When --parent writes the parent's Decomposed-into, sync that parent's index cell the way reconcile's spawned-column apply does (`children_of).`

## Acceptance Criteria

- [ ] **AC1** Given a finding filed with --parent naming an RFC that has an index row, when the filer returns, then reconcile detect reports no spawned-column drift for that parent. Fails on: a parent row whose spawned-work cell omits the new child.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_parent_index_cell.py::ParentIndexCellTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | Claude Opus 5.5 (backlog triage orchestrator) | Filed |
