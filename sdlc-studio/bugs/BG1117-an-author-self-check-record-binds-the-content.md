# BG1117: An author self-check record binds the content of the unit's whole Affects, so a later unit's commit to a shared file makes it stale and, under block, refuses the earlier unit's brief

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py, changelog.d/BG1117.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md, sdlc-studio/reviews/author-self-checks.md
> **Evidence:** Run three, 2026-10-22: self_check_gap on main after e58c7bcd; US1088 and US1089 re-recorded with the same claims and mutants, the author field naming the commit that moved each digest.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T07:27:06Z

## Summary

US1088's record stores a digest of the content of every file in the unit's Affects, and US1089's brief gate admits a unit only when that digest matches the content now. In run three, US1089 changed critic.py after US1088's record was taken, and US1090 changed AGENTS.md before US1089 reached main. Both records read stale on main although neither unit's own change had moved: `self_check_gap` reported 'stale: its digest eb8be939da1f2dbb is of an earlier diff' for US1088 and the same for US1089. Under this repository's `review.author_self_check: block`, their briefs would be refused until the authors re-recorded unchanged evidence. Every batch whose units share a file (the breakdown's shared-file clusters) meets this whenever a unit is reviewed after a later unit lands.

A second cause, from US1089's QA review (APPROVE, round 1, 2026-10-22): `record_self_check` digests the Affects before appending its own row (critic.py:2789-2792), so a unit whose Affects declares the self-check log, or `sdlc-studio/reviews`, reads stale after every record, re-records included; and any `critic.py record` stales a unit declaring `critic-verdicts.md`. BG1113 declares it, so under block BG1113 could be briefed only if no verdict were recorded between its record and its brief, and never for a second seat or round.

## Steps to Reproduce

Record a self-check for unit A, commit a change from unit B to a file both declare, then run `critic.py brief --unit A --seat qa` under block: refused as stale.

## Proposed Fix

Bind the record to the unit's own change rather than the whole files: digest the unit's diff against the run's base restricted to its Affects, minus the hunks of units that landed after it, or record a digest per file and judge staleness only on the files whose content moved since the record by a commit naming this unit. Whichever is chosen, a later unit's commit to a shared file must not stale an earlier unit's record, and the author's own further edit must.

## Acceptance Criteria

- [ ] **AC1** Given unit A's recorded self-check and a later commit by unit B to a file both declare, when A is briefed under block, then the brief is admitted; given an edit by A's own author to that file after the record, the brief is refused as stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py::LaterUnitTests::test_a_later_units_commit_does_not_stale_the_record
- [ ] **AC2** Given a unit whose Affects declares the review tooling's own logs (sdlc-studio/reviews/author-self-checks.md, sdlc-studio/reviews/critic-verdicts.md, or the directory holding them), when its self-check is recorded and then another unit's verdict is recorded, then its brief under block is admitted: the record's own append and a `critic.py record` do not move the digest
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py::LaterUnitTests::test_the_review_tools_own_writes_do_not_stale_the_record

## Impact

Re-recording unchanged evidence becomes routine, which teaches authors to re-record without re-checking, the habit the gate exists to stop.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
| 2026-10-22 | sdlc | AC2 from US1089's QA review: the review tooling's own writes stale a record whose Affects declares its logs; joins run three before BG1113 |
| 2026-10-22 | sdlc | Affects gains reference-review.md, help/review.md and the self-check log's header: each says the digest binds whole files, which this fix makes false (its builder's finding) |
