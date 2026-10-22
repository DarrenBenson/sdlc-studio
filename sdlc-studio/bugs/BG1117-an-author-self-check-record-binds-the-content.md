# BG1117: An author self-check record binds the content of the unit's whole Affects, so a later unit's commit to a shared file makes it stale and, under block, refuses the earlier unit's brief

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py, changelog.d/BG1117.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Run three, 2026-10-22: self_check_gap on main after e58c7bcd; US1088 and US1089 re-recorded with the same claims and mutants, the author field naming the commit that moved each digest.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T07:27:06Z

## Summary

US1088's record stores a digest of the content of every file in the unit's Affects, and US1089's brief gate admits a unit only when that digest matches the content now. In run three, US1089 changed critic.py after US1088's record was taken, and US1090 changed AGENTS.md before US1089 reached main. Both records read stale on main although neither unit's own change had moved: `self_check_gap` reported 'stale: its digest eb8be939da1f2dbb is of an earlier diff' for US1088 and the same for US1089. Under this repository's `review.author_self_check: block`, their briefs would be refused until the authors re-recorded unchanged evidence. Every batch whose units share a file (the breakdown's shared-file clusters) meets this whenever a unit is reviewed after a later unit lands.

## Steps to Reproduce

Record a self-check for unit A, commit a change from unit B to a file both declare, then run `critic.py brief --unit A --seat qa` under block: refused as stale.

## Proposed Fix

Bind the record to the unit's own change rather than the whole files: digest the unit's diff against the run's base restricted to its Affects, minus the hunks of units that landed after it, or record a digest per file and judge staleness only on the files whose content moved since the record by a commit naming this unit. Whichever is chosen, a later unit's commit to a shared file must not stale an earlier unit's record, and the author's own further edit must.

## Acceptance Criteria

- [ ] **AC1** Given unit A's recorded self-check and a later commit by unit B to a file both declare, when A is briefed under block, then the brief is admitted; given an edit by A's own author to that file after the record, the brief is refused as stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py::LaterUnitTests::test_a_later_units_commit_does_not_stale_the_record

## Impact

Re-recording unchanged evidence becomes routine, which teaches authors to re-record without re-checking, the habit the gate exists to stop.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
