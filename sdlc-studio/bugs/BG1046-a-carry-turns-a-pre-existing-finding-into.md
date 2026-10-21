# BG1046: A carry turns a pre-existing finding into a criterion the carried bug can never meet

> **Status:** Superseded
> **Superseded by:** BG1079
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG1045, filed by the carry of US1006's round-2 REJECT on 2026-10-14: its AC2 restated BG1043's open finding; groomed out by hand (BG1045's revision history).
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T11:04:38Z

## Summary

`critic.carried_criteria` writes one criterion per item of the carrying REJECT, 'The round N REJECT finding no longer holds: <item>', for every item `split_items` returns, including items tagged [pre-existing]. A pre-existing item is already true of the tree, usually held by an open Bug or CR it names, and AGENTS.md says it does not hold a review; `reconcile.blocking_findings` skips such items. The carried bug then holds a criterion its own fix cannot meet (BG1045 was filed with 'no longer holds: [pre-existing] BG1043 ...', a different open bug's finding) and had to be groomed by hand before the run could take it.

## Steps to Reproduce

Record a REJECT at the review cap on a unit in the open run whose ISSUES carry one [new] and one [pre-existing] item: the bug `carry_at_cap` files holds a criterion for each.

## Proposed Fix

Write criteria only for the items that hold the gate, by the same reading `reconcile.blocking_findings` makes (skip an item whose own origin tag is pre-existing or that says non-blocking), and list the pre-existing items in the summary as context.

## Acceptance Criteria

- [ ] **AC1** Given a REJECT at the cap whose issues hold a [new] item and a [pre-existing] item, when it is recorded on a unit in the open run, then the carried bug holds a criterion for the [new] item only and names the [pre-existing] one in its summary.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): superseded by BG1079: duplicate of BG1079, which also covers info items and has an executable Verify |
