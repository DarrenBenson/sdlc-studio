# RV-0015: Design-rung closing review: three rounds, three rejections, one class

> **Date:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

RUN-01KY5EJX, the design rung over 40 units / 111 points (US0311-US0342, BG0256-BG0261,
BG0264, BG0265). Three independent adversarial rounds, each a fresh context that did not
author the work. Diff bases 5d0cf86, 44cb915, 0c02185.

## Findings

Every round's MAJOR was the same class: a rule RESTATED beside the thing it describes rather
than DERIVED from it. Four versions of one guard, each defeated by an expression the runner
reads differently from the way the guard read it - the target tokens as written, an invented
flag-aware split, an assertion about grep that is false of this DSL, and a directory walk that
saw files the runner refuses to read. The batch under review contains CR0394, which exists to
abolish exactly this, and the defect was committed inside the repair for it three times.

What the author got wrong, recorded rather than smoothed:

- Normalising 21 bug verifiers to a prose prefix made every one unparseable, and the commit
  asserted they passed.
- A surviving mutant was declared EQUIVALENT without proof. It was not.
- A flag form was argued to fail loudly. Measured: it exits zero and passes silently.
- Directory fixtures were all flat, so a verdict-flipping mutant survived on cases where the
  mutant and the original agree by construction.

What worked: round 1's repair was written as a PLAN and attacked before any code changed. The
plan was REFUTED in full - it closed none of the three escapes - and the attacker found two
more the review had missed. EP0106, which makes that a gate, is in this batch and unbuilt.

Evidence: 3,960 skill tests, 312 tool tests, drift 0, validate 0 errors, floor 0 violations.
Red-now ledger: 94 criteria, pass=0, fail=91, manual=3.

## Verdict

| Round | Verdict | Findings |
| --- | --- | --- |
| 1 | REJECT | 4 MAJOR, 3 MINOR |
| 2 | REJECT | 3 MAJOR, 2 MINOR; per-item on round 1: 3 CLOSED, 1 OVER-CLAIMED, 3 MOVED |
| 3 | REJECT | 1 MAJOR, 3 MINOR; per-item on round 2: 5 CLOSED, 1 OVER-CLAIMED |

`review.max_rounds` is 3. The ceiling is spent and **round 3's repair carries no independent
review**. Findings not repaired are filed: BG0266, and the residuals disclosed on BG0264. The
sign-off is the reviewer of record's and is owed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
