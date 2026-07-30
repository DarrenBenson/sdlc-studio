# Latest review anchor

<!-- close-status:begin -->
> **RUN-01KYPZ1G closing.** 36 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Goal verdict:** partial (clause 1 achieved, clauses 2 and 3 fail)
> · **Delivered:** 37 units / 130 points of a 44-unit 158-point plan
> · **Dropped:** 11 units / 40 points, each with a recorded reason

## Landed since: EP0192 - the compulsory sprint checklist

Delivered outside a sprint, at the operator's direction. **Seven stories, 27 points, all at
Review** - Done needs the reviewer-of-record sign-off, and the author never records their own.

The checklist is rows of the EXISTING `sprint_report.py`, not a second document: one row per
stage of the cycle (pre-plan reconcile, goal seat review, grooming gate, run opening,
batch-boundary reviews, closing review, goal verdict, retro, lessons, sign-off, handoff) beside
the figures this file used to derive by hand (planned against delivered, dropped / held /
carried over with reasons, scope creep as a ratio, review attribution by seat and lens,
impediments, carried known issues, cost). `sprint close` gained a `checklist` chain step that
refuses on an unanswered item and names it; the waiver is `decisions.py waive --subject
rule:sprint-checklist:<item>`. Stop-ship rulings live in the retro's new `## Known issues
carried` table - the one row the tree cannot derive.

Three corrections the planning pass made to the request itself: `sprint_report.py` already
existed and the four original stories pointed at `retro.py` plus a template that does not
(building there was the two-document drift CR0505 was filed about); US0570's recording half
already shipped; and the set only asked close-time questions, so US0574-US0576 were added and
`cycle_drift()` now fails when a ceremony verb has no row.

Evidence: 22 ACs pass, 12/12 mutants killed, blast-radius suite green across 17 modules in
2m21s. Detail in the commit and in EP0192.

## The RUN-01KYPZ1G close - six stop-ships found, six fixed

Judged against the operator's standard: **an increment that adds value and makes nothing
worse.** The run ledger records 18 review rounds. `git log -S` sorted the twelve findings
from the last of them rather than judgement. Two were regressions
(BG0446, BG0451) and both are fixed; six were pre-existing and revealed rather than caused
(BG0443-BG0445, BG0448, BG0449, BG0452); the rest are new-but-better, BG0447 being a weak
guard where there was none.

| Fixed | What it was |
| --- | --- |
| BG0441 | `review_coverage` laundered a REJECT into coverage through the evidence lane, which carries no verdict column by design |
| BG0450 | The unresolved-questions gate had three live escapes and a tautological verifier; the mutant reducing it to a bare `Done` comparison survived all 5,489 tests |
| BG0453 | The same unguarded run-state read that consecutive earlier rounds each failed to close, still live in a further branch, discarding a completed verification |
| BG0446 | REGRESSION: `_is_superseded` closed the blockquoted case and left the fenced one, so a spec could drop itself as a version home, exit 0 |
| BG0451 | REGRESSION: `start_batch` minted a null-id run and the next `sprint plan` then destroyed the batch span |

**Coverage on the repaired gate is 0 of 37** - low because seven reviewers rejected, not
because reviews are missing. The ten units closed on 2026-07-30 under waivers D0077-D0086 were
all reported *covered* by the broken gate; the hand-recorded waivers are the only thing that
stopped it clearing them. Full detail, including the three false claims this file previously
carried, is in RETRO0085.

## Known divergences

- **The gate budget is OVER: 467s against 380s**, +47% since the 2026-07-26 baseline.
- **`tools/tests` is RED from any worktree** (BG0445): the census matches its skip list against
  the absolute path, so a checkout under `.claude/worktrees/` censuses zero files. Green in the
  main checkout, inert in the environment reviewers run in.
- **The seat ceremony was bypassed twice in one session** after CR0503 was filed about exactly
  that. Both attestations are on CR0503.
- **Scope: 48 unplanned artefacts against 44 planned units, a ratio of 1.09.** Derived by hand
  twice; EP0192 now reports it.

## Next steps

1. **Sign-off on the seven EP0192 stories is the operator's.** They hold at Review.
2. **BG0442 first in the next batch.** A goal metric that cannot be computed is worse than an
   absent one: it reports the good outcome.
3. **CR0507** (the close asks twenty questions where two would do) and **CR0508**
   (`verify_ac.selector_resolves` ships and no writer calls it) remain unrefined, as do CR0496
   and CR0497.
