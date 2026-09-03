# HO-0066: A unit's acceptance criteria can be EXECUTED, and the instruments that judge them report one number each. (1) `file_finding.py file` authors a criterion together with its verifier, byte-exact, and REFUSES to mint one carrying no verifier at all - `_md_safe` backtick-wraps underscored tokens, so a selector routed through it is corrupted rather than merely present. (2) `sprint plan`, driven as a subprocess, REFUSES a batch holding a unit whose criteria carry neither an executable verifier nor a manual marker, and `_AC_MISS` carries a rendering for that reason so the planner does not KeyError on its own new refusal. The refusal is enforced on the whole population with no grandfather, on the operator's ruling of 2026-09-02, which takes 12 of 19 open bugs out of the plannable backlog until each is groomed - a cost accepted deliberately rather than discovered. (3) `conformance` separates a unit it could not EVALUATE from one that genuinely FAILED, so the lane stops returning three different figures for one corpus depending only on which directories were copied. (4) A repair row names the phase and the rejection it answers, and a delivery repair no longer discharges a plan-review rejection that carries the SAME finding text on the same date. (5) `sprint close` takes both its convergence count AND its recorded stages from `held_blockers()`, so an all-advisory pre-flight records zero and no stages, and `review.max_rounds` is REMOVED from the project config rather than set to a number - no single value is right for a key two consumers read with different defaults, and D0177's interim authorisation expires on that commit. (6) US0569 to US0576 each reach a recorded resolution - an independent verdict or a waiver naming what is being set aside - because `conformance` is a blocking release-boundary lane and the release bar going green does not make this repository taggable. (7) BG0634 and BG0632 close under recorded triage reasons quoting the source line that falsifies each filed premise, and their live residues are carried as their own units rather than discharged by the closure

> **Date:** 2026-09-03
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M1H09S (started 2026-09-02T12:16:23Z)
> **Outcome:** goal-reached
> **Batch source:** run-state.json

## Where to pick up

4 of 4 unit(s) remain (0 suit copilot-assisted completion, 4 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 1119.1 min, 4 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~2,520,746 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (4)

### BG0636 (bug, Fixed) - judgement

- **check:** `verify:unproven` - the file says delivered; the evidence says 7 red AC(s) - reconcile the two (re-run verify_ac, fix, or reopen)
- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::VerifierAuthoringTests::test_the_verifier_reaches_the_artefact_byte_exact (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::VerifierAuthoringTests::test_a_criterion_with_no_verifier_is_refused_at_filing (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::VerifierGroomingTests::test_plan_refuses_a_unit_whose_criteria_cannot_be_executed (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::VerifierGroomingTests::test_every_ungroomed_reason_has_a_rendering (pytest)
- **ac:** `AC5` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::VerifierGroomingTests::test_a_section_that_parses_to_nothing_is_ungroomed (pytest)
- **ac:** `AC6` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::VerifierGroomingTests::test_a_verifier_bearing_unit_stays_groomed (pytest)
- **ac:** `AC7` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::VerifierGroomingTests::test_the_refused_population_matches_the_shipped_scan (pytest)
- **issue:** `missing-regression-test` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0636-file-finding-py-has-no-verify-so-every.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by verify:unproven, difficulty:high

### BG0628 (bug, Fixed) - judgement

- **check:** `verify:unproven` - the file says delivered; the evidence says 4 red AC(s) - reconcile the two (re-run verify_ac, fix, or reopen)
- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UnevaluableTests::test_an_unresolvable_selector_reports_unevaluable_not_non_conformant (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UnevaluableTests::test_a_resolving_selector_that_fails_is_still_non_conformant (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UnevaluableTests::test_the_check_names_the_unevaluable_population_before_its_verdict (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UnevaluableTests::test_a_partial_tree_does_not_change_the_non_conformant_count (pytest)
- **issue:** `missing-regression-test` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0628-conformance-reports-a-unit-non-conformant-when-it.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by verify:unproven, difficulty:high

### BG0631 (bug, Fixed) - judgement

- **check:** `verify:unproven` - the file says delivered; the evidence says 5 red AC(s) - reconcile the two (re-run verify_ac, fix, or reopen)
- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_a_delivery_repair_does_not_answer_a_same_text_plan_review_rejection (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_the_delivery_phase_still_reads_its_own_repair (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_a_written_row_carries_its_phase_and_rejection (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_legacy_rows_are_attributed_or_named_unattributable (pytest)
- **ac:** `AC5` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_every_unit_that_moves_is_named_with_its_reason (pytest)
- **issue:** `missing-regression-test` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-schema.md` - declared Affects
- **file:** `sdlc-studio/reviews/repair-record.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0631-a-repair-row-names-neither-the-rejection-nor.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by verify:unproven, difficulty:high

### BG0635 (bug, Fixed) - judgement

- **check:** `verify:unproven` - the file says delivered; the evidence says 4 red AC(s) - reconcile the two (re-run verify_ac, fix, or reopen)
- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_an_all_advisory_preflight_records_zero_and_no_stages (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_a_blocking_lane_is_still_counted_and_named (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_a_converged_run_at_the_cap_reaches_a_later_stage (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_the_project_config_pins_no_round_cap (pytest)
- **issue:** `missing-regression-test` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/.config.yaml` - declared Affects
- **file:** `sdlc-studio/bugs/BG0635-the-close-s-convergence-series-counts-advisory-gate.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by verify:unproven, difficulty:medium

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Generated at the run close (`handoff generate`) |
