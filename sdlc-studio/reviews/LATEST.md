
<!-- close-status:begin -->
> **RUN-01KZ56M6 closed goal-reached.** 7 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01KZ56M6 - the first run of the backlog-clearing programme.
> 22 of 22 points delivered across 7 units. Every unit is terminal, covered by an independent
> pass, and signed off by the operator. The batch review REJECTed round 1 on a regression this
> run introduced and approved round 2 after it was repaired.

## Landed: RUN-01KZ56M6 - a shipped mechanism does what its own record claims

The goal was that for every unit the gap between a mechanism's recorded claim and its actual
behaviour is closed and proven by execution - an executed mutant where the claim is a verifier,
a reproduced wrong result where the claim is behaviour. Judged **achieved**.

**Four verifiers that could not fail can now fail.** `BG0419` repaired the close dry run (which
evaluated only until its first refusal), the close's cost line (whose sole call site could be
deleted with 34 tests still passing), `critic`'s batch verbs (which asserted that nothing landed
rather than that nothing was attempted), and `reconcile.detect_all`'s corpus cache (whose eleven
tests each opened their own cache in a fixture, so they proved the mechanism and never its
caller). Every mutant was demonstrated to survive the old coverage before the repair and to die
after it.

**Three defects that reach consuming projects are fixed.** A skill-relative `Affects` path no
longer resolves to a consuming project's own file of the same name (`BG0494`). `refine` fills
the User Story fields it mints and reports the grooming it leaves owed, priced from the
planner's own census (`BG0477`). The shared points reader learns the `Story Points` spelling
that 20 stories use, so `batch add-epic` stops pricing whole epics at zero (`BG0501`).

**And `status` names the open run** on its first line - id, rung, Sprint Goal, batch, remaining -
so a session re-anchors from the one command AGENTS.md already tells it to run (`US0467`).

### What the reviews found, and why it matters

| Finding | Shape |
| --- | --- |
| The dashboard died on a structurally malformed run state | a regression this run introduced; base exit 0, HEAD exit 1, taking `hint` with it |
| `open_run` hand-rolled a second reader of `run-state.json` | the defect `BG0501` repaired elsewhere in the same batch |
| `BG0501`'s filed fix did not fix `BG0501` | the shared reader could not read the field either |
| `BG0485`'s premise did not reproduce | its fix shipped four days before the bug was filed |
| A criterion would have reinstated a deliberate fix | `BG0477` AC1 against commit `7ef88707` |

The first two came from the independent batch review. The next three came from the plan-time
goal review, before any code was written - which is where they were cheapest to find.

Five gates refused this work and were right every time: the lane-check (five verifiers that
never entered `main()`), the repo-hygiene sweep (a bare artefact read), the verify-ratchet (two
criteria sharing one selector - the very defect `US0635` exists for), the transition depth gate,
and the suite-claim lane (a verdict the tree had moved past).

### What is owed

| Item | Where |
| --- | --- |
| `batch add-epic` and `batch swap` skip the ungroomed census | `BG0512`, open |
| `US0467` AC5's doc verifier is presence-only | ruled not-stop-ship; the `BG0457` shape |
| `BG0419` AC5 is pinned by a grep over its own prose | ruled not-stop-ship; same shape |
| Twelve pre-existing findings carried under D0125 | filed, excluded from the v5 gate |

### The programme, honestly

`D0125` freezes the target at the 66 units open on 2026-08-03 and rules that a pre-existing
finding raised mid-programme is filed post-v5. Run 1 delivered **22 points in a full cycle**
including three goal-review rounds and a rejected batch review. The measured five-run mean is
61. Roughly 235 points remain.

Three runs will not clear that, and the operator has decided the programme is re-planned as
**more, smaller runs** rather than by cutting the ceremony - on this run's evidence, every
refusal the ceremony produced caught something that would otherwise have shipped, including a
crash in the very command the run existed to improve. The frozen target does not move; only the
run count does.
