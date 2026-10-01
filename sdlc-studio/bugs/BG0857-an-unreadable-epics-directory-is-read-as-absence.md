# BG0857: An unreadable epics directory is read as absence by reconcile's detectors, so the gate and migrate report a drift count with no mention that part of the workspace was never read

> **Status:** Won't Fix
> **Closed with findings in:** D0291, discovery backlog sweep 2026-10-01 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py,.claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG0857.md
> **Evidence:** BG0842 QA review (subagent a52cb751), 2026-09-30
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T09:42:35Z

## Summary

Found by BG0842's QA review (RUN-01M3RPSK, 2026-09-30): on a fixture with `chmod 000 sdlc-studio/epics`, `gate.py --only reconcile` reports '2 drift item(s)' and `migrate` reports '2 index/status drift item(s)', and neither names the unreadable directory. The count reads as the workspace's drift when a whole artefact type was skipped. Identical at 06f90e1a, so pre-existing; the cause is reconcile's detectors. An absent, empty and unreadable input read the same way is LC-006.

## Steps to Reproduce

Copy a workspace with epics, `chmod 000 sdlc-studio/epics`, run `gate.py --root <copy> --only reconcile` and `migrate.py --root <copy>`: both print a drift count and exit as usual, naming nothing unreadable.

## Proposed Fix

In reconcile's per-type read, tell an unreadable type directory (PermissionError) apart from an absent one and surface it as its own drift item or error naming the path, so the gate lane and migrate, which share the tally since BG0842, both report it.

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose sdlc-studio/epics directory is unreadable, when `gate.py --only reconcile` runs, then its output names the unreadable directory and the lane does not report PASS. Fails on: HEAD, which counts the other types and says nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::UnreadableTypeDirTests::test_an_unreadable_type_directory_is_named_not_skipped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
