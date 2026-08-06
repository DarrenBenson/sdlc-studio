# HO-0053: v5 release sprint: the verification claim is half true, twelve units remain

> **Date:** 2026-08-06
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZCAJX (started 2026-08-06T19:54:48Z)
> **Outcome:** running
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

18 of 18 unit(s) remain (9 suit copilot-assisted completion, 9 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 56.2 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~4,197,908 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (18)

### BG0516 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0516-the-close-reports-a-gate-refusal-it-could.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0521 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0521-us0481-ships-a-config-key-that-does-nothing.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0530 (bug, Open) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_a_section_that_parses_to_nothing_is_refused_through_the_cli (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_absent_and_unparseable_are_different_events (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::WriterMatchesParserTests::test_a_freshly_filed_bug_parses (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_the_corpus_scan_reports_three_distinct_states (pytest)
- **ac:** `AC5` - pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseVerifyScopeTests::test_the_release_lane_states_its_scope (pytest)
- **ac:** `AC6` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_criteria_with_no_verifiers_are_not_a_pass (pytest)
- **ac:** `AC7` - pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_a_well_formed_unit_still_passes (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_file_finding.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0530-verify-ac-reports-a-unit-whose-criteria-it.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### BG0533 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0533-the-mutation-engine-enumerates-a-mutant-at-one.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0524 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0524-warning-ratchet-reports-a-stale-baseline-as-clean.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0564 (story, Ready) - judgement

- **issue:** `unmet-deps: BG0533:Open` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0564-a-unit-typed-as-a-repair-requires-mutation.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps

### US0565 (story, Ready) - judgement

- **issue:** `unmet-deps: BG0533:Open` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/stories/US0565-the-gate-is-the-survivor-count-over-those.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps

### US0566 (story, Ready) - judgement

- **issue:** `unmet-deps: BG0533:Open` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0566-feature-work-keeps-the-cheaper-bar-and-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0567 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/reference-doctrine.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/core/definition-of-done.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-agentic-lessons.md` - declared Affects
- **file:** `tools/tests/test_check_spec_claims.py` - declared Affects
- **file:** `sdlc-studio/stories/US0567-the-shipped-doctrine-states-that-a-fix-s.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0573 (story, Ready) - judgement

- **issue:** `unmet-deps: BG0533:Open` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/stories/US0573-an-uncommitted-changed-surface-is-reported-as-that.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0591 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0591-every-checklist-item-declares-its-enforcing-command-and.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0592 (story, Draft) - judgement

- **issue:** `unmet-deps: BG0516:Open, BG0521:Open` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0592-the-goal-seat-review-is-enforced-by-sprint.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0593 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0593-a-run-whose-only-review-verdicts-are-reject.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0594 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0594-a-unit-whose-ticked-criteria-the-tree-contradicts.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0595 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/decisions.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_decisions.py` - declared Affects
- **file:** `sdlc-studio/stories/US0595-a-waiver-records-whether-it-was-deliberate-or.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0596 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0596-coverage-is-computed-once-and-two-rows-disagreeing.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0635 (story, Ready) - judgement

- **issue:** `unmet-deps: BG0530:Open` - tranche audit
- **file:** `sdlc-studio/stories` - declared Affects
- **file:** `sdlc-studio/.verify-lint-baseline.json` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0635-the-thirteen-story-side-duplicate-verify-groups-are.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0636 (story, Ready) - judgement

- **issue:** `unmet-deps: BG0530:Open` - tranche audit
- **file:** `sdlc-studio/bugs` - declared Affects
- **file:** `sdlc-studio/.verify-lint-baseline.json` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0636-the-seven-bug-side-duplicate-verify-groups-are.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Generated at the run close (`handoff generate`) |
