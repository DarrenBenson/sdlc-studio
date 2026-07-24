# HO-0026: Every remaining backlog story carries authored acceptance criteria and an executable Verify line, so the delivery sprint that empties the backlog can be planned against a groomed backlog rather than a guess

> **Date:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYA8CF (started 2026-07-24T14:28:11Z)
> **Outcome:** stopped
> **Goal:** design
> **Batch source:** run-state.json

## Where to pick up

18 of 18 unit(s) remain (17 suit copilot-assisted completion, 1 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 240 min, units 18 unit(s)
- **Spent:** 75.8 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~1,501,482 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (18)

### US0345 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests::test_no_shipped_file_references_the_old_module_names (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests::test_gate_and_sprint_call_sites_resolve_and_behave_identically (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameTests::test_the_public_audit_command_is_unchanged (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/audit.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/audit_check.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0345-rename-audit-py-and-audit-check-py-update.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0346 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameDocsTests::test_the_suites_are_renamed_and_green (pytest)
- **ac:** `AC2` - grep readiness.py .claude/skills/sdlc-studio/reference-scripts.md (grep)
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-scripts.md` - declared Affects
- **file:** `CHANGELOG.md` - declared Affects
- **file:** `sdlc-studio/stories/US0346-update-tests-reference-scripts-md-and-changelog.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0347 (story, Ready) - copilot-tail

- **ac:** `AC1` - shell python3 tools/check_versions.py --strict | grep -q '5\.0\.0' (shell)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/../../../../tools/tests/test_check_versions.py::StrictBumpTests::test_a_single_stale_file_is_named (pytest)
- **file:** `.claude/skills/sdlc-studio/SKILL.md` - declared Affects
- **file:** `CHANGELOG.md` - declared Affects
- **file:** `tools/check_versions.py` - declared Affects
- **file:** `sdlc-studio/stories/US0347-version-bump-to-5-0-0-across-authoritative.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0348 (story, Ready) - copilot-tail

- **ac:** `AC1` - shell python3 .claude/skills/sdlc-studio/scripts/gate.py --release (shell)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_the_section_is_cut_from_fragments_and_unreleased_is_emptied (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_a_tag_is_refused_when_the_green_was_measured_elsewhere (pytest)
- **file:** `CHANGELOG.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0348-gate-release-green-on-a-fresh-dry-run.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0349 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_no_file_appears_in_two_lanes (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_the_partition_changes_nothing_else_in_the_plan (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_an_undeclared_unit_is_named_not_placed (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0349-sprint-plan-emits-a-report-only-lane-partition.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0350 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneExportTests::test_each_lane_round_trips_through_the_worklist_reader (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneExportTests::test_the_exports_themselves_are_pairwise_disjoint (pytest)
- **ac:** `AC3` - grep undeclared .claude/skills/sdlc-studio/reference-sprint.md (grep)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `sdlc-studio/stories/US0350-export-each-lane-as-a-per-team-worklist.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0351 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::PrimaryPathTests::test_the_primary_path_drives_a_batch_to_close (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::PrimaryPathTests::test_a_failing_unit_stops_the_loop_and_is_named (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::PrimaryPathTests::test_the_suite_kills_a_loop_control_mutant (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_autosprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/autosprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0351-test-autosprint-py-exercising-the-primary-path.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:medium

### US0352 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_xrepo.py::PrimaryPathTests::test_the_primary_path_completes_across_two_trees (pytest)
- **ac:** `AC2` - shell grep -q 'currently have no direct test' sdlc-studio/tsd.md && exit 1 || exit 0 (shell)
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_xrepo.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/xrepo.py` - declared Affects
- **file:** `sdlc-studio/tsd.md` - declared Affects
- **file:** `sdlc-studio/stories/US0352-test-xrepo-py-primary-path-and-update-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:medium

### US0355 (story, Ready) - copilot-tail

- **ac:** `AC1` - grep '## Choosing the Primary' .claude/skills/sdlc-studio/reference-persona.md (grep)
- **ac:** `AC2` - shell python3 .claude/skills/sdlc-studio/scripts/validate.py check --root . 2>&1 | grep -q 'RFC0017.*accepted-open-decision' && exit 1 || exit 0 (shell)
- **file:** `.claude/skills/sdlc-studio/reference-persona.md` - declared Affects
- **file:** `sdlc-studio/decisions.md` - declared Affects
- **file:** `sdlc-studio/stories/US0355-decide-and-document-the-primary-selection-method-in.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0356 (story, Ready) - copilot-tail

- **ac:** `AC1` - shell grep -q 'Decision-Override' sdlc-studio/rfcs/RFC0017*.md && exit 1 || exit 0 (shell)
- **file:** `sdlc-studio/rfcs/RFC0017-agent-persona-selection.md` - declared Affects
- **file:** `sdlc-studio/decisions.md` - declared Affects
- **file:** `sdlc-studio/stories/US0356-remove-the-decision-override-from-rfc0017-once-d1.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0359 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::OverAppetiteTests::test_both_the_standing_and_accepted_appetite_are_recorded (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::OverAppetiteTests::test_the_plan_does_not_read_as_fitting (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::OverAppetiteTests::test_a_within_appetite_run_records_no_overage (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0359-run-state-records-an-over-appetite-batch-keeping.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0360 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OverAppetiteReportTests::test_the_close_states_the_overage_not_the_raised_ceiling (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::OverAppetiteReportTests::test_the_retro_records_the_overage_and_its_acceptance (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0360-the-close-and-retro-report-the-over-commitment.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0367 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::ClaimAnchoredTests::test_a_stale_count_fails_and_is_named (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::ClaimAnchoredTests::test_a_correct_count_passes_on_the_value_not_the_stamp (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/doc_freshness.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py` - declared Affects
- **file:** `sdlc-studio/stories/US0367-anchor-the-cr0302-freshness-guard-to-the-claim.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0368 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestRelevantSetTests::test_every_path_a_shipped_test_reads_is_in_the_set (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestRelevantSetTests::test_a_doc_a_test_reads_defeats_the_docs_only_skip (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0368-extend-the-cr0340-test-relevant-set-to-every.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0369 (story, Ready) - copilot-tail

- **ac:** `AC1` - grep 'Revision History' sdlc-studio/trd.md (grep)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::DocDriftResidualTests::test_every_residual_is_corrected_or_declined_with_a_reason (pytest)
- **file:** `sdlc-studio/trd.md` - declared Affects
- **file:** `sdlc-studio/stories/US0369-correct-the-cr0304-trd-sentence-and-disposition-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0370 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AcDefectTests::test_an_amended_criterion_is_recorded_as_an_ac_defect (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-verify.md` - declared Affects
- **file:** `sdlc-studio/stories/US0370-record-the-ac-correction-cases-as-ac-defects.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0413 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateCheckTests::test_a_near_duplicate_is_reported_with_the_existing_id (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateCheckTests::test_an_ordinary_new_title_is_not_flagged (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateCheckTests::test_a_closed_artefact_still_counts_as_a_duplicate (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `sdlc-studio/stories/US0413-artifact-py-new-warns-on-a-near-duplicate.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0414 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateStrictTests::test_advisory_by_default_mints_and_reports (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateStrictTests::test_strict_refuses_and_writes_nothing (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `sdlc-studio/stories/US0414-the-duplicate-check-is-advisory-by-default-and.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Generated at the run close (`handoff generate`) |
