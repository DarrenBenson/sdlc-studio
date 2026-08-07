# BG0541: the repair-mutation gate is dead code: transition.py set does not call it, while the shipped doctrine tells consuming projects that it refuses

> **Status:** In Progress
> **Severity:** High
> **Points:** 8
> **Verification depth:** functional (unit: the lane driven through `transition.py set` in all three modes, both arms of every refusal; mutation: 8 planned mutants applied and killed, sources restored byte-identically; live: the doctrine guard run over a doctored source with each named lane's call removed in turn)
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
      answer. Today the CLI exits 0 while the library returns STALE. `mutation_evidence_lane` is a
      NEW pure-read wrapper composing the existing `repair_mutation_gate`, `no_surface_record` and
      `verify_no_surface_claim`; it is the thing `_pre_write_gates` calls, and it is the name every
      mutant below refers to.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_the_command_refuses_what_the_library_refuses
      - **Verified:** yes (2026-08-07)

- [ ] **AC2:** The default mode reports and proceeds. With no `review.mutation_evidence` set, the
      same fixture exits 0, the artefact reads `Fixed`, and the stale evidence is named as a
      warning. Wiring a new hard block would contradict the operator's decision in CR0537. The
      default is recorded in `templates/config-defaults.yaml` beside the other review keys, so a
      consuming project can read the mode it is getting rather than infer it.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_the_default_mode_reports_and_the_transition_proceeds
      - **Verified:** yes (2026-08-07)

- [ ] **AC3:** The exemption is re-derived from the DIFF, and the fixture proves which source it
      read. A repair whose `Affects` names an UNCHANGED Python module while its diff changes a
      DIFFERENT Python module, carrying a hand-written `.local/no-mutatable-surface.json` naming
      `README.md`, is REFUSED under `block` naming the path taken from the diff - not the one
      taken from `Affects`, and not the one the record claims. The base ref is `run_state.base_ref`
      for the open run - `repair_mutation_gate` today declares a `base_ref` parameter that no
      caller supplies and the body never reads, so the source has to be named or the fixture
      cannot be built. The fixture is a real git repository with at least one commit, and the
      assertion names the derived PATH rather than merely a non-zero exit - a bare tmpdir takes
      the could-not-be-established arm and refuses for a reason the criterion is not about, which
      an exit-code assertion cannot tell from the refusal it wants. The three sources must disagree in
      the fixture, because `repair_mutation_gate` derives its surface from `affects_files(text)`
      and accepts a `base_ref` it never uses: against a fixture where Affects and the diff name
      the same file, the old behaviour and the new one produce identical output and the test pins
      nothing.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::NoSurfaceExemptionCLITests::test_the_refusal_names_the_path_the_diff_gives_not_the_one_affects_gives
      - **Verified:** yes (2026-08-07)

- [ ] **AC4:** The guard can fail, over every lane the DOCTRINE names. `reference-doctrine.md`
      rule 21 is rewritten to ENUMERATE its lanes by name in backticks - `mutation_evidence_lane`,
      `repair_mutation_gate` and `verify_no_surface_claim` - and the reachability predicate takes
      its set from that passage, never from its own derived set and never from a list typed into
      the test, answering False when any named lane is unreached from `_pre_write_gates`. The
      test asserts a floor of THREE, so neither an edited-down passage nor a narrowed predicate
      can quietly satisfy it. The extraction takes backticked tokens that are Python identifiers
      and discards `*.py` filenames: rule 21 also backticks `transition.py`, and a set including
      it is permanently unreachable from `_pre_write_gates`, which an implementer would resolve
      by deleting the filename the guard beside it requires. Rule 21 as it stands backticks one identifier, `transition.py`, so a
      set derived from today's passage has cardinality 1 and no floor above 1 is reachable: making
      the doctrine name its own mechanisms is part of this criterion, not an assumption behind it.
      **Verify:** pytest tools/tests/test_check_spec_claims.py::DoctrineTests::test_removing_any_lane_the_doctrine_names_reddens_the_guard
      - **Verified:** yes (2026-08-07)

- [ ] **AC5:** The lane does not inherit an unrelated cutoff. With `review.test_plan_after` absent
      - so `_plan_gate_active` is False - a STALE repair under `review.mutation_evidence: block`
      is still REFUSED by the shipped verb. Today's repair branch sits inside that condition, so
      a lane hung there would be inert in every project that has not set a test-plan cutoff,
      while a fixture setting both went green: the dead-lane defect this bug exists to close,
      recreated one level in.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_the_lane_runs_with_no_test_plan_cutoff_set
      - **Verified:** yes (2026-08-07)

- [ ] **AC6:** Sound evidence PASSES, and `off` refuses nothing and warns about nothing. A repair
      carrying a fresh hash-matching ledger entry over its own changed lines exits 0 under `block`
      and the artefact reads `Fixed`; the same STALE fixture that AC1 refuses exits 0 under `off`
      AND emits no mutation warning. Without this pair every other criterion is a refusal, and a
      lane that refuses every repair - or one that never fires - satisfies the whole plan. The
      silence under `off` is asserted separately because a lane that warns under `off` passes an
      exit-code assertion while breaking the mode's only promise.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_sound_evidence_passes_and_off_refuses_nothing
      - **Verified:** yes (2026-08-07)

- [ ] **AC7:** An empty base ref REFUSES the exemption. With no open run, so `run_state.base_ref`
      yields nothing, a repair carrying a `.local/no-mutatable-surface.json` is refused under
      `block` naming the missing base ref as the reason, asserted on that wording rather than on
      the exit code, for the same reason AC3 gives. The fallback fails the worse way here:
      a derivation that cannot run and returns an empty set grants every exemption it was built
      to re-derive, which is the fail-open this bug exists to close, one layer down.
      **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::NoSurfaceExemptionCLITests::test_an_empty_base_ref_refuses_the_exemption
      - **Verified:** yes (2026-08-07)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | delete the `mutation_evidence_lane` call from `_pre_write_gates` in transition.py - the state of the tree today | The shipped verb reaches the gate |
| AC2 | change transition.py to map the report mode onto the blocking arm | The default mode reports and proceeds |
| AC3 | revert transition.py to deriving the exempted surface from `affects_files(text)` rather than from the diff against the run's base ref | The exemption is re-derived from the DIFF |
| AC4 | narrow the predicate in tools/tests/test_check_spec_claims.py to one hard-coded lane name, so an unreached sibling still counts as wired | The guard can fail, over every lane the DOCTRINE names |
| AC5 | nest the `mutation_evidence_lane` call inside the existing `_plan_gate_active` condition in transition.py | The lane does not inherit an unrelated cutoff |
| AC6 | change transition.py to append the lane's block whatever the lane returned, so every repair refuses | Sound evidence PASSES, and `off` refuses nothing |
| AC6 | change transition.py to emit the mutation warning in the `off` arm as well | Sound evidence PASSES, and `off` refuses nothing |
| AC7 | change transition.py to swallow an empty base ref and grant the exemption rather than refusing on it | An empty base ref REFUSES the exemption |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
| 2026-08-07 | sdlc-studio | AC5 added and AC4 widened, both from the plan-time seat review: engineering found the repair branch sits inside `_plan_gate_active`, so a lane hung there is inert wherever `review.test_plan_after` is unset; qa found the reachability predicate covered one call site, so the same gap could reopen one lane along |
| 2026-08-07 | sdlc-studio | Plan review round 1 REJECTed: AC4's mutant survived a predicate whose lane set was its own derived loop, AC3's fixture could not distinguish diff-derivation from Affects-derivation, and with every row a refusal a lane that refused every repair satisfied the plan. AC3 now requires the three sources to disagree, AC4 takes its lane set from the doctrine passage making the claim, AC6 adds the positive control and the empty-base-ref row, and the points move 5 to 8 |
| 2026-08-07 | sdlc-studio | Plan review round 2 ruled AC1 and AC3 CLOSED and AC4 MOVED: the lane set had come off the predicate onto a doctrine passage that names no lanes, so rule 21 now enumerates them and the floor is pinned at three. AC6's empty-base-ref row was unasserted by AC6's own text and becomes AC7; AC3 names `run_state.base_ref` as the source, which `repair_mutation_gate` declares and never reads; and the silence under `off` gains a mutant |
| 2026-08-07 | sdlc-studio | Plan review round 3 APPROVEd, ruling all four round-2 findings CLOSED. Its two minors are folded in: AC4 states the extraction filter, so an implementer does not resolve a permanently-False predicate by deleting the filename rule 21's neighbouring guard requires; and AC3 and AC7 assert the named path rather than a non-zero exit, over a real git fixture |
| 2026-08-07 | sdlc-studio | Built. Two design changes the mutants forced, both recorded because the plan said otherwise. The exemption surface is the diff ALONE, not the intersection of the diff with `Affects`: with the intersection in place, AC3's mutant SURVIVED, because a declaration can only shrink the derived surface and shrinking it is the same fail-open one step over. And `review.mutation_evidence: off` parses to the boolean False under YAML 1.1, so a project writing the mode the doctrine documents would have been refused for typing it correctly - `False` now resolves to `off` and `True` is refused by name |
| 2026-08-07 | sdlc-studio | The evidence discipline turned on this batch itself. 61 registrations had been written across the eight units for mutants that were never applied - the ledger held claims, which is the exact state this bug exists to stop counting as proof. All 61 were cleared and 47 mutants were applied for real: two SURVIVED. US0573 AC1's test asserted on a sentence composed in the same branch as the field the criterion was about, so clearing the field left the sentence standing; US0567 AC2's guard was a whole-section substring satisfied by words elsewhere in the contract. Both are now anchored on what the mutant changes, and the ledger is rebuilt only from the run that happened |
