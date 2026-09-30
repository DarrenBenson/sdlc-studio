# BG0863: An unreadable verdict ledger drops unreviewed units from the close's status rows since BG0859, and the bug remedy is wrong for a bug that already has an APPROVE

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0863.md
> **Evidence:** BG0859 QA review (subagent a302a39d), 2026-10-01
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T23:34:04Z

## Summary

Found by BG0859's QA review (RUN-01M3T8N1, 2026-10-01, APPROVE with this [regression] ruled non-blocking): with a non-UTF-8 critic-verdicts.md, `awaits_only_signature` raises inside `seal_bar_unmet` and `_pre_delivery_status` swallows it into '' (sprint.py:6631, 6635), so the dry run names 1 status STOP where 62af4d6d named 7 (unreviewed bugs included). Mitigated: the same dry run prints review-coverage 'covered by no independent review' and the checklist UnicodeDecodeError, and the real close raises. Also: the bug remedy 'record its independent review, critic.py record ... --verdict APPROVE' is wrong for a bug named despite an APPROVE on record (APPROVE then a standing REJECT, where another reviewer's record is refused), and the approved-CR half of the change and both remedy texts are unpinned (mutants M7, M8, M13 survive).

## Steps to Reproduce

Fixture: an open run with a base ref, an unreviewed In Progress bug named by a commit, and a critic-verdicts.md holding non-UTF-8 bytes; run `sprint.py close --dry-run` at 62af4d6d and at 3cf06672 and compare the STOP status rows.

## Proposed Fix

When the seal bar cannot be read, name the unit's status (unknown is not approved, LC-006); give a bug that already has an APPROVE followed by a REJECT the rejecting reviewer's round as its remedy; pin the approved-CR exemption and both remedy texts.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose verdict ledger is unreadable and whose batch holds an unreviewed In Progress bug named by a commit, when `sprint.py close --dry-run` runs, then a STOP status row names that bug. Fails on: 3cf06672, which swallows the read error and names nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UndeliveredBlockerTests::test_an_unreadable_ledger_still_names_an_unreviewed_bug

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
