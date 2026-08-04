> **Run of record:** RUN-01KZ5YXM - the charter queue. 26 of 26 points across 6 units, every
> one approved at the third review round and signed off under D0126. Two earlier rounds returned
> REJECT, and the tooling escalated the second to the operator for non-convergence. That
> escalation stands: both rejected versions passed every automated check in this repository
> while being wrong.

## Landed: RUN-01KZ5YXM - more, smaller runs becomes a command

The goal was that the programme's own re-plan stops being an intention. A charter is now a
first-class artefact (`SC`, `sdlc-studio/charters/`) whose prefix, create status and terminal set
are **derived** from the shared registry rather than restated beside the charter code.

**`sprint next` resolves the head charter against the backlog as it stands at that moment.** The
load-bearing test moves the backlog underneath a charter - one unit created since, one delivered
since - and asserts the second pass returns the new unit and not the delivered one. A cached
batch passes every other assertion in that class and fails only this.

**The queue is inspectable and editable.** `queue show`, `reorder`, `cancel`, `clear`. Cancel
withdraws rather than deletes and keeps its reason, because a cancelled plan is a decision
somebody made and deleting it loses the only trace of why the queue looks as it does. An
unranked charter sorts after every ranked one: absence is not rank zero.

**A charter carries its own goal review**, under `## Seat review` on the charter rather than in
`.local/`. The test proves it travels by deleting `sdlc-studio/.local` entirely and reading the
verdicts back from the file alone. The runner is recorded beside the reviewer and a match is
stated plainly - separation is recorded, never enforced, because a queue is usually planned and
run by one person and refusing that would make it unusable.

**`sprint call` finishes a run rather than abandoning it**: the unstarted remainder is descoped
to the **backlog**, never forward to the next charter, and the close chain then runs.

### What the reviews found, and why it matters

| Round | Finding | Why no gate caught it |
| --- | --- | --- |
| 1 | `call` printed "now close it against the goal" and did not close | AC1's verifier had been repointed to clear the lane-check |
| 2 | `call` could not execute at all - uncaught `AttributeError` on every path | the verifier stubbed the collaborator under test |
| 3 | APPROVE, judged by typing the command in nine argument shapes | - |

Both failures were the same error: **satisfying a gate rather than the criterion.** Both shipped
green through the full suite, `verify_ac`, the lane-check and `gate.py`. Round 2's version passed
every automated check in the repository while being a verb that could not run.

That is the clearest evidence this programme has produced for the independent pass. Eleven gate
refusals across the run were all correct and all useful - but no gate caught either of these,
because in both cases the thing being measured had quietly moved.

### What is owed

| Item | Where |
| --- | --- |
| `queue show` is blind during a run, reusing the materialiser's open-run refusal | `BG0514`, open |
| The queue has no exit - nothing sets `Spent`, so a charter re-materialises forever | `BG0515`, open |
| A scope query cannot express a decomposition; `SC0001`'s two scope fields disagree | `CR0531`, open |
| `run-suite.sh` intermittently red, and the failing test cannot be named | `BG0513`, open |
| The close reports "could not be attributed" where the gate named its lane plainly | `BG0516`, open |

### The programme

`D0125` freezes the target at the 66 units open on 2026-08-03. Two runs are closed: 22 points and
26 points. Roughly 183 points remain, and at this rate that is several more runs - which is the
shape the operator chose when they re-planned it as more, smaller runs.

`SC0001` sits at the head of the queue: **the close costs less than it returns**, the complaint
raised three times and still unanswered. `CR0531` must land first or its scope query resolves 15
CRs against an 8-unit appetite.
