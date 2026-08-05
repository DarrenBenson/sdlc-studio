# BG0510: the plan-review ledger has no kind column, so a second pre-code gate would be cleared by the first gate's approval

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Found at the plan-time goal review for RUN-01KZ (EP0207), independently by the QA and product seats, each by reading critic.py and plan_review.py rather than by running the batch. Confirmed by the author at transition.py's plan_review.gate call site and at critic.verdict_for.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A plan-review verdict is keyed by unit and phase only - `critic.verdict_for(root, unit, phase='plan-review')` returns the latest row for that pair, and `plan-review-verdicts.md` carries no column saying WHAT was reviewed. Today only one kind of plan review exists: the US0090 pre-implementation AC-vs-spec check that `plan_review.gate` enforces from `transition.py` on entry to In Progress, Review or Done. That is sound while the kind is unique. It stops being sound the moment a second pre-code artefact is reviewed through the same phase, because one approval then discharges both gates and neither reviewer read the other's artefact. This was found while planning EP0207, whose US0630 proposed exactly that second gate: the criterion as drafted read 'an APPROVE row in plan-review-verdicts.md', which a design-plan approval satisfies with no test plan ever written. The criterion was withdrawn rather than shipped, so nothing in the tree is wrong today - what is wrong is that the ledger's shape makes the mistake the DEFAULT for the next author, and two independent review seats found it only by reading the source.

## Steps to Reproduce

1. Read `critic.verdict_for` - the signature is (`repo_root`, unit, phase) and the phase vocabulary is the two-item PHASES tuple.
2. Read the header of sdlc-studio/reviews/plan-review-verdicts.md - the row schema is Unit, Verdict, Reviewer, Author, Date, Issues. Nothing records which artefact was judged.
3. Read transition.py where it calls `plan_review.gate` - the one consumer, and the reason the ambiguity is currently harmless.

## Proposed Fix

Give a plan-review row a KIND (the artefact judged - spec, test-plan, whatever follows) and make the lookup take it. Default the existing rows to the spec kind so no history is reinterpreted. A gate then asks for an approval of the artefact it actually cares about, and a phase with one kind stays a one-word change away from a phase with two.

## Acceptance Criteria

- [x] **A plan-review row records the kind of artefact it judged**, written by `critic record --kind` and read back as a parsed field. *Mutant:* keep the seven-column schema - the field is absent on read-back. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_a_plan_review_row_records_its_kind
- [x] **The lookup discriminates on kind.** A `spec` approval does not satisfy a `test-plan` lookup, and with both rows present each query returns its own. *Mutant:* ignore the kind in the lookup - one approval discharges both gates and neither reviewer read the other's artefact. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_a_spec_approval_does_not_satisfy_a_test_plan_lookup
- [x] **A caller that names no kind still sees every row**, so nothing that reads this log today changes. *Mutant:* filter on the default when no kind is named - a test-plan verdict becomes invisible to every existing reader. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_a_caller_that_names_no_kind_still_sees_every_row
- [x] **Existing rows default to the spec kind, so no history is reinterpreted.** Only one kind was ever reviewed, which makes `spec` a fact about those rows rather than an assumption. *Mutant:* read an absent kind as unknown - every historical approval stops counting and `transition` refuses units it passes today. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_an_existing_row_defaults_to_spec
- [x] **The legacy table is PADDED, not rewritten, and every cell keeps its value and position.** LL0028: the migration is attacked, not re-read - and this sprint had already watched a column added to VELOCITY.md shift every historical row. *Mutant:* append the cell after Issues instead of before it - a recorded judgement moves column. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_the_legacy_table_is_widened_and_its_cells_keep_their_values
- [x] **The one live consumer asks for its own kind.** `plan_review.gate` requests `spec`; a test-plan approval no longer discharges the AC-vs-spec check, and every case it passes and refuses today it still passes and refuses. *Mutant:* leave the gate asking for any kind - the column exists and nothing reads it, which is the state `critic brief --tier` is already in. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::PlanReviewKindTests::test_the_gate_asks_for_the_spec_kind_and_its_behaviour_is_unchanged
- [x] **An approval recorded before the column existed still clears the gate.** *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::PlanReviewKindTests::test_an_approval_recorded_before_the_column_existed_still_clears_the_gate
- [x] **An unknown kind is refused at write time**, naming the vocabulary. *Mutant:* accept any string - a misspelt kind silently creates a gate that can never be satisfied and that nobody can see. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_an_unknown_kind_is_refused_at_write_time
- [x] **A kind on the DELIVERY phase is refused**, because a delivery verdict judges the diff and a kind has no meaning there. *Mutant:* accept and ignore it - a caller believes it recorded a distinction the record does not hold. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_a_kind_on_the_delivery_phase_is_refused
- [x] **The shipped verb records it, not only the library.** LL0040: the flag has to reach `record_verdict` from the parser. *Mutant:* add the argument and forget to pass it - every other criterion still passes and this reddens. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewKindTests::test_the_shipped_verb_records_the_kind

## Impact

Latent rather than live. It costs nothing today and it silently mis-designs the next pre-code gate somebody adds - which is a gate whose whole purpose is to refuse work, so the failure mode is a gate that passes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
