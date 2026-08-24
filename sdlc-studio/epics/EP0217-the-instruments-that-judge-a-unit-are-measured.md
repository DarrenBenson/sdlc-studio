# EP0217: The instruments that judge a unit are measured from the change, not asserted about the file

> **Status:** Draft
> **Parent:** CR0550
> **Parent:** CR0549
> **Parent:** CR0548
> **Derived Point Total:** 45
> **Parent:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0547. Delivers the work CR0547 requested.

## Story Breakdown

- [x] [US0671: revert-check reverts a unit's production files and REFUSES when its own verifiers stay green](../stories/US0671-revert-check-reverts-a-unit-s-production-files.md)
- [x] [US0672: revert-check restores the working tree byte-exact, including when it is interrupted](../stories/US0672-revert-check-restores-the-working-tree-byte-exact.md)
- [x] [US0673: revert-check REPORTS a unit whose Affects names no production file rather than passing it](../stories/US0673-revert-check-reports-a-unit-whose-affects-names.md)
- [x] [US0674: revert-check runs as a gate lane, so a unit whose tests reach nothing is refused rather than reported](../stories/US0674-revert-check-runs-as-a-gate-lane-so.md)
- [x] [US0675: Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so](../stories/US0675-every-count-in-verification-depth-is-read-from.md)
- [x] [US0676: The derived half of Verification depth is delimited and a hand-edit to it is refused, while the author's judgement half survives verbatim](../stories/US0676-the-derived-half-of-verification-depth-is-delimited.md)
- [ ] [US0677: The code and risk subscores are computed from the hunks a unit CHANGES against the base ref, not from every function in every declared file](../stories/US0677-the-code-and-risk-subscores-are-computed-from.md)
- [ ] [US0678: A unit whose diff cannot be resolved bands FULL and names the basis the estimate used](../stories/US0678-a-unit-whose-diff-cannot-be-resolved-bands.md)
- [ ] [US0679: The scope subscore stops counting a test file present only because the Affects convention requires it](../stories/US0679-the-scope-subscore-stops-counting-a-test-file.md)
- [ ] [US0680: The band distribution over this repository's corpus is RE-MEASURED after the change and recorded, so the claim that the gate discriminates rests on a number](../stories/US0680-the-band-distribution-over-this-repository-s-corpus.md)
- [ ] [US0681: _plan_gate_active takes a SCOPE as well as a date, so the test-plan gate can be required of high-band units alone](../stories/US0681-plan-gate-active-takes-a-scope-as-well.md)
- [ ] [US0682: review.mutation_evidence stays independent of the test-plan scope, with a fixture setting both proving the two lanes stay sequential rather than nested](../stories/US0682-review-mutation-evidence-stays-independent-of-the-test.md)
- [ ] [US0683: The close REPORTS which units the test-plan gate applied to and which it exempted, with the band that decided each](../stories/US0683-the-close-reports-which-units-the-test-plan.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a unit whose production change is reverted to the run's base ref, when only that unit's own `Verify:` selectors run, then they FAIL - green after the revert is the refusal, because a test that passes without the fix is pinned to something other than the fix
- [ ] Given a unit whose tests genuinely exercise the shipped path, when the same revert-and-run happens, then they fail and the unit passes the check - the control, so the gate discriminates rather than refusing everything
- [ ] Given a unit whose `Affects` names no production file at all, when the check runs, then it REPORTS that rather than passing: nothing to revert is not evidence that the tests reach anything
- [ ] Given the revert, when the check completes or is interrupted, then the working tree is byte-identical to how it started - the check must not be able to leave a unit's production change reverted
- [ ] Given BG0593 as it stood on 2026-08-19 - four criteria green, four mutants recorded killed, and a production change no test reached - when the check runs against that commit, then it REFUSES

### From CR0548

- [ ] Given a unit with a Test Plan and a mutation ledger, when its `Verification depth` is rendered, then every COUNT in it - criteria, declared rows, executed, killed, survived - is read from the ledger and the verify report rather than from prose
- [ ] Given a unit whose ledger says a row was never executed, when the field is rendered, then it SAYS so; a derived field that can only report success is the defect this replaces
- [ ] Given the author's judgement half - the tier, and what was deliberately not covered - when the field is regenerated, then that half is preserved verbatim inside its delimiters
- [ ] Given a hand-edit to the DERIVED half, when the gate runs, then it is refused and named, exactly as a hand-edited `_index.md` is
- [ ] Given BG0592 as it stood on 2026-08-19 - a field claiming shipped-CLI coverage that did not exist - when the field is derived instead, then the claim is absent, because nothing in the ledger supports it

### From CR0549

- [ ] The `code` and `risk` subscores are computed from the hunks a unit changes against the run's base ref, not from every function in every declared file, and a unit with no diff yet degrades to the missing-signal path rather than to a whole-file score
- [ ] A two-line change to a large module and a rewrite of that module produce DIFFERENT bands, demonstrated by scoring both against the same file
- [ ] `scope` stops counting a test file that is present only because the project convention requires it in `Affects`, or the convention's contribution is stated and weighted separately
- [ ] The band distribution over this repository's bug corpus is re-measured after the change and recorded in the CR, so the claim that the gate now discriminates rests on a number rather than on the design
- [ ] A unit whose diff cannot be resolved bands FULL and says why, preserving the existing fail-towards-deeper-review rule
- [ ] `route.estimate`'s returned dict names which basis it used - diff or whole-file - so a reader can tell a measured band from a degraded one

### From CR0550

- [ ] `_plan_gate_active` takes a scope as well as a date, so a project can require the test plan for high-band units alone rather than for every unit past the cutoff
- [ ] A unit below the configured scope reaches `Fixed` without a planned-mutant join, while a unit at or above it is refused exactly as today - both demonstrated by execution through `transition.py`, not through the library
- [ ] The authoring-time rule that a criterion names a production change its test dies on is UNCHANGED and still applies at every band, so the setting narrows the ledger and never the falsifiability requirement
- [ ] `review.mutation_evidence` remains independent: a project setting `block` still blocks at every band, and a fixture setting both settings proves the two lanes stay sequential rather than nested
- [ ] An unresolvable band applies the gate rather than skipping it, matching the existing fail-towards-deeper-review rule
- [ ] The close reports which units the gate applied to and which it exempted, with the band that decided each, so an exemption is visible rather than silent

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
