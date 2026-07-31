# Latest review anchor

<!-- close-status:begin -->
> **RUN-01KYPZ1G closing.** 36 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Goal verdict:** partial - clauses 1 and 2 achieved, clause 3 partial
> · **Delivered:** 20 units / 57 points of a 46-unit 150-point plan
> · **Carried:** 26 units, each dropped with a recorded reason

## Landed: RUN-01KYTKA1 - the standing review debt, cleared honestly

The batch was 19 gate-honesty bugs plus the 26 units that had been sitting at Review with no
independent verdict. **13 bugs Fixed and 7 stories Done. 19 stories carry a recorded REJECT
and 7 bugs were never built** - all 26 carried with reasons, on the operator's ruling that
bugs may carry forward.

**The review is the result.** Seven independent seats across three charters (engineering,
product, QA), each in its own worktree, none of them the author, applied roughly 180 mutants
and rejected 19 of the 26 units. Every rejection carries a filed finding with an executed
reproduction: BG0457 through BG0463, plus CR0509.

One shape recurs, attested independently by more than one seat - **a guard reporting green
over something it never checked**:

- a guard comparing a document against a projection of itself, so the reverse direction is
  structurally unrepresentable (`named = _backticked(block) & types`, then asserting
  `types - named == set()`)
- a whole-file substring assertion satisfied by the Revision History row describing the very
  change being asserted, so both stating passages could be gutted green
- a ratio invariant to what it measures: neutering the corpus cache cost a ninefold read
  increase and moved the asserted number by nothing
- a floor tolerating the failure it was written to catch, so a lost marker was invisible
- a check written, shipped and unreachable behind an earlier branch

**The one Critical, found by the seat reviewing the machinery that enforces review.**
`critic.verdict_for` skipped any verdict row whose `superseded` flag was truthy, of any grade,
so an author could retire the REJECT blocking their own work with one hand-appended line naming
themselves as authoriser - and the close then reported the unit "covered by an independent
pass". `record_supersession` refuses to write that record and `_is_principal_superseded` exists
as the read-time backstop for the hand append; only the sign-off gate consulted it. Fixed in
BG0464: the grade of correction required now scales with the direction the mistake fails.

Five gates were repaired to check what they claim (BG0440, BG0456, BG0459 part, BG0464,
BG0465). The guards behind BG0457, BG0458 and BG0461 still over-claim in their own prose and
are carried with the claim uncorrected - which is why the goal verdict is partial.

**The delivered bugs got their own closing review** and it rejected two of thirteen. BG0442's
verifier accepted a hardcoded constant in the very function the bug was about - one fixture,
one single-value assertion, and the mutant survived all 623 tests of its module. BG0452's
sweep named `handoff.py` in its own Summary and its own Affects and never touched it. Both
repaired under BG0465; repairing the second showed why the original sweep had gone round it -
`extract_record_id` covers `ARTIFACT_TYPES` and only those, so `stem_record_id` now answers
for handoffs, retros and reviews.

## What the next session should know

- **`sprint close` reported `ok retro-validate: RETRO0086 valid` over a 100% unreplaced retro
  scaffold.** Three demonstration rows carried no marker and the close discards the validator's
  report on a zero exit. The markers are fixed; the discarded report is BG0459 and still open.
- **The gate budget is over and degrading** - 500-517s against a 380s ceiling, +59% since
  baseline, worse at the end of this sprint than at the start. BG0415, ruled accepted-risk.
- **A review worktree opens at a stale base.** Seven reviewers for seven hit it; they noticed
  only because `critic.py brief` refused an unknown id. One measured the suite red on a
  188-commit-stale tree and reported it; on main it is green (5587 pytest / 5586 unittest).
  CR0509.
- **A unit standing at Review is not nearly-done.** 101 points were planned as if the remaining
  work were a signature. The review established it was repair. That is the estimating lesson.
