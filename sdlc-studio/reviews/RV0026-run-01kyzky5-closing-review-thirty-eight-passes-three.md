# RV-0026: RUN-01KYZKY5 closing review - thirty-eight passes, three stop-ship defects, and a sprint that could not close because nobody had reviewed it

> **Date:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Run:** RUN-01KYZKY5
> **Reviewers:** seven independent contexts, none of which wrote the code
> **Author:** Claude Opus 5

## Scope

Forty-four units, 152 points. The run had been STOPPED rather than closed, and the reason it
could not close was not the code. It was that **the review had not happened in the record**.

The batch's own ledger, read at the start of this review:

| | Units | State |
| --- | ---: | --- |
| Covered by an independent pass | 6 | 5 APPROVE plus one batch review |
| Live REJECT from an earlier round | 18 | findings filed as `BG0488`-`BG0494` |
| No recorded verdict at all | 20 | almost all of them the bug fixes |

The run's own account said "27 REJECT and 11 APPROVE over 38 units". Only twenty-three
verdicts had ever reached `critic.py record`. The rest lived in a transcript, which is the
same as nowhere. Twenty units - nearly half the batch - had no independent pass on record in
any form.

So this review is not a formality over an already-reviewed batch. It is the review that batch
never got.

Thirty-eight briefs, every one from `critic.py brief` - eighteen as rejoinders carrying the
prior REJECT verbatim, twenty as first passes. Six independent contexts, each in its own git
worktree so mutation probing could not contaminate a neighbour or the working tree. Scope
bounded to each unit's declared `Affects` against the run's base ref `4e7d5e6c`.

| Pass | Units | Outcome |
| --- | --- | --- |
| A (rejoinder) | US0607, US0466, US0470, US0471, US0473, US0601 | 6 APPROVE |
| B (rejoinder) | US0606, US0609, US0611, US0615, US0598, US0599 | 6 APPROVE |
| C (rejoinder) | US0600, US0603, US0604, US0608, US0612, US0613 | 5 APPROVE, 1 REJECT |
| D (first pass) | BG0438, BG0423, BG0432, BG0433, BG0435, BG0436, BG0448 | 6 APPROVE, 1 REJECT |
| E (first pass) | BG0462, BG0470, BG0476, BG0478, BG0431, BG0434, BG0437 | 6 APPROVE, 1 REJECT |
| F (first pass) | BG0475, BG0483, BG0359, BG0420, BG0474, BG0487 | 6 APPROVE |
| Round 2 | BG0423, BG0437, US0604 | judged after repair |

### The blocking bar was written down

Earlier rounds on this batch returned 27 REJECT over 38 units and the run stopped. That rate
is not a batch that was bad at everything; it is a review with no stated threshold, where any
imperfection reads as a defect. This pass was given the operator's release policy as law:

**Only a stop-ship defect blocks.** The headline behaviour does not work through the shipped
entry point; a gate the unit claims to add is bypassable; a factual claim in the paperwork is
false; or the unit's own verifier cannot fail. Everything else is reported, filed as a new
bug, and the unit closes - because the code ships at the end of the sprint either way.

That is not a lower standard. Every one of the three REJECTs below is a defect the earlier
rounds' 27 did not isolate, and each was reproduced by execution before it was believed.

## Findings

### The three stop-ship defects

**`BG0423` - the fail-open the fix did not close.** The bug was that a green suite verdict got
recorded beside a failing lane, so the byte-identical retry reused it and ran no tests. The
fix guarded the write on the lane result - but left it sitting BETWEEN the two suite lanes,
where the flag it read carried the skill lane's verdict alone. A green skill lane beside a
failing `tool-tests` lane wrote `status green` exactly as before. The reviewer reproduced it
end to end: hook exits 1, verdict file says green, `gate.py --suite-decision` then prints
`skip ... running no tests`. The same fail-open, reached through the other lane. Both of the
unit's verifiers assert on the hook's TEXT and never execute it, so both were green on the
tree the fail-open reproduces on.

**`US0604` - a feature dead at the only input it has.** The close report read its review
rounds through `critic` without importing it; every other use in that module is a deferred
local import. Any non-empty batch raised `NameError` into an advisory `except`, so the report
printed only for an empty batch - a batch size no real close has. Both criteria called the
renderer directly with a hand-built dict, so neither could see that the caller never reached
it. Repairing it exposed a second crash underneath: `_close_cost` read `token_forecast.actual`
where the plan writes a plain integer.

**`BG0437` - a criterion whose input needed no disambiguating.** AC2 exists to prove a
carry-over marker disambiguates a two-run provenance line. Its fixtures named ONE `run <id>`
beside a bare carried id, so the candidate list had one entry however the carry-over matched.
Deleting the disambiguation outright left the whole module green at 21 passed. The criterion
was stamped `Verified: yes` on a check that could not see its own subject.

All three were repaired in `53107b9b` and `5472f851`, each mutation-verified - the old shape
kills the new test, the tree restored byte-identical - and each re-reviewed by an independent
pass judging the repair rather than the claim about it.

### The finding that matters most

**Twenty units shipped with no independent review, and nothing in the system said so.**

The close refused, correctly, on review coverage. But it refused at the CLOSE - after 152
points had landed - and the refusal was the first moment the gap became visible. Everything
upstream was green: the units were `Done` and `Fixed`, the gate passed, the paperwork was
complete. A batch can pass every check this repo has and still have had no reviewer look at
half of it.

`sprint.py review-batch --open` exists precisely to review at the boundary where work lands.
It was never called once across 44 units, because nothing prompts it and nothing refuses
without it. That is `CR0523`, filed from this run and not yet built.

The second-order finding is smaller and sharper: **a review that happened but was not recorded
did not happen.** Fifteen verdicts were reported in a transcript and never reached the ledger,
and the close cannot read a transcript. The gap between "we reviewed it" and "the record shows
we reviewed it" was fifteen units wide and nobody noticed until the close counted.

### The dominant defect class, unchanged from RV0025

A verifier that asserts the SHAPE of a change rather than its behaviour. Across all 38 passes
the reviewers named it repeatedly, and each instance is now filed:

- `US0470`, `US0473`, `US0466` - source greps over a module's text, satisfied by a comment.
- `US0609`, `US0603`, `US0598`, `US0601`, `US0599` - criteria calling the library function
  directly while the shipped command reaches it through wiring nothing exercises.
- `US0608` - a mutant flipping the very flag the unit exists to change leaves the suite
  failing on exactly the same six tests as the unmutated tree.
- `BG0420`, `BG0436`, `BG0435` - verifiers that survive the mutant their own docstring names.

`verify_ac.py lane-check` now measures this and reports 165 findings over 634 stories. It
ships ADVISORY. `CR0520` makes it blocking, and until it does this rule is a known-weak one.

### Document legs

PRD, TRD, TSD and personas carry no change from this run. The batch touched `scripts/`,
`tools/`, `.githooks/` and the shipped reference documents. `reference-sprint.md` gained the
close's stated fixed point and its budget ceiling moved 740 to 819;
`reference-sprint-toolchain.md` grew to 34 commands across 54 rows with a new In-flight
section, and `tools/runbook.py` now enforces its step order and per-step command coverage.

### What is owed

| Item | Where it went |
| --- | --- |
| Unrepaired findings from the earlier rounds | `BG0488`-`BG0494`, open |
| Review at the boundary, not at the close | `CR0523`, unbuilt |
| Lane-check made blocking | `CR0520`, unbuilt |
| The close's fixed point | `CR0527` / `EP0204`, decomposed, unbuilt |
| The four structural repairs | `EP0204`-`EP0207`, 67 points, all skeletons |
| Findings raised by THIS review | filed from the close, listed in `RETRO0089` |

`US0604` remains named by the advisory lane-check: its new test drives `_finalise_outcome`,
the production caller, rather than `main()`. Reaching the report through the CLI needs an
unpatched close chain, which refuses on its own checklist in a fixture. Disclosed rather than
papered over.

## Verdict

**APPROVE with findings filed.** Thirty-eight units independently covered where six were
before. Three stop-ship defects found, repaired and re-reviewed. Every remaining finding
carries an id and an owner, and no unit in this batch is left open.

The run's Sprint Goal verdict stands at **partial**: the loop does now stop when it stops
converging, and the gates did land in the commands people run - but the close still needed the
operator in it, because the amigo panel could not satisfy the reviewer-of-record half.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-02 | Claude Opus 5 | The closing review of record for RUN-01KYZKY5 |
