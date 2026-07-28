# RV-0024: RUN-01KYMJEM - two independent adversarial passes, nineteen majors, and the two the sprint had already learned

> **Date:** 2026-07-28
> **Run:** RUN-01KYMJEM
> **Verdict:** REJECT (findings filed, not fixed - see Disposition)
> **Reviewers:** two independent contexts, neither of which wrote the code
> **Author:** Claude Opus 5

## What was reviewed

`git diff 59d7b5b8..HEAD` over the sprint's 34 units, split across two reviewers by subsystem
so neither could be primed by the other's findings:

- **Pass A** - the seam map, goal panel, clause splitting, sprint naming, blocker grouping,
  lane in-flight tracking (`refine.py`, `critic.py`, `lib/run_state.py`, `sprint.py`).
- **Pass B** - index-cell derivation, gate relevance, the filing paths (`reconcile.py`,
  `gate.py`, `.githooks/pre-commit`, `artifact.py`, `file_finding.py`).

Both were instructed to reproduce every finding before reporting it, and to state what they
probed if they found nothing. Both did.

## Verdict

**REJECT.** 19 majors and 17 minors, across code that ships and code that cannot be reached.
The shipped test suites pass in full, so not one of these was caught by them.

## The findings that matter most

**1. Data loss on tracked files, already in the installed copy.** `_INDEX_OWNED_COLUMNS`
listed the PLURAL projection columns and not the singular ones, so `Epic` and `Story` were
treated as file-owned scalars. Bugs carry `> **Epic:** --` as a placeholder, so the pass wrote
`--` over a populated cross-link and reported `index synced=True`. It reaches every caller of
`apply_type` - transition, file_finding, archive, project_upgrade, lite_profile, migrate_v3.
This repository escaped only because its bug index predates the shipped template.

REPAIRED AND RE-PORTED before anything else in the queue, with three defences rather than one,
and verified against the installed copy.

**2. Seven functions and two parameters that nothing calls.** `goal_clauses`, `sprint_name`,
`run_id_from_name`, `goal_panel`, `judge_defects_against_goal`, `record_content_review`,
`prediction_miss`; and no caller passes `record_goal_verdict(clauses=)` or
`record_review_round(seconds=)`. So `sprint_report`'s new exact-overhead branch can never fire
in production: the consumer was built and the producer was not.

The consequence for this run's own close is direct. The plan-time question was answered by the
PRE-EXISTING `goal-review record`, not by the content question US0545 specifies. The close-time
question was never asked, because no code path asks it. The per-clause verdict was assembled by
hand, which is why the panel's author-exclusion never fired on its author.

This is carried lesson 1 verbatim - *a mechanism that reaches no caller is inert, however well
it is tested* - printed in every lane brief of this sprint, in the plan digest and in the seat
brief. Filed as BG0385.

**3. Two defects the codebase had already solved.** The seam owner check matches by naive
substring, so `Preserves: tests/test_critic.py` owns the seam on `critic.py` -
`critic._verifier_names` documents and fixes that exact rule three files away, and the seam
block claims to be modelled on it. And `Preserves:` is honoured anywhere in the document while
its docstring says *in a criterion*; `critic.caller_declarations` walks the AC blocks.

**4. The defect-judging capability is blind to this repo's vocabulary.** `BLOCKING_PRIORITIES`
is `p0/p1/critical/blocker`; the corpus is High/Medium/Low - 104 High-severity bugs against 13
P1. Every High would be ruled leavable at a close.

## What the reviewers probed and found clean

`CALLER_INDETERMINATE`'s branch and its detail text; `record_lane_return`'s single-unit clear;
the `_mutate` lock over the new writes; `_carried_lessons_rel`'s derivation and the
LESSONS-TOP divergence it fixes; `round_duration` against negatives, string floats and missing
keys; `open_run` not leaking in-flight markers or content reviews across runs; the existing
round-count and reviewer-label guards; markdown-only seam exclusion; and the seam map finding
the real US0541/US0543 pair in this repository.

## Disposition

| Finding | Disposition |
| --- | --- |
| Index cross-link destruction | FIXED, tested, mutation-checked, re-ported |
| Status-column alias and unbounded field scrape | FIXED in the same commit |
| story+summary refused; string `acs` per character; batch atomicity | FIXED (regression cluster) |
| Twelve surviving majors | FILED: BG0387-BG0398, 30 points |
| Inert mechanisms | FILED: BG0385, 5 points |
| `caller-check --unit` single-valued | FILED: BG0386, 2 points |
| Seventeen minors | Recorded here; folded into the filed units where they share a fix |

Nothing was waived. Every surviving finding is an artefact with acceptance criteria, and the
run closes with them OPEN rather than with them argued away.

## The finding that outlives the batch

**A test written by the author of a fix asserts the shape of the fix, not the property it was
for.** Mutation found three survivors tonight and two were tests written hours earlier in this
sprint: the seam owner-check accepted any `Preserves:` line because every fixture happened to
name the shared file, and the carried-file test compared two constants that derive from each
other, so it passed whatever they said - including the wrong name they both had. A third
survived during the repair itself, when the relationship fix shadowed the placeholder guard.

The sprint set out to make a batch tell the truth about itself. The two most valuable things it
produced were an independent reading that found nineteen defects its own suites could not, and
an operator's question that found five units nothing could call.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Recorded: two independent passes, verdict REJECT, disposition per finding |
