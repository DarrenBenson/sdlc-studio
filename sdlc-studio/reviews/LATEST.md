> **Run of record:** RUN-01KYZKY5 - closing review [`RV0026`](RV0026-run-01kyzky5-closing-review-thirty-eight-passes-three.md).
> 152 of 152 points delivered across 44 units. Every unit is terminal and independently
> reviewed. Three stop-ship defects were found, repaired and re-reviewed.

## Landed: RUN-01KYZKY5 - the batch delivered in full, and the review finally happened

The run had been STOPPED rather than closed, and the reason was not the code.

**The review had not happened in the record.** Of 44 units: six were covered by an independent
pass, eighteen carried a live REJECT from an earlier round, and **twenty had no recorded
verdict at all** - almost all of them the bug fixes. The run's own account claimed "27 REJECT
and 11 APPROVE over 38 units", but only twenty-three verdicts had ever reached
`critic.py record`. The rest lived in a transcript, and the close cannot read a transcript.

So the close was right to refuse, and what it was refusing was real.

`RV0026` is the review that batch never got: 38 briefs from `critic.py brief`, six independent
contexts in their own git worktrees, scope bounded to each unit's `Affects` against
`4e7d5e6c`. Eighteen rejoinders carrying the prior verdict verbatim, twenty first passes.

### What the review found

Three stop-ship defects, each reproduced by execution before it was believed:

| Unit | Defect |
| --- | --- |
| `BG0423` | the fix for a fail-open left the verdict write BETWEEN the two suite lanes, so a failing `tool-tests` lane still recorded `status green` and the identical retry ran no tests |
| `US0604` | the close report called `critic` without importing it, so every non-empty batch raised `NameError` into an advisory `except` - it printed only for an empty batch |
| `BG0437` | a criterion testing disambiguation whose fixtures needed no disambiguating - deleting the feature outright left the module green at 21 passed |

All three share one shape: **the feature did not work through the entry point, and the
verifier could not see it.** Each was repaired, mutation-verified, and re-reviewed by a pass
judging the repair rather than the claim about it.

Round two then found a fourth of the same class on a different criterion, and a fifth that
this run's own repair had introduced - a bare `index()` in a neighbouring test falling through
to the second occurrence a new log capture had created. Both fixed. A repair that quietly
weakens the test beside it is exactly what round two exists to catch.

### The finding that outranks all of them

**Twenty units shipped with no independent review, and nothing in the system said so.** The
units were `Done` and `Fixed`, the gate was green, the paperwork complete. A batch can pass
every check this repo has while nobody has looked at half of it, and the first moment that
becomes visible is the close refusing after 152 points have landed.

`sprint.py review-batch --open` exists to review at the boundary where work lands. It was
never called once across 44 units, because nothing prompts it and nothing refuses without it.
That is `CR0523`, unbuilt.

The second-order version is sharper: **a review that happened but was not recorded did not
happen.** Fifteen verdicts were reported and never written down.

### What is owed

| Item | Where |
| --- | --- |
| Unrepaired findings from the earlier rounds | `BG0488`-`BG0494`, open |
| Review at the boundary, not at the close | `CR0523` |
| `lane-check` made blocking (165 findings over 634 stories, advisory today) | `CR0520` |
| The close's fixed point | `CR0527` / `EP0204` |
| The four structural repairs | `EP0204`-`EP0207`, 67 points, all skeletons |

`US0604` is still named by the advisory lane-check: its criterion enters `_finalise_outcome`,
the production caller, not `main()`. Round two confirmed the criterion is pinned regardless,
killing every mutant including deletion of the emitter's body. Disclosed, not papered over.

### Sprint Goal: partial

The loop does now stop when it stops converging, and the gates landed in the commands people
run. But the close still needed the operator in it, because the amigo panel could not satisfy
the reviewer-of-record half - which was the goal's headline.
