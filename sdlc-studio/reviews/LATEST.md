# Latest review anchor

<!-- close-status:begin -->
> **RUN-01KYMJEM closed stopped.** 34 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Review record:** RV0024 (2026-07-28) - two independent adversarial passes, nineteen majors
> **Retro:** RETRO0082 · **Goal verdict:** partial (per clause) · **Outcome:** closing with known issues

## Where the pipeline is

RUN-01KYMJEM delivered all 34 units of its batch: 15 bugs Fixed, 19 stories at Review, 112 of
112 points, across eight commits every one of which passed the full gate. The batch is the
machinery the RUN-01KYKVZM review said was missing, plus the defects that review found.

**Sign-off owed.** The 19 stories stand at Review pending an adversarial pass by a context that
did not write them and the operator's sign-off as reviewer of record. The author does not record
either; the two-role rule holds.

## What RUN-01KYMJEM changed

- **EP0184** - a seam between two units has an owner before the work starts. `refine seams` maps
  the pairs of a batch sharing a declared file, a `Preserves:` criterion owns one, the map reaches
  every lane brief, and the close names any seam that shipped unowned.
- **EP0185/EP0186/EP0187/EP0188** - a Sprint Goal is recorded as clauses and judged clause by
  clause by a panel that refuses the author; an open defect is judged against those clauses rather
  than a guessed severity; the goal review is a bookend asked at plan and at close with the
  shortfall supplied; a sprint carries its goal in its name; the bounded exit files one artefact
  per cause rather than one per unit.
- **EP0182/EP0183** - a review round records how long it took, so the overhead ratio stops
  crediting unattributed time to delivery; one changelog rule that parallel lanes can obey.
- **Fifteen bugs**, eight of them found and filed DURING the sprint by using the tools it built.

## What the new instruments measured about runs that had already closed clean

- **RUN-01KYKVZM: 52 seams, none owned.**
- **RUN-01KYJZGZ: 24 of 33 units** reached terminal carrying a declared proof obligation nobody
  discharged - both suites green, gate passed, close clean.
- **The carried-lessons writer read ZERO lessons** out of the file the lane briefs read five from.
- **109 stale index cells** while `reconcile detect` reported `drift_items=0`. `status.py` reads
  the index, so every backlog figure quoted that day came from an unchecked source.

## Known divergences

**This run's own seam coverage is 107 seams, none owned.** The map was built during the sprint and
so was not available when the batch was planned; the units are heavily concentrated in `sprint.py`
by design (the planner withheld parallel delivery for exactly that reason). It is reported here
rather than omitted, because a batch that ships with unowned seams is not the same as one whose
pairs were accounted for.

**Clause 2 cannot be closed by this run.** The qa seat said so at plan time: US0542 asserts a
panel excludes the author, and this sprint's plan-time seat review was written by the author of
the plan. A capability cannot be dogfooded by the run that builds it. The first genuinely
independent panel is the next sprint's.

## The finding that outlives the batch

Mutation testing produced three survivors, and two were tests written in this sprint to check its
own fixes: the seam owner-check accepted any `Preserves:` line because every fixture happened to
name the shared file, and the carried-file test compared two constants that derive from each other,
so it passed whatever they said - including the wrong name they both had. A test written by the
author of the fix tends to assert the shape of the fix rather than the property it was for.

## The review

Two independent contexts reviewed the diff, neither of which wrote it. **REJECT** - 19 majors
and 17 minors, none of them caught by the shipped suites (RV0024).

Repaired before the close: index cross-link DESTRUCTION (data loss, reaching every caller of
`apply_type`, already mirrored to the installed copy - fixed, tested, re-ported and verified);
the status-alias and body-scrape defects beside it; and three regressions into paths that
worked this morning.

Filed OPEN, 37 points across BG0385-BG0398: seven unreachable mechanisms, a severity floor
blind to this repo's own priority vocabulary, two defects the codebase had already solved
three files away, and nine guards narrower than they claim. **Nothing waived.**

## Next steps

1. BG0385-BG0398 at the front of the next batch. BG0386 first - `caller-check --unit` is
   single-valued, so a batch check silently answers about one unit, and it has already
   produced one false measurement in this repository.
2. The first genuinely independent goal panel is the next sprint's. Both the qa seat at plan
   time and the review at close say so, for different reasons that both hold.
3. **CR0498 - the close ceremony costs more than the work it certifies.** Measured on this
   run: ~32 minutes of gate across 5 commits, 57 process spawns to record three facts about 19
   units (38 of them wasted on one argument error), and 3 close attempts of which 2 stopped on
   a refusal. Four remedies, largest first: a `close --dry-run` reporting every refusal in one
   pass, batch forms on the critic verbs, a retro scaffold that passes its own validator, and a
   close-scoped gate profile.
4. The gate budget lane went OVER during this close - 427s against a 380s ceiling, +35% on the
   2026-07-26 baseline. It has stopped being advisory noise and is now a true reading.
