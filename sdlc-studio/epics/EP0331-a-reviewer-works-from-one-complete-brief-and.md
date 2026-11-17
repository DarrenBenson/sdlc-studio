# EP0331: A reviewer works from one complete brief and no longer re-fetches what the brief could carry

> **Status:** Draft
> **Derived Point Total:** 19
> **Parent:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0679. Delivers the work CR0679 requested.

## Story Breakdown

- [ ] [US1211: The capped unit diff puts claim surfaces first and the full diff is written beside the brief](../stories/US1211-the-capped-unit-diff-puts-claim-surfaces-first.md)
- [ ] [US1212: Critic brief writes the brief to a named path and prints one line, and the dispatch says to read it whole](../stories/US1212-critic-brief-writes-the-brief-to-a-named.md)
- [ ] [US1213: The brief carries the red lines of the verifier dry run and the selected tests, stamped with its HEAD](../stories/US1213-the-brief-carries-the-red-lines-of-the.md)
- [ ] [US1214: A verify stamp records the Affects digest, and a transition accepts a current stamp without a re-run](../stories/US1214-a-verify-stamp-records-the-affects-digest-and.md)
- [ ] [US1215: A rejoinder brief diffs from the round one verdict's commit and leaves out the file history](../stories/US1215-a-rejoinder-brief-diffs-from-the-round-one.md)
- [ ] [US1216: Each recorded verdict says whether it cites the file history](../stories/US1216-each-recorded-verdict-says-whether-it-cites-the.md)

## Acceptance Criteria (Epic Level)

- [ ] The capped UNIT DIFF sorts by surface (artefact, changelog.d, docs, production, tests) before the cap, the uncapped diff is written to <brief>.diff and named in the remainder line, and the scope line says the UNIT DIFF is base..HEAD for those paths; a test pins that a cut keeps the artefact and drops tests first.
- [ ] `critic.py brief --out <path>` writes the brief and prints one line (path, tokens, tier, fingerprint), and the shipped review dispatch says to read it whole in one call.
- [ ] The brief runs `verify_ac --dry-run` and the gate's test selection for the Affects and prints a RESULTS section stamped with the HEAD it ran at, red lines only; `verify_ac.py run` records the Affects digest with its stamp, transition.py and a light-tier brief accept a stamp at the current digest without re-running, and a mismatch re-runs.
- [ ] `critic.py brief --rejoinder` takes the round-1 verdict's commit from the ledger as the UNIT DIFF base, omits FILE HISTORY, keeps the per-item repair verdict, the verify command and the criteria at the round-1 tier (BG0975), and a test pins that a rejoinder's diff excludes hunks present at the round-1 commit.
- [ ] Each verdict records whether it cites FILE HISTORY, and before and after: reviewer calls per unit-review on the next sprint fall from run six's 30 (547 over 18) to at most 26.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
