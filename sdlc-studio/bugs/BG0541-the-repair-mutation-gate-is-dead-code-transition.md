# BG0541: the repair-mutation gate is dead code: transition.py set does not call it, while the shipped doctrine tells consuming projects that it refuses

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, tools/tests/test_check_spec_claims.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, independent delivery review of US0564/US0565/US0566/US0567/US0573. Demonstrated at the shipped entry point: exit 0 from the CLI against STALE from the library, and exit 1 without the exemption file against exit 0 with it. Four declared mutants also survived their own verifiers, including `mutants_over_changed_lines` returning [] unconditionally.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0564-US0567 built a gate requiring a repair to carry mutation evidence over its own changed lines. `transition.repair_mutation_gate` and `mutation.mutants_over_changed_lines` have ZERO non-test callers. `_pre_write_gates` wires the pre-existing `_planned_mutant_gate`, which is test-plan-row based and satisfied by a self-reported `register` claim with no changed-line evidence at all.

Every criterion in that wave names `transition.py set` as its When. The tests call the library function directly, so none of them can see the missing lane - the scar AGENTS.md records verbatim.

The part that reaches consuming projects is worse than the gap. `reference-doctrine.md` rule 21 states that `transition.py` refuses the terminal status of a repair whose changed surface carries no surviving-mutant evidence, and the Definition-of-Done template carries the matching clause under a registered check id. Both are false. `test_the_named_gate_actually_exists` is the guard written to catch precisely this INERT state, and it anchors on `_plan_gate_active` and `review.test_plan_after` - both present at the run's base ref - so it is green while the condition it names holds.

## Steps to Reproduce

1. Build a fixture bug with a Python surface and a mutation record stale against the edited bytes. 2. `transition.py set --id BG0001 --status Fixed` exits 0. 3. `transition.repair_mutation_gate('.', 'BG0001', text)` returns STALE for the same unit. The library refuses and the command does not.

## Proposed Fix

Wire `repair_mutation_gate` into `_pre_write_gates` so the shipped verb reaches it, and re-point every criterion in the wave at a test that drives `transition.py set` rather than the function. Until then, either the doctrine passage and the DoD clause are corrected to describe what the tree does, or they are removed - a mechanism named in a consuming-facing file that does not exist is worse than no rule, because a reader stops looking for the gap.

US0566's exemption is the second half. `verify_no_surface_claim` re-derives over the record's OWN self-declared paths rather than the unit's changed lines, so a hand-written `.local/no-mutatable-surface.json` naming `README.md` exempts a repair whose Affects is a mutatable module. AC4's own words: an exemption an author can assert is the gate's own fail-open.

## Acceptance Criteria

- [ ] **AC1:** The shipped verb reaches the gate. A bug whose mutation record is STALE against the
      edited bytes, under `review.mutation_evidence: block`, is REFUSED by `transition.py set
      --id <id> --status Fixed` naming STALE - so the command and the library give the same
      answer. Today the CLI exits 0 while the library returns STALE.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_the_command_refuses_what_the_library_refuses
- [ ] **AC2:** The default mode reports and proceeds. With no `review.mutation_evidence` set, the
      same fixture exits 0, the artefact reads `Fixed`, and the stale evidence is named as a
      warning. Wiring a new hard block would contradict the operator's decision in CR0537.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_the_default_mode_reports_and_the_transition_proceeds
- [ ] **AC3:** The exemption is re-derived from the diff, not from its own paths. A repair whose
      `Affects` is a mutatable Python module with committed changed lines, carrying a hand-written
      `.local/no-mutatable-surface.json` naming `README.md`, is REFUSED in every mode but `off`,
      naming both the claimed path and the derived one. An empty base ref refuses rather than
      granting the exemption - the fallback fails the worse way here.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::NoSurfaceExemptionCLITests::test_a_claim_over_another_file_is_refused_through_the_command
- [ ] **AC4:** The guard can fail, over every lane the doctrine names. The reachability predicate
      takes its lane set from the code rather than a list typed into the test, and answers False
      when ANY one of them is unreached - demonstrated by removing each call in turn from a copy
      of `transition.py`'s source, while answering True over the real source. A predicate pinned
      to one call site is the enumerated-list defect the registry already records, and would let
      this same gap reopen one lane along.
      **Verify:** pytest tools/tests/test_check_spec_claims.py::DoctrineTests::test_removing_any_lane_call_reddens_the_guard

- [ ] **AC5:** The lane does not inherit an unrelated cutoff. With `review.test_plan_after` absent
      - so `_plan_gate_active` is False - a STALE repair under `review.mutation_evidence: block`
      is still REFUSED by the shipped verb. Today's repair branch sits inside that condition, so
      a lane hung there would be inert in every project that has not set a test-plan cutoff,
      while a fixture setting both went green: the dead-lane defect this bug exists to close,
      recreated one level in.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_the_lane_runs_with_no_test_plan_cutoff_set

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | delete the `mutation_evidence_lane` call from `_pre_write_gates` in transition.py - the state of the tree today | The shipped verb reaches the gate. A bug whose mutation record is STALE against the |
| AC2 | change transition.py to map the report mode onto the blocking arm | The default mode reports and proceeds. With no `review.mutation_evidence` set, the |
| AC3 | revert transition.py to re-deriving the exemption from the record's own declared paths | The exemption is re-derived from the diff, not from its own paths. A repair whose |
| AC4 | narrow the predicate in tools/tests/test_check_spec_claims.py to one hard-coded lane name, so an unreached sibling still counts as wired | The guard can fail, over every lane the doctrine names |
| AC5 | nest the `mutation_evidence_lane` call inside the existing `_plan_gate_active` condition in transition.py | The lane does not inherit an unrelated cutoff |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
| 2026-08-07 | sdlc-studio | AC5 added and AC4 widened, both from the plan-time seat review: engineering found the repair branch sits inside `_plan_gate_active`, so a lane hung there is inert wherever `review.test_plan_after` is unset; qa found the reachability predicate covered one call site, so the same gap could reopen one lane along |
