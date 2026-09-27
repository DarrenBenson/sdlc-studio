# BG0783: Review rounds are write-dead after US0918, so the ceiling and repair-regression readers of run-state rounds read nothing

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_dead_round_readers.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0783.md, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, sdlc-studio/bugs/BG0261-the-state-anchor-and-the-goal-verdict-both.md, sdlc-studio/bugs/BG0366-overhead-ratio-computes-delivery-by-subtraction-so-unmeasured.md, sdlc-studio/stories/US0261-count-review-rounds-on-the-run-state-and.md, sdlc-studio/stories/US0262-detect-a-repair-regression-a-finding-in-code.md, sdlc-studio/stories/US0263-on-a-repair-regression-escalate-to-a-revert.md, sdlc-studio/stories/US0264-record-cumulative-review-token-cost-per-round-and.md, sdlc-studio/stories/US0534-a-recorded-review-round-carries-a-duration-and.md, sdlc-studio/stories/US0535-the-overhead-ratio-consumes-recorded-review-durations-and.md
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T11:37:33Z

## Summary

US0918 retired critic.py sprint-review, the only writer of `run_state` review rounds (`record_sprint_review).` The ceiling guard, `next_round_offer` and repair-regression machinery that read run-state review rounds now read an empty record. The per-unit delivery cap reads the verdict ledger (`critic.delivery_rounds)` and is unaffected. Found by US0918's builder.

## Steps to Reproduce

grep `record_review_round` callers after US0918: none in production.

## Proposed Fix

Delete the run-state review-round readers and their config, or re-point them at `critic.delivery_rounds`; one test that no production reader of run-state rounds remains.

## Acceptance Criteria

- [ ] **AC1** Given an open run, when the goal verdict is recorded with a note that states 'two rounds of review converged', then it is recorded, and the record carries no round count read from run-state review rounds. Fails on: HEAD's `record_goal_verdict`, which refuses the note against `len(review_rounds)`, always 0 since US0918 (probed: 'the ledger carries 0'), and stamps `rounds: 0` on every goal verdict
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_dead_round_readers.py::DeadRoundReaderTests::test_a_goal_verdict_note_naming_rounds_is_recorded
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given the production scripts, then no module names `REVIEW_ROUNDS`, `CEILING_OVERRIDES`, `record_review_round`, `review_round_count`, `review_round_guard`, `next_round_offer`, `round_cost_report`, `classify_finding` or `escalation_for`. Fails on: deleting the writer's tests while a reader survives, as US0918 left eight
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_dead_round_readers.py::DeadRoundReaderTests::test_no_run_state_round_reader_survives
  - **Verified:** yes (2026-09-27)
- [ ] **AC3** Given a unit with two recorded rounds in the open run, when a third verdict is recorded, then it is refused. Fails on: deleting `review_ceiling` with the dead guard beside it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::ReviewRoundTests::test_a_third_round_is_refused
  - **Verified:** yes (2026-09-27)

## Notes

- Sprint 6 engineering: delete, do not re-point. No production caller reaches `review_round_guard`, `next_round_offer`, `round_cost_report`, `classify_finding`, `escalation_for`, `record_escalation`, `defer_escalation` or `record_ceiling_override`, and no CLI verb does. Re-pointing at `critic.delivery_rounds` would feed per-unit rounds to readers built for whole-sprint close rounds. Also removes `sprint_report._component_review`'s run-state read (the overhead component then reads NOT CAPTURED, as it already does in practice), the checklist's `review_rounds` context and `_verdict_entries`' second loop, and doc_freshness's round-count drift. Keep `review_ceiling` (the live per-unit cap). Before retiring any test, mutate the live rule beside it and confirm a surviving test kills it (RETRO0125 Stop, LC-002). Land before US0959.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: delete the readers; the goal-verdict refusal against the dead ledger is the live bite |
