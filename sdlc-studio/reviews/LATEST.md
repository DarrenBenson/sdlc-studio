# Reviews - LATEST (anchor)

> Derived from **RUN-01KY5EJX** (2026-07-22). Supersedes the RUN-01KY3MFX picture.
> That run is CLOSED: 33 units, 100 points, goal verdict `partial`, RETRO0066 recorded,
> sign-off landed, `close_owed detect` reports none. The current run is a DESIGN rung,
> groomed and committed, with its closing review in flight.

## Where the pipeline is (2026-07-22)

**RUN-01KY5EJX is open at the design rung over 38 units / 108 points** - EP0106-EP0115 plus
six bugs. Its whole output is acceptance criteria; the delivery run follows.

Goal: *every story's acceptance criteria would fail if the behaviour were absent, every bug
states what makes its fix complete and tested, and any declared dependency records a logical
constraint the file census cannot already derive.*

The batch attacks the loop that cost the previous sprint ten review rounds: plan a repair
before executing it (EP0106), derive a claim about a guard from the guard (EP0107), brief the
reviewer with the practices that found defects (EP0108), inventory claims first not last
(EP0109), validate `Affects` at mint (EP0110), stop a second sprint fusing into an open run
(EP0111), check the CHANGELOG's structure (EP0112), carry a REJECT forward as filed findings
(EP0113), price the sprint not the build (EP0114), hunt work done before its contract
(EP0115).

## Evidence

3,947 skill tests and 312 tool tests green. Drift 0, validate 0 errors, engagement floor 0
violations. Red-now ledger over the batch: **pass=0, fail=89, manual=5** - no criterion is
vacuously green at a rung where the behaviour is absent. Two waves, five declared dependency
edges. `verify_ac lint` exits 0: no markdown-only verifier survives in the batch.

## What shipped as code

**BG0264** only. `verify_ac lint` REFUSES a `grep`/`file` verifier whose every target is
markdown, on a story at Draft or Ready; its fixture is the four verifiers US0310 actually
shipped, recovered from git. Five mutants applied, four killed. The fifth is equivalent, and
it falsified the docstring beside it - a decision justified by a scenario `_expand_globs`
rules out. No mutation-coverage claim is made for that line.

## The first plan review, and what it cost

The Sprint Goal was REJECTED by the engineering seat before any work started: it asserted
acceptance criteria for six bugs that carry none, its dependency clause was information-free
because the shared-file clusters are already derived from `Affects`, and its bar was
satisfiable by 32 trivially-true verifiers. Reframed, it was accepted. Two seats
independently reached the same objection - a counterfactual bar is a belief, not a check -
and both noted the red run is free at a rung where the behaviour is genuinely absent.

Filed from the ceremony itself: **BG0262** (a seat saying NOT achievable discharges the gate
exactly as one saying yes - `achievable` is never parsed), **BG0263** (no rounds, so
rewriting a rejected goal erases the rejection), **CR0408** (acting on the review invalidates
every verdict including the proposing seat's, so the cheapest path is to leave a bad goal
alone), **CR0409** (the seat brief is assembled by the author the review exists to check).

## Known holes, recorded not hidden

- **D0056:** the goal sets dependency QUALITY, not coverage. Declaring nothing would satisfy
  it. Shared-file warnings therefore remain in the plan and are expected.
- **BG0265:** `parse_story` keeps only the FIRST `Verify:` line per AC block, so seven
  verifiers in this workspace have never run - four on Done stories, two of them inside
  RUN-01KY3MFX's published claim of 84 criteria verified.
- **BG0256:** nothing re-runs a bug's verifier; `walk_stories` yields only `US` records, so a
  bug's `Verified:` stamp is a dated record, not a live guarantee.
- The kill list carried by the grooming commit: US0323's untestable future writer, US0324's
  ordering claim, US0316's polarity scan, US0341/US0342's manual lens checks, US0331's
  staged-diff bound, and CR0403's "drawn from real failures" - the weakest leg in the batch,
  with no criterion anywhere holding it.

## Next steps

- The closing adversarial review of the design rung is in flight. Its verdict decides whether
  this run closes or repairs.
- Then the DELIVERY run over the same 38 units, against the goal recorded for it.
- **CR0319** is the 5.0.0 release cut, still outstanding.

## Lessons

A repair can mask the defect beside it. Prose that justifies code is the least-reviewed code
in the repo. A counterfactual bar needs a ledger beside it. The data to detect a defect is
usually already present and unread.
