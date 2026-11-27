# BG1777: US1344 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/US1344.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-27T18:58:01Z

## Summary

US1344 was rejected at round 2, the review cap, by agent-ae72813b850b44cbd (qa), so it was carried as a known issue rather than reviewed again. Filed at Low rather than the carry's default Medium: the release bar (`review.blocking_priority`) bars Medium, and Low is the most severe level it allows. The findings still open: BLOCKING: [new] the repair writes the Unit cell as `sdlc_md.norm_id(unit)` (critic.py:6617, docstring critic.py:6588), which is the comparison key and drops the dash a schema v3 id is spelt with. On a fixture at `schema_version: 3`, the version templates/config.yaml:9 seeds every new project with, `approach record --unit US-01ABCDEF`, typed exactly as its file spells it, wrote `/ US01ABCDEF / 1 / GO /`, and grep finds no `US-01ABCDEF` in the ledger, while `sdlc_md.display_id` returns `US-01ABCDEF` for both `US-01ABCDEF` and `us01abcdef`. This is BG0825's defect again (Fixed, Medium: "ids print in their file's spelling, never as the hyphenless comparison key", and the norm\_id docstring says "A KEY, never a display ... print an id through display\_id"). critic.py's other writers keep to it (critic.py:242, 2342, 4880). At round one the typed spelling was kept, so the repair loses the right spelling for every v3 row, and the fixture's own `US-0007` is now written `US0007`. Matching still goes through `norm_id`, so the rounds and `approach_agreed` are unaffected. Write `sdlc_md.display_id(repo_root, unit)` and assert that US-0007's cell reads `US-0007`; [pre-existing] a `.config.yaml` that does not parse still falls back to the built-in defaults with a warning (config.py:92, not in this diff, no open bug found). The repair keeps that on purpose (critic.py:6474), so the step reads as off and every record is refused naming `min_points` 0; RULINGS: "the per-unit round is pinned by no test" CLOSED: the same mutant, re-applied, is killed by test\_a\_verdict\_is\_bound\_to\_the\_note\_digest\_round\_by\_round at US0004's round. "the row `record_solution_review` returns, and that `approach record` prints as its own" CLOSED: moving the read-back out of the lock is killed by test\_the\_row\_printed\_is\_the\_one\_this\_call\_wrote, which prints round 2 and the peer's digest. "that the lock is taken at all is unpinned" CLOSED: `contextlib.nullcontext()` in place of the lock is killed by both test\_two\_records\_at\_once\_take\_two\_rounds (the ledger is written while the test holds the lock) and test\_the\_row\_printed\_is\_the\_one\_this\_call\_wrote (the peer never fires). "the OSError catch in `cmd_approach_record`" CLOSED: narrowing it to ValueError is killed twice, by a traceback and by exit 1. "the `solution_review_settings` docstring" CLOSED: probed through the CLI, `review: 5`, `review: [1, 2]`, `solution_review: []`, `off` and `true` are each refused naming the block, and a null or `{}` block reads as the defaults, as the docstring now says. "Points are read with `raw.isdigit()`" CLOSED: `sdlc_md.read_points` refuses the superscript two as no Points. A Points value off the scale, such as 4, is also read as no Points, which matches the shared reader. "the Unit and Note cells keep what was typed" MOVED: the Note half is closed (a note outside the project is written as `../note.md` relative to the root, whatever the working directory), but the Unit half became the v3 finding above. The pre-existing config fallback is unchanged. Re-run at 517e83e14 in a detached worktree: test\_solution\_review\_record.py, test\_lean\_config\_keys\_read, test\_lean\_config\_code\_defaults, test\_config and the NON\_CEREMONY\_VERBS test give 50 passed, verify\_ac dry-run gives 4 of 4 pass, `docgen.py surface --check` reports no drift, and reference-config.md is 724 lines. Claim inventory for the repair: the reference-config.md row, the reference-scripts-review.md paragraph, both docstrings, the fragment and the commit body are TRUE of the code. The one remark is that the row's "a block that is not a mapping" refusal does not cover a null block, which reads as the defaults (UNVERIFIABLE as a reader would take it, not a finding). docs/known-issues.md and docs/release-notes-v6.5.0.md are still changed only by multi-id paperwork commits, so US1344's Affects is right.

## Steps to Reproduce

1. Read the round 2 REJECT of US1344 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1344 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repair writes the Unit cell as `sdlc_md.norm_id(unit)` (critic.py:6617, docstring critic.py:6588), which is the comparison key and drops the dash a schema v3 id is spelt with. On a fixture at `schema_version: 3`, the version templates/config.yaml:9 seeds every new project with, `approach record --unit US-01ABCDEF`, typed exactly as its file spells it, wrote `/ US01ABCDEF / 1 / GO /`, and grep finds no `US-01ABCDEF` in the ledger, while `sdlc_md.display_id` returns `US-01ABCDEF` for both `US-01ABCDEF` and `us01abcdef`. This is BG0825's defect again (Fixed, Medium: "ids print in their file's spelling, never as the hyphenless comparison key", and the norm\_id docstring says "A KEY, never a display ... print an id through display\_id"). critic.py's other writers keep to it (critic.py:242, 2342, 4880). At round one the typed spelling was kept, so the repair loses the right spelling for every v3 row, and the fixture's own `US-0007` is now written `US0007`. Matching still goes through `norm_id`, so the rounds and `approach_agreed` are unaffected. Write `sdlc_md.display_id(repo_root, unit)` and assert that US-0007's cell reads `US-0007`
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] a `.config.yaml` that does not parse still falls back to the built-in defaults with a warning (config.py:92, not in this diff, no open bug found). The repair keeps that on purpose (critic.py:6474), so the step reads as off and every record is refused naming `min_points` 0
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** US1344 AC1 still passes: the setting decides which units take the step
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_the_setting_decides_which_units_take_the_step
- [ ] **AC4** US1344 AC2 still passes: a verdict is recorded against the note's digest, round by round
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_a_verdict_is_bound_to_the_note_digest_round_by_round
- [ ] **AC5** US1344 AC3 still passes: a verdict that cannot stand is refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_a_verdict_that_cannot_stand_is_refused
- [ ] **AC6** US1344 AC4 still passes: the step ships off, and the reference says so
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_the_step_ships_off_and_the_reference_says_so

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Filed |
