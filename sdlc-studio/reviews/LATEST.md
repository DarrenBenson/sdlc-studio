# Reviews - LATEST (anchor)

> **RUN-01KY5Y3W is the live delivery run** over the 43 units the design rung
> (RUN-01KY5EJX, closed partial, RETRO0067) groomed. Building in waves; not yet closed.

## Where the pipeline is (2026-07-23)

**26 of 43 units delivered to full fidelity** - code, node-addressed tests, and a
per-guard mutation pass - and pushed. The remaining 17 are the sprint/critic/artefact
coupled core, in flight as three file-disjoint parallel clusters.

Goal: *all 43 units reach Review with every acceptance criterion proven by a test that
fails without the code it guards, and every guard this batch ships is ENABLED in this
project's own config - so nothing here can be delivered inert.*

## What has shipped

- **Instrumentation first (BG0265, BG0256):** a stacked `Verify:` line is refused rather
  than silently dropped; a stamped-green AC whose selector selects nothing reads STALE, by
  collection not execution. Until these landed the run could not trust its own pass count.
- **EP0106, the repair-plan gate** - the flagship. A REJECT yields a written plan (one entry
  per finding: change, approach, risk), reviewed by an independent pass before any code,
  pinned to the findings; a repeat-class repair must change the design past a threshold.
  Opt-in, off by default. 21 tests, 11 mutants.
- **EP0113, carry-forward** - a project may declare `review.policy: carry-forward`; a REJECT
  then ships with its findings filed or waived, never by narrative downgrade.
- **Six clusters via parallel worktrees** - EP0107 (derive a guard's message), EP0112
  (CHANGELOG structure), EP0115 (process audit lens), BG0258, BG0259, BG0260, BG0261.

## What the fan-out taught, filed as CR0411

The parallel delivery worked, and it exposed two real interactions, both fixed and one
filed as an operator-requested feature: `.claude/worktrees/` was linted as shipped payload
and swept as a scrub site (now excluded, gitignored); and one merge conflict came from a
clustering that excluded TEST files from coupling. CR0411 asks that `sprint plan` offer
sequential-or-parallel delivery at run start, only when a real file-disjoint decomposition
exists, and count test files as coupling.

## Evidence

4043 skill tests + 312 tool tests green on the last integrated tree. Drift 0, floor 0,
gate green on every commit. Every delivered guard mutation-proven; equivalent survivors
recorded with their reason, never hidden.

## Next steps

- The three in-flight clusters (EP0108+EP0109 critic; EP0111+EP0114 sprint; EP0110 artefact)
  merge, then the batch's own closing review - in waves, per the plan's own guidance, never a
  single review over the whole diff.
- Transition the delivered units to Review, then the reviewer-of-record sign-off.
- **CR0319** is the 5.0.0 release cut, held until the backlog is clear (D0057).

## Lessons

Derive the whole behaviour, not the half you were looking at. A counterfactual bar needs a
ledger beside it. Plan the repair, attack the plan, then execute. Count test files as
coupling before fanning out.
