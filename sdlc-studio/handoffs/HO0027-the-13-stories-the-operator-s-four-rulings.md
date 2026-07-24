# HO-0027: The 13 stories the operator's four rulings created carry authored acceptance criteria and an executable Verify line, so Sprint 3b can be planned against a fully groomed backlog and the PARTIAL verdict Sprint 3a returned is closed out

> **Date:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYAG6X (started 2026-07-24T16:47:50Z)
> **Outcome:** goal-reached
> **Goal:** design
> **Batch source:** run-state.json

## Where to pick up

13 of 13 unit(s) remain (11 suit copilot-assisted completion, 2 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 8.8 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~1,501,482 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (13)

### US0419 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyTests::test_the_plan_names_the_tsd_risk_areas_the_batch_touches (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyTests::test_no_risk_area_is_stated_explicitly_not_left_blank (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyTests::test_a_newly_added_risk_area_appears_without_a_code_change (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0419-the-planner-reads-the-tsd-and-names-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0420 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ProofRequirementTests::test_each_unit_carries_the_proof_its_band_requires (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ProofRequirementTests::test_demanded_coverage_the_batch_omits_is_flagged (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ProofRequirementTests::test_the_close_reports_a_claimed_proof_the_evidence_does_not_show (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0420-each-unit-carries-the-proof-its-risk-band.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0421 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleTsdTests::test_a_stale_tsd_is_reported_before_it_is_used (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleTsdTests::test_a_current_tsd_passes_on_comparison_not_on_a_marker (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/doc_freshness.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0421-the-review-reports-a-stale-tsd-rather-than.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0422 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::StrategyScopedTests::test_the_run_mutates_the_units_the_strategy_named (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::StrategyScopedTests::test_the_blanket_sweep_does_not_also_run (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/stories/US0422-the-stated-strategy-names-the-units-worth-mutating.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0423 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticTests::test_three_lenses_run_before_the_plan_is_written (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticTests::test_a_lens_with_no_finding_is_distinct_from_a_lens_that_did_not_run (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticTests::test_a_failed_pass_leaves_no_run_and_no_plan_file (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0423-a-plan-critic-pass-runs-before-write-across.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0424 (story, Ready) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFindingDispositionTests::test_write_is_refused_while_a_finding_is_undispositioned (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFindingDispositionTests::test_a_decline_without_a_real_reason_is_refused (pytest)
- **issue:** `weak-AC` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0424-findings-must-be-filed-or-declined-with-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:weak-AC

### US0425 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticIntensityTests::test_a_larger_batch_receives_more_scrutiny (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticIntensityTests::test_the_pass_names_what_the_intensity_cap_skipped (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0425-the-pass-is-intensity-scaled-to-batch-size.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0426 (story, Ready) - copilot-tail

- **ac:** `AC1` - grep '## What the plan critic cannot see' .claude/skills/sdlc-studio/reference-sprint.md (grep)
- **ac:** `AC2` - grep 'Ponytail' .claude/skills/sdlc-studio/reference-sprint.md (grep)
- **ac:** `stale` - 1 AC(s) verified against changed code - re-run verify_ac
- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `sdlc-studio/stories/US0426-reference-sprint-md-states-the-plan-critic-has.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0427 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::DelegatedSignoffTests::test_a_subagent_in_its_own_context_is_accepted_and_marked (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::DelegatedSignoffTests::test_a_delegated_signoff_cannot_be_recorded_unmarked (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::DelegatedSignoffTests::test_self_approval_is_still_refused (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0427-a-subagent-reviewer-of-record-in-its-own.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0428 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DisclosureTests::test_every_delegated_signoff_is_named_with_its_delegate (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DisclosureTests::test_the_close_output_discloses_delegated_signoffs (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0428-the-sprint-report-and-the-close-output-disclose.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0429 (story, Ready) - copilot-tail

- **ac:** `AC1` - grep '## A disclosed sign-off is not an independent one' .claude/skills/sdlc-studio/reference-review.md (grep)
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0429-reference-review-md-states-plainly-that-a-disclosed.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0430 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalAwareBreakdownTests::test_an_ungroomed_batch_is_still_refused_at_goal_done (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalAwareBreakdownTests::test_the_same_batch_is_accepted_at_goal_design (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalAwareBreakdownTests::test_the_size_and_affects_gates_bind_at_the_design_rung_too (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0430-the-breakdown-gate-refuses-an-ungroomed-batch-at.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0431 (story, Ready) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GroomingReportTests::test_the_close_reports_the_grooming_it_produced (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GroomingReportTests::test_a_rung_that_groomed_nothing_is_reported_not_passed (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0431-a-design-rung-s-close-reports-how-many.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Generated at the run close (`handoff generate`) |
