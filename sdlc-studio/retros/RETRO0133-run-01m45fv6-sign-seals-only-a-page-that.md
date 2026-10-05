# RETRO-0133: RUN-01M45FV6: sign seals only a page that still checks

> **Date:** 2026-10-05
> **Run:** RUN-01M45FV6
> **Batch:** BG0940, BG0943

## Keep

- Reviewing the goal before writing the plan. QA judged it partial because 'every shipped
  default' outran a criterion naming three keys, and product found a clause of BG0940's fix with
  no criterion; both bugs were re-groomed (D0344) and the build met the stronger criteria.
- Letting the build execute the premise rather than trust the bug's diagnosis. BG0943's cause
  was a comment-only section merged as null, not the list the bug named, and the test now runs
  every shipped key through show in three projects.
- One QA reviewer per unit (D0341): both units approved in their first round.

## Stop

- [LC-004] Reading a premise as executed from a probe that could not tell the hypotheses
  apart: I took config.get's correct-looking values as proof it read the keys, but each
  fallback equals its default, so the probe returned the same either way. D0344 carried the
  wrong claim until the build corrected it.
- [LC-018] Writing a changelog sentence from the unit test rather than the CLI path: BG0940's
  fragment says the page is signed after a late ruling, but sign refuses the changed tree until
  a re-close (BG0945).

## Try

- Probe a premise with an input whose result differs under each hypothesis, such as a key whose
  code fallback differs from its shipped default.
- Run each user-facing sentence in a changelog fragment through the CLI before asking for
  review, as the paperwork reviews already do.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG0944 | not-stop-ship | orchestrator | 2026-10-05 |
| BG0945 | not-stop-ship | orchestrator | 2026-10-05 |
