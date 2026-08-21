# CR-0549: route.estimate scores whole declared files, so the risk band that drives review ceremony is a constant in any repo with large modules

> **Status:** In Progress
> **Decomposed-into:** EP0217
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/complexity.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, .claude/skills/sdlc-studio/scripts/tests/test_complexity.py
> **Date:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The ceremony-proportional-to-blast-radius gate CR0510 asked for is built and cannot fire here, because the risk band it reads is derived from FILE size rather than CHANGE size. `route.estimate` takes 0.40 of its weight from `code` and `risk`, both of which come from `complexity.assess`, which scores every function in every file named in `Affects` and takes the maximum. A two-line change to `sprint.py` therefore inherits `sprint.py`'s worst function and scores identically to a rewrite of it. A further 0.20 comes from `scope`, a count of declared files, which this project's own convention inflates by requiring the test file in `Affects`. So 60% of a unit's score is a statement about the files it names rather than about the change it makes.

Measured over the whole bug corpus, 603 units: 525 (87%) tier `full`, 78 (13%) `light`; `code` AND `risk` both saturated at 1.0 for 290 (48%); of the 400 units touching `scripts/`, 372 (93%) band medium or above. The score spread is min 13, p25 48, median 50, p75 54, max 75 - half the corpus inside six points. A gate whose input has that little dynamic range is a constant wearing the appearance of a gate, which is the exact phrase CR0510 used about the state it was written to fix.

CR0510 scoped the REVIEWER to the changed hunks and left the ESTIMATOR reading whole files. This is the unfinished half.

Threshold tuning is not a substitute and should not be adopted as one: modelled against the same corpus, `routing.thresholds.small` at 40 gives 13% light, 48 gives 22%, 50 gives 29%, 52 gives 54%, 55 gives 76%. The 50-to-52 step flips a quarter of the corpus, so any cutpoint chosen there is tuning noise rather than measuring risk.

## Impact

Every project using the skill, and this one first. The consequence is measurable on the run that raised it: RUN-01M0CT8P delivered 21 points for 11,034,109 main-thread tokens - 525,434 per point, against a plan forecast of 44,427 and a corpus history whose worst prior row is 353,810. Ten independent review rounds for six units. Five of the six banded medium or high and drew the deepest review; the one that banded low did so because it touches `.githooks/commit-msg` and `tools/`, which are small files, not because the change was safer.

What breaks if nothing changes: the tier gate stays decorative, ceremony stays uniform, and the only remaining levers are hand-tuned config cutpoints that nobody can defend with a measurement. What breaks if this is done carelessly: a diff-scoped estimate that reads only added lines will band a one-line change to a load-bearing branch as trivial, so the change's own complexity must be read in the context of the function it lands in, not in isolation.

## Correction from an independent goal review, 2026-08-21

Three defects in this request as filed, found by a goal review before any code was written, and
recorded here rather than quietly edited out.

**The consumers are not named, and they are the problem.** `route.estimate(repo_root, unit_path)`
takes no base ref, and its two principal callers run BEFORE a diff exists:
`plan_review._difficulty_band`, which decides whether a unit needs a pre-code plan review at all,
and `sprint.py` at the point the planner bands a batch. A diff-scoped estimate at those two sites
does not become accurate - it becomes UNRESOLVABLE, so this request as filed would replace a
constant `full` band with a constant `missing` one at exactly the moment the band is used. Neither
file appears in the `Affects` of any story decomposed from this CR.

**`base_ref` is per-RUN, not per-unit.** `lib/run_state.base_ref` records where the open run
started. It says nothing about where any individual historical unit's change began, so the
corpus-wide re-measurement this request asks for has no diff to read for 603 bugs that are already
closed. Two criteria written from this CR then contradicted each other: one sent every unresolvable
unit to `full`, which makes the distribution NARROWER, while the other asserted the spread widens.

**What "re-measure the corpus" can honestly mean** must therefore be settled before this is planned.
A distribution over units whose diffs no longer resolve measures the degradation path, not the
estimator. The candidates are a re-measurement over units delivered AFTER the change with their own
diffs available, or a synthetic corpus of known-small and known-large changes against the same
files - and either is a different claim from the one filed.

None of this weakens the diagnosis. The measurement behind this CR stands: 87% of 603 bugs tier
`full`, `code` and `risk` both saturated for 48%, and half the corpus inside a six-point spread.
It is the REMEDY that was under-specified, and a request that cannot say where its own output is
consumed is not ready to be built.

## Acceptance Criteria

- [ ] The `code` and `risk` subscores are computed from the hunks a unit changes against the run's base ref, not from every function in every declared file, and a unit with no diff yet degrades to the missing-signal path rather than to a whole-file score
- [ ] A two-line change to a large module and a rewrite of that module produce DIFFERENT bands, demonstrated by scoring both against the same file
- [ ] `scope` stops counting a test file that is present only because the project convention requires it in `Affects`, or the convention's contribution is stated and weighted separately
- [ ] The band distribution over this repository's bug corpus is re-measured after the change and recorded in the CR, so the claim that the gate now discriminates rests on a number rather than on the design
- [ ] A unit whose diff cannot be resolved bands FULL and says why, preserving the existing fail-towards-deeper-review rule
- [ ] `route.estimate`'s returned dict names which basis it used - diff or whole-file - so a reader can tell a measured band from a degraded one

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Raised |
| 2026-08-21 | sdlc-studio | Goal review CORRECTION: the two principal consumers (`plan_review._difficulty_band`, the planner's banding) run before a diff exists and were unnamed; `base_ref` is per-run so a corpus re-measurement has no diff for closed units; two derived criteria contradicted each other on whether the spread widens or narrows. Needs re-grooming before it can be planned |
