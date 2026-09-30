# BG0845: migrate's conformance cutoff on a v4.1 project exempts the 98 units after the project's own adoption point, because a verdict row with no Author column never reads as independent

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py, changelog.d/BG0845.md, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py
> **Evidence:** docs/upgrade-rehearsal-v6.md (US0962), v4.1 row; migrate.py _conformance_cutoff; critic.py is_independent / is_pre_gate; the v4.1 copy's critic-verdicts.md header
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T19:42:58Z

## Summary

US0962 rehearsal (a v4.1 project of 687 stories, skill 6.0.0-rc.1 at 5e45cbf9): the project already sets `conformance.adopt_after: US0682`. The conformance lane fails all 98 stories above it (US0683 to US0784), most missing 'critiqued (independent APPROVE verdict)', and migrate proposes 'add `conformance.adopt_after: US0784`', the project's highest story, which exempts every story it has. 49 of those 98 units hold an APPROVE row in `reviews/critic-verdicts.md`, written in the v4.1 ledger shape (Unit | Verdict | Reviewer | Date | Issues) with no Author column: `critic.is_independent` needs an author and `is_pre_gate` needs the `pre-gate` sentinel, which no shipped command writes. The report calls the 98 'pre-adoption history' although they post-date the project's own cutoff, says 'add' for a key the project already sets, and does not separate units with an author-less APPROVE row from units with no review at all.

## Steps to Reproduce

On a fixture with `conformance.adopt_after: US0002`, Done stories US0003 and US0004 with a Verified AC, and a critic-verdicts.md in the five-column shape with an APPROVE row for US0003 only, run `migrate.py --format json`: the conformance item says 'add `conformance.adopt_after: US0004`' and treats both units alike.

## Proposed Fix

Report only, no new check (LC-008). In `_conformance_cutoff`: when a cutoff is already set, name it and say the line raises it (from US0682 to US0784), never 'add'; and split the failing units into those whose only unmet half is an APPROVE row with no recorded author (ledger shape, answerable by recording the author or a reviewed pre-gate stamp) and the rest, each with its count.

## Acceptance Criteria

- [ ] **AC1** Given a fixture that already sets `conformance.adopt_after` below its failing units, when `migrate.py --format json` runs, then the conformance item names the existing cutoff and the proposed one as a raise from it, and never tells the user to add the key. Fails on: today's 'add `conformance.adopt_after: ...`' wording
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py::MigrateCutoffTests::test_an_existing_cutoff_is_named_as_raised_not_added
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given a fixture whose failing units include one with an APPROVE row in the five-column ledger (no Author) and one with no verdict row, then the conformance item counts them apart and names which is which. Fails on: one undifferentiated list
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py::MigrateCutoffTests::test_approve_rows_with_no_author_are_counted_apart
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
