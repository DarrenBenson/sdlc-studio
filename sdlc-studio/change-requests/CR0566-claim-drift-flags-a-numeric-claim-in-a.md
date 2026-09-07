# CR-0566: claim-drift flags a numeric claim in a diff's prose that no measurement backs

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Evidence:** RUN-01M1WPNV delivery, 2026-09-07: BG0646 (two REJECTs r1) and BG0649 (three REJECTs r1, two r2) - every rejection was a check a seat did in minutes that the author had not: run the shipped lane on this repository, measure a number written into prose, write a mutant for a branch the fixture never reached. Analysis recorded in the run's retro.
> **Date:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

'about 45 s' shipped into AGENTS.md from the gate's budget constant, '519 s' from a bug report's evidence line, and a criterion attributed a figure to a ledger row that holds a verdict and no number. Each was caught by a review seat measuring. The advisory claim-drift lane should flag a numeric claim (seconds, minutes, counts of modules or files) added to AGENTS.md, a fragment, a criterion or a reference doc when the same diff's revision rows and evidence files carry no command that produced it. Advisory while its yield is measured, the term the lane already ships under.

## Impact

A figure in consumer-facing prose carries a command behind it; a wrong cost or count stops shipping on the author's word and the review seat stops being the instrument.

## Acceptance Criteria

- [ ] Given a diff adding 'about four minutes' to AGENTS.md with no revision row naming the measuring command, when the claim-drift lane runs, then it reports the claim and the file; the same diff with the command in a revision row reports nothing - the control.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Raised |
