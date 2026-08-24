# CR-0549: route.estimate scores whole declared files, so the risk band that drives review ceremony is a constant in any repo with large modules

> **Status:** Superseded
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

## Second correction, 2026-08-24: the consumer list was short, and it settles the design

The correction above named two consumers. There are FOUR, found by grep rather than by memory,
and the split between them is the design this request needs before it can be planned:

| Caller | Site | When it runs |
| --- | --- | --- |
| `sprint.py` | 1094, the planner banding a batch | BEFORE the unit is implemented |
| `plan_review.py` | 106, `_difficulty_band` for the pre-code gate | BEFORE, by definition |
| `handoff.py` | 308, the suitability seed | BEFORE |
| `critic.py` | 2666, choosing the review TIER via `_difficulty_band` | AFTER, for a delivery brief |

So THREE of the four ask the question before a diff can exist, and one asks it after. A single
diff-scoped estimator does not serve both: at the three pre-code sites it would resolve to
nothing, and the fail-towards-deeper-review rule would then band every unit `full` - the constant
this request exists to remove, arrived at by a different route.

**The estimator therefore answers two questions and must say which it answered.** A DECLARED
basis, from the unit's `Affects` and its stated size, is what a planner and a pre-code gate can
have; a DIFF basis, from the hunks against the run's base ref, is what a delivery brief can have.
Both are legitimate; conflating them is what makes the band uninterpretable. `route.estimate`
gains an explicit basis in its returned dict, each caller asks for the basis it can actually
support, and a caller that asks for `diff` where none resolves is REFUSED rather than silently
degraded - because a silent degradation to `full` is indistinguishable from the defect.

This also disposes of the re-measurement contradiction the first correction found. A distribution
over 603 closed bugs has no per-unit diff, so it can only be measured on the DECLARED basis, which
is what the estimator already does - re-measuring it proves nothing about the change. The claim
worth making is about the DIFF basis, and the only honest corpus for it is a synthetic one: known-
small and known-large changes against the same files, where the expected bands are known in
advance and a failure to discriminate is visible.

## Third correction, 2026-08-24: the remedy, settled by measurement

A pre-code goal review REJECTED the first re-groom, and it did so with a number rather than an
opinion: scored over all 610 bugs, that design moved the band at ONE of four consumers -
`medium`-or-above 87% to 85%, interquartile spread unchanged at six points, a uniform downward
translation. The reason is structural. Three of the four consumers take a DECLARED basis, and the
declared basis as specified was byte-for-byte today's algorithm - `complexity.assess` over whole
files. Naming the basis without changing what the declared basis READS moves the problem.

**So the declared basis stops reading whole-file complexity and reads what the unit itself
declares.** Measured over the same corpus, a band led by `Points` with `Affects` breadth as its
second term:

| Band | Today | Points-led |
| --- | --- | --- |
| `light` | 13% | 33.4% |
| `medium` | - | 46.3% |
| `full` | 87% | 20.3% |

And it DISCRIMINATES on a property whole-file complexity cannot see, because `Points` is a claim
about the CHANGE rather than about the file: one point in one file bands `light`, three points in
one file bands `medium`, eight points across four files bands `full` - the same file, three
answers. That is CR0510's ask, and it is the half this request was filed to finish.

**Why `Points` is available exactly when it is needed.** 467 of 610 historical bugs carry it, but
the figure that matters is not that one: `sprint plan` REFUSES a batch holding a unit with no
`Points` or no `Affects`, so at the moment the planner, the pre-code gate and the suitability seed
read the band, both terms are present by construction. A signal the tooling already demands is
strictly better than one it has to infer.

**What the DIFF basis can and cannot be.** `risk` is `composite_risk(cognitive, churn)` and churn
counts commits touching a FILE - a two-line change and a rewrite of the same module have identical
churn. `risk` therefore has no per-hunk meaning and must stay file-level and be stated as such; only
`code` becomes hunk-scoped. A criterion demanding both from hunks is unsatisfiable, and the first
re-groom carried one.

**The consumer list is seven, not four.** `sprint.py:1094`, `plan_review.py:106` and `:110`,
`handoff.py:308`, `critic.py:2666` (via `plan_review._difficulty_band`), `project_upgrade.py:706`
(the `migrate --apply` backfill, exercised by the release-boundary rehearsal) and `route.pick`
at `route.py:229`, plus the shipped `cmd_estimate` CLI. A basis parameter with no default breaks
all of them; `_difficulty_band` also swallows a bare `Exception`, so a refusal degrades silently at
every existing site unless that is changed too.

## Fourth correction, 2026-08-24: the remedy is WITHDRAWN and replaced by CR0555

A third specification was rejected, and this time the finding was not about cutpoints. The
measurement justifying the Points-led band was taken against a throwaway script; `route.estimate`
computes five weighted subscores into a 0-100 score and bands it at 20/40/60/80. Run through the
pipeline that actually ships, three literal readings of the criterion land at 81%, 92% and 97%
`light` - the mirror image of this request's own defect, in the direction that ships defects.

Two further things this record should carry, because both were errors of mine rather than of the
reviewer. The published table compared two different definitions of `full`: the 87% baseline is
`medium`-or-above under `critic.BAND_TIER`, and the model's own script printed the honest
figure - ceremony 87% to 66.6% - while the flattering 20.3% went into the correction. And the
Points-led band is threshold tuning on a different field, which this request's Summary rejects
in terms: "any cutpoint chosen there is tuning noise rather than measuring risk."

**D0150 then settled it as a class**: no author-declared field may gate review depth, and `Points`
is author-declared. That rules out the whole family of pre-code remedies, because everything
available before a unit is implemented is a declaration by its author.

**The diagnosis stands and the remedy moves to CR0555.** The gate does not need a better pre-code
band - it needs to fire where a diff exists. `critic.tier_for` already reads a post-code band
successfully for exactly that reason. What survives from this request is the `scope` convention fix
(US0679) and the diff basis for the one consumer that runs after code, and both should be re-cut
against CR0555 rather than salvaged from a batch three reviews have rejected.

## Acceptance Criteria

- [ ] The DECLARED basis - the one three of the four pre-code consumers read - is computed from the unit's own `Points` and `Affects` breadth, not from a complexity read over whole declared files
- [ ] The same production file, changed at one point and at eight, produces DIFFERENT bands, which whole-file complexity cannot do because it never sees the change
- [ ] The DIFF basis scopes `code` to the hunks a unit changes against the run's base ref; `risk` stays file-level and SAYS SO, because churn counts commits touching a file and has no per-hunk meaning
- [ ] `route.estimate` names the basis it used - `declared` or `diff` - so a band can be interpreted, and a `diff` request that does not resolve is REFUSED rather than degraded to a whole-file score
- [ ] Every existing caller keeps working: the three pre-code consumers ask for `declared`, `critic`'s tier asks for `diff`, and `project_upgrade`, `route.pick` and the `estimate` CLI are migrated rather than broken
- [ ] `scope` stops counting a test file present only because the repository's convention requires it beside its production file, while a unit whose SUBJECT is a test file still counts it
- [ ] The band distribution is re-measured on BOTH bases and both are recorded here beside the pre-change figures, with the basis named against each

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Raised |
| 2026-08-21 | sdlc-studio | Goal review CORRECTION: the two principal consumers (`plan_review._difficulty_band`, the planner's banding) run before a diff exists and were unnamed; `base_ref` is per-run so a corpus re-measurement has no diff for closed units; two derived criteria contradicted each other on whether the spread widens or narrows. Needs re-grooming before it can be planned |
| 2026-08-24 | sdlc-studio | Second and third corrections: the consumer list is seven, not two; the estimator answers two questions and names which; and the DECLARED basis is re-specified onto `Points` and `Affects` breadth after a goal review measured the first re-groom moving the band at one of four consumers. Acceptance criteria rewritten to the settled design - the previous set encoded the superseded one and `critic.py brief` serves them as law. |
| 2026-08-24 | sdlc-studio | Fourth correction: remedy WITHDRAWN after a third rejection, superseded by CR0555. D0150 rules out the whole pre-code family. Diagnosis stands. |
