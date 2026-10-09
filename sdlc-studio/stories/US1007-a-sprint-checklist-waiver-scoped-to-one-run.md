# US1007: A sprint-checklist waiver scoped to one run covers that run's close and no other

> **Status:** Draft
> **Delivers:** CR0614
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_run_scope.py, changelog.d/US1007.md
> **Epic:** EP0279
> **Points:** 3
> **Depends on:** BG1008, BG1012, BG1013
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer closing a run whose checklist row is wrong for this run alone
**I want** to waive that row for this run by naming the run in the waiver
**So that** the row is enforced again on the next run instead of being switched off for good

## Acceptance Criteria

- **AC1:** Given run RUN-AAAA1111 whose closing-review row is open on BG0460 and US0002 and a waiver recorded through `decisions.py waive --subject rule:sprint-checklist:closing-review:RUN-AAAA1111`, when `sprint_report.py checklist --format json` runs, then the row reads waived, names that waiver's id, and its detail still names both open units.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_run_scope.py::RunScopedChecklistWaiverTests::test_a_run_scoped_waiver_answers_its_own_run_and_still_names_the_units
- **AC2:** Given that same waiver and a run record RUN-BBBB2222 with the same outstanding row, when the checklist runs, then the row stays outstanding and names no waiver.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_run_scope.py::RunScopedChecklistWaiverTests::test_a_run_scoped_waiver_does_not_answer_another_run
- **AC3:** Given a clone that holds RUN-AAAA1111 only as the tracked record `sdlc-studio/reports/runs/RUN-AAAA1111.json`, with no `.local` state, and the run-scoped waiver, when the checklist runs, then the row reads waived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_run_scope.py::RunScopedChecklistWaiverTests::test_the_run_is_found_from_the_tracked_record_alone
- **AC4:** Given the well-formed subject `rule:sprint-checklist:goal-judged:RUN-TYPO1234`, which names no live, archived or tracked run, when `decisions.py waive` runs, then it exits 2 saying the tail names no run, and writes no decision row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_run_scope.py::RunScopedChecklistWaiverTests::test_a_run_tail_that_names_no_run_is_refused
- **AC5:** Given a run whose checklist leaves goal-judged outstanding, when the remedy the checklist footer prints is run exactly as printed through `decisions.py waive`, then it records a waiver scoped to that run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_run_scope.py::RunScopedChecklistWaiverTests::test_the_printed_remedy_records_a_run_scoped_waiver

## Notes

- Release: 6.2 (D0355 breakdown G5, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: `_resolve_item` looks the waiver up under the unscoped subject only, so the run tail is recorded and never read; or the waived row drops the detail that names what it waived.
- AC2 must fail on: the scoped lookup matches any waiver whose subject starts with the item, ignoring which run it names.
- AC3 must fail on: the tail is matched against `.local/run-state.json` and its archive only, so the waiver covers its run on the machine that closed it and nowhere else.
- AC4 must fail on: the tail is checked by shape only, so a mistyped run id records clean and covers nothing.
- AC5 must fail on: the printed remedy keeps the bare `rule:sprint-checklist:<item>` form, or a placeholder the command refuses.
- Grammar: `rule:sprint-checklist:<item>[:<run id>]`. The item half is validated first, as today, so `test_a_waiver_naming_NO_REAL_ITEM_is_refused` stays green. The run half is parsed with run_state's own grammar (`_RUN_ID_IN_NAME`, run_state.py:1555, as a full match), not `sdlc_md.is_v3_id`, which accepts `run-01m4apnq` and rejects the suite's fixture id `RUN-TEST01`. It is compared through `sdlc_md.norm_id`, because `_norm_subject` stores the subject lower-cased.
- Record time: the tail must name a run that exists, live, archived or tracked (`run_state.tracked_path`). Read time: it is matched against the run the checklist resolves, which BG1012 makes live, then tracked, then archived. When no run resolves, a run-scoped waiver covers nothing and the row stays outstanding.
- Lookup order is run-scoped, then unscoped, and the row names whichever answered it. An unscoped waiver behaves exactly as today. US-4 adds the warning that says so.
- BG1013 fixes the three printed remedies first (sprint.py:5661 in the close step, sprint.py:7202 in the close pre-flight, sprint_report.py:2428 in the footer). This story makes each print the run-scoped form for the run in hand, with the --authorised-by placeholder BG1013 adds. It also corrects the footer's stale 'The close refuses until each is answered' (panel Q6), since the close records an unanswered item as a known issue (sprint.py:9223).
- Fixture: a retro, a run record and a critic ledger in which US0001 is approved and BG0460 and US0002 are not, so closing-review is outstanding and its detail names the two open units. `_resolve_item` already keeps `detail` on a WAIVED row (sprint_report.py:2253); AC1 pins it, because that detail is what stops a run-scoped waiver written about BG0460 from hiding an unreviewed US0002.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G5 after the refine panel's review |
