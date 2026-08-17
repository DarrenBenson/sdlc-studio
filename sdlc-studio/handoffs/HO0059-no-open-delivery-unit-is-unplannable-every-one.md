# HO-0059: No open delivery unit is unplannable: every one carries authored acceptance criteria whose Verify line executes and fails RED against the absent behaviour, rather than restating the finding

> **Date:** 2026-08-17
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M05A5M (started 2026-08-16T13:05:42Z)
> **Outcome:** goal-reached
> **Goal:** design
> **Batch source:** run-state.json

## Where to pick up

12 of 12 unit(s) remain (7 suit copilot-assisted completion, 5 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 661.7 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~1,265,726 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (12)

### BG0490 (bug, Open) - judgement

- **ac:** `AC1` - pytest tools/tests/test_check_links.py::AuditProfilePathsTests::test_the_one_real_row_resolves (pytest)
- **ac:** `AC2` - pytest tools/tests/test_check_links.py::AuditProfilePathsTests::test_invocation_and_prose_shapes_are_not_skipped (pytest)
- **ac:** `AC3` - pytest tools/tests/test_check_versions.py::DocstringMatchesTheCodeTests::test_the_never_by_grep_claim_is_true (pytest)
- **file:** `sdlc-studio/bugs` - declared Affects
- **file:** `tools/check_links.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/code.md` - declared Affects
- **file:** `tools/check_versions.py` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `tools/tests/test_check_links.py` - declared Affects
- **file:** `tools/tests/test_check_versions.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0490-four-bug-repairs-are-fixed-with-half-their.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### BG0493 (bug, Open) - copilot-tail

- **ac:** `AC1` - pytest tools/tests/test_conftest_guard.py::TheGuardSeesTheCallNotTheDocstringTests::test_deleting_the_call_reddens_ac1 (pytest)
- **ac:** `AC2` - pytest tools/tests/test_precommit_lane_order.py::TheSliceReadsTheLaneTests::test_the_slice_is_not_a_comment_block (pytest)
- **ac:** `AC3` - pytest tools/tests/test_best_practice_rules.py::AnAbsentPracticeFileRefusesTests::test_a_missing_file_is_not_an_exemption (pytest)
- **ac:** `AC4` - pytest tools/tests/test_best_practice_rules.py::AnAbsentPracticeFileRefusesTests::test_the_checker_is_wired_into_a_lane (pytest)
- **file:** `tools/tests/conftest.py` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `tools/best_practice_rules.py` - declared Affects
- **file:** `tools/tests/test_best_practice_rules.py` - declared Affects
- **file:** `tools/tests/test_conftest_guard.py` - declared Affects
- **file:** `tools/tests/test_precommit_lane_order.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0493-four-more-verifiers-pass-on-a-delivery-that.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0625 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_the_doctrine_states_the_per_finding_rule (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_a_finding_with_no_ruling_is_refused (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_two_findings_keep_their_own_rulings (pytest)
- **file:** `.claude/skills/sdlc-studio/reference-doctrine.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0625-the-doctrine-states-the-rule-and-the-stop.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0626 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_close_refuses_and_names_the_unit (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_stop_refuses_on_the_same_condition (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_the_refusal_names_where_the_findings_went (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_a_terminal_batch_still_closes (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0626-sprint-close-and-sprint-stop-refuse-while-any.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0627 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_done (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_stop_ship_ruling_discharges_the_reject (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_id_naming_no_artefact_is_refused (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0627-closing-a-story-over-a-recorded-reject-requires.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0628 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_the_story_names_the_filed_artefact (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_ruling_is_named_with_its_author (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_an_ordinary_close_writes_no_discharge_line (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0628-a-story-closed-this-way-names-the-bug.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0646 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::ContractReporterTests::test_the_demands_come_from_executing_the_guard (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::ContractReporterTests::test_a_changed_guard_changes_the_report (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::ContractReporterTests::test_no_guard_and_no_answer_are_different (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_contract_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0646-a-shared-contract-reporter-derives-a-verb-s.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0647 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VocabularyFromTheConstantTests::test_the_refusal_renders_the_enforcing_constant (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VocabularyFromTheConstantTests::test_a_new_member_appears_without_an_edit (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VocabularyFromTheConstantTests::test_uncovered_vocabularies_are_named (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/stories/US0647-the-vocabularies-that-gate-a-caller-print-from.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0648 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::TheFourCostliestVerbsTests::test_all_four_answer_the_reporter (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::TheFourCostliestVerbsTests::test_the_shape_is_reported_not_only_the_field (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::TheFourCostliestVerbsTests::test_the_reported_shape_round_trips (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_contract_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `sdlc-studio/stories/US0648-the-four-verbs-whose-refusals-cost-most-in.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0649 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest tools/tests/test_contract_coverage.py::CoverageLaneTests::test_the_lane_reports_a_fraction (pytest)
- **ac:** `AC2` - pytest tools/tests/test_contract_coverage.py::CoverageLaneTests::test_every_unreachable_verb_is_named (pytest)
- **ac:** `AC3` - pytest tools/tests/test_contract_coverage.py::CoverageLaneTests::test_the_lane_does_not_fail_the_commit (pytest)
- **file:** `tools/check_contract_coverage.py` - declared Affects
- **file:** `tools/tests/test_contract_coverage.py` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `sdlc-studio/stories/US0649-a-lint-lane-counts-contract-reporter-coverage-and.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:medium

### US0650 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest tools/tests/test_check_spec_claims.py::ContractsAreNotRestatedTests::test_no_help_page_restates_a_derived_contract (pytest)
- **ac:** `AC2` - pytest tools/tests/test_check_spec_claims.py::ContractsAreNotRestatedTests::test_the_pointer_names_a_runnable_command (pytest)
- **ac:** `AC3` - pytest tools/tests/test_check_spec_claims.py::ContractsAreNotRestatedTests::test_an_exemption_is_named_and_reasoned (pytest)
- **file:** `.claude/skills/sdlc-studio/reference-scripts.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/` - declared Affects
- **file:** `tools/tests/test_check_spec_claims.py` - declared Affects
- **file:** `tools/check_spec_claims.py` - declared Affects
- **file:** `sdlc-studio/stories/US0650-help-and-reference-scripts-point-at-the-contract.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0651 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::RefusalsAreCountedTests::test_refusals_are_counted_per_run (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::RefusalsAreCountedTests::test_the_retro_renders_the_count (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::RefusalsAreCountedTests::test_zero_is_stated_rather_than_omitted (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::RefusalsAreRecordedTests::test_a_refusing_verb_records_the_refusal (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0651-the-refusals-a-run-hits-are-counted-so.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Generated at the run close (`handoff generate`) |
